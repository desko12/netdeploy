#!/usr/bin/env python3
import json
import subprocess
import os
import sys
from xml.etree import ElementTree as ET
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
import yaml

WORK_DIR = '/tmp/netdeploy'
os.makedirs(WORK_DIR, exist_ok=True)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads"""

HTML = open('index.html').read()

def parse_xml(xml_string):
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError:
        root = ET.fromstring(f"<root>{xml_string}</root>")
    
    configs = []
    config_elements = root.findall('.//config')
    
    if not config_elements:
        config_elements = [root] if root.tag == 'config' else []
    
    if not config_elements:
        return configs
    
    for config_el in config_elements:
        config = {
            'target': config_el.get('target'),
            'host': config_el.get('host'),
            'os': config_el.get('os'),
            'user': config_el.get('user'),
            'password': config_el.get('password'),
            'elements': []
        }
        
        supported = ['interface', 'vlan', 'bgp', 'ospf', 'network']
        
        for elem in config_el:
            if elem.tag not in supported:
                continue
                
            element = {'type': elem.tag, 'attrs': dict(elem.attrib), 'children': []}
            
            for child in elem:
                if child.tag == 'neighbor':
                    neighbor = {'ip': child.get('ip'), 'remote-as': child.get('remote-as')}
                    desc = child.find('description')
                    if desc is not None:
                        neighbor['description'] = desc.text
                    element.setdefault('neighbors', []).append(neighbor)
                else:
                    element['children'].append({'tag': child.tag, 'text': child.text})
            
            config['elements'].append(element)
        
        configs.append(config)
    
    return configs

def generate_inventory(configs):
    inventory = {'all': {'children': {}}}
    
    for config in configs:
        os_name = config['os']
        if os_name not in inventory['all']['children']:
            inventory['all']['children'][os_name] = {'hosts': {}}
        
        # SSH options to handle older Cisco IOS devices
        inventory['all']['children'][os_name]['hosts'][config['target']] = {
            'ansible_host': config['host'],
            'ansible_user': config['user'],
            'ansible_password': config['password'],
            'ansible_connection': 'network_cli',
            'ansible_network_os': os_name,
            'ansible_ssh_common_args': '-o KexAlgorithms=+diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1 -o HostKeyAlgorithms=+ssh-rsa -o StrictHostKeyChecking=no',
            'ansible_ssh_pass': config['password'],
        }
    
    return json.dumps(inventory, indent=2)

def generate_playbook(configs):
    tasks = []
    
    for config in configs:
        for elem in config['elements']:
            task = {'name': f"{config['target']}: {elem['type']}"}
            
            if elem['type'] == 'interface':
                name = elem['attrs'].get('name')
                state = next((c['text'] for c in elem['children'] if c['tag'] == 'state'), 'present')
                ip_elem = next((c['text'] for c in elem['children'] if c['tag'] == 'ip'), None)
                
                if config['os'] == 'eos':
                    playbook = {'eos_interfaces': {'config': [{'name': name, 'enabled': state == 'present'}], 'state': state}}
                    if ip_elem:
                        ip, prefix = ip_elem.split('/')
                        playbook['eos_interfaces']['config'][0]['ipv4_address'] = ip
                        playbook['eos_interfaces']['config'][0]['ipv4_prefix_length'] = int(prefix)
                    task.update(playbook)
                elif config['os'] == 'nxos':
                    task['nxos_interfaces'] = {'config': [{'name': name, 'enabled': state == 'present'}], 'state': state}
                elif config['os'] == 'ios':
                    task['ios_l2_interfaces'] = {'config': [{'name': name, 'mode': 'access'}], 'state': state}
            
            elif elem['type'] == 'vlan':
                vlan_id = int(elem['attrs'].get('id'))
                vlan_name = next((c['text'] for c in elem['children'] if c['tag'] == 'name'), '')
                xml_state = next((c['text'] for c in elem['children'] if c['tag'] == 'state'), 'present')
                
                # Map state for different OS
                state_map = {
                    'eos': 'present',
                    'nxos': 'present',
                    'ios': 'merged'  # Cisco IOS uses merged/replaced/deleted
                }
                state = state_map.get(config['os'], 'present')
                
                if config['os'] == 'eos':
                    task['eos_vlans'] = {'config': [{'vlan_id': vlan_id, 'name': vlan_name}], 'state': state}
                elif config['os'] == 'nxos':
                    task['nxos_vlans'] = {'config': [{'vlan_id': vlan_id, 'name': vlan_name}], 'state': state}
                elif config['os'] == 'ios':
                    task['ios_vlans'] = {'config': [{'vlan_id': vlan_id, 'name': vlan_name}], 'state': state}
            
            elif elem['type'] == 'bgp':
                asn = int(elem['attrs'].get('as'))
                neighbors = elem.get('neighbors', [])
                
                if config['os'] == 'eos':
                    task['eos_bgp'] = {
                        'config': [{'as_number': asn, 'neighbors': [
                            {'neighbor_address': n['ip'], 'remote_as': int(n.get('remote-as', 0)), 'description': n.get('description', '')}
                            for n in neighbors
                        ]}],
                        'state': 'present'
                    }
                elif config['os'] == 'nxos':
                    task['nxos_bgp'] = {
                        'config': [{'as_number': asn, 'neighbor': [
                            {'neighbor': n['ip'], 'remote_as': n.get('remote-as', 0), 'description': n.get('description', '')}
                            for n in neighbors
                        ]}],
                        'state': 'present'
                    }
            
            if len(task) >= 2:
                tasks.append(task)
    
    return yaml.dump([{'name': 'Network Configuration Deployment', 'hosts': 'all', 'gather_facts': False, 'tasks': tasks}], default_flow_style=False, sort_keys=False)

def run_ansible_playbook(inventory_content, playbook_content):
    try:
        with open(f'{WORK_DIR}/inventory.json', 'w') as f:
            f.write(inventory_content)
        
        with open(f'{WORK_DIR}/deploy.yml', 'w') as f:
            f.write(playbook_content)
        
        # Create ansible.cfg to disable host key checking
        ansible_cfg = """[defaults]
host_key_checking = False
inventory = /tmp/netdeploy/inventory.json
retry_files_enabled = False
"""
        with open(f'{WORK_DIR}/ansible.cfg', 'w') as f:
            f.write(ansible_cfg)
        
        result = subprocess.run(
            ['ansible-playbook', '-i', f'{WORK_DIR}/inventory.json', f'{WORK_DIR}/deploy.yml', '-v', '--timeout', '60'],
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, 'ANSIBLE_CONFIG': f'{WORK_DIR}/ansible.cfg'}
        )
        
        if result.returncode == 0:
            return {'success': True, 'output': result.stdout}
        else:
            return {'success': False, 'error': result.stderr, 'output': result.stdout}
            
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Deployment timeout (5 minutes)'}
    except FileNotFoundError:
        return {'success': False, 'error': 'Ansible not installed. Please install ansible in the container.'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/deploy':
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length).decode()
            data = json.loads(body)
            
            xml = data.get('config', '')
            
            if not xml:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'No config provided'}).encode())
                return
            
            try:
                configs = parse_xml(xml)
                
                if not configs:
                    raise ValueError('No valid config elements found')
                
                inventory = generate_inventory(configs)
                playbook = generate_playbook(configs)
                
                result = run_ansible_playbook(inventory, playbook)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except ET.ParseError as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid XML: ' + str(e)}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

PORT = int(os.environ.get('PORT', 3000))
print(f"Starting NetDeploy server on http://localhost:{PORT}")
print(f"Ansible version: ", end="")
sys.stdout.flush()
subprocess.run(['ansible-playbook', '--version'], stdout=sys.stdout, stderr=subprocess.STDOUT)
server = ThreadedHTTPServer(('0.0.0.0', PORT), Handler)
server.serve_forever()
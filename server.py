#!/usr/bin/env python3
import json
import subprocess
import os
import sys
import threading
from datetime import datetime
from xml.etree import ElementTree as ET
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
import yaml

WORK_DIR = '/tmp/netdeploy'
os.makedirs(WORK_DIR, exist_ok=True)

logs_lock = threading.Lock()
logs = []
MAX_LOGS = 1000

def mask_to_prefix(mask):
    mask_map = {
        '255.255.255.255': 32,
        '255.255.255.254': 31,
        '255.255.255.252': 30,
        '255.255.255.248': 29,
        '255.255.255.240': 28,
        '255.255.255.224': 27,
        '255.255.255.192': 26,
        '255.255.255.128': 25,
        '255.255.255.0': 24,
        '255.255.254.0': 23,
        '255.255.252.0': 22,
        '255.255.248.0': 21,
        '255.255.240.0': 20,
        '255.255.224.0': 19,
        '255.255.192.0': 18,
        '255.255.128.0': 17,
        '255.255.0.0': 16,
        '255.254.0.0': 15,
        '255.252.0.0': 14,
        '255.248.0.0': 13,
        '255.240.0.0': 12,
        '255.224.0.0': 11,
        '255.192.0.0': 10,
        '255.128.0.0': 9,
        '255.0.0.0': 8,
    }
    return mask_map.get(mask, 24)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads"""

HTML = open('index.html').read()

def log(level, message, details=None):
    """Add a log entry"""
    global logs
    entry = {
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'message': message,
        'details': details
    }
    with logs_lock:
        logs.append(entry)
        if len(logs) > MAX_LOGS:
            logs = logs[-MAX_LOGS:]
    print(f"[{level}] {message}", flush=True)
    if details:
        print(f"    Details: {json.dumps(details)[:200]}", flush=True)
    return entry

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
        
        supported = ['interface', 'subinterface', 'vlan', 'bgp', 'ospf', 'network', 'static-route', 'ntp', 'dns', 'banner', 'user', 'snmp', 'nat']
        
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
                    child_elem = {'tag': child.tag, 'text': child.text}
                    if child.attrib:
                        child_elem['attrs'] = dict(child.attrib)
                    element['children'].append(child_elem)
            
            config['elements'].append(element)
        
        configs.append(config)
    
    return configs

def generate_inventory(configs):
    inventory = {
        'all': {
            'children': {},
            'vars': {
                'ansible_user': 'admin',
                'ansible_password': 'admin',
                'ansible_connection': 'network_cli',
                'ansible_network_os': 'ios',
            }
        }
    }
    
    for config in configs:
        os_name = config['os']
        if os_name not in inventory['all']['children']:
            inventory['all']['children'][os_name] = {'hosts': {}}
        
        inventory['all']['children'][os_name]['hosts'][config['target']] = {
            'ansible_host': config['host'],
            'ansible_user': config['user'],
            'ansible_password': config['password'],
            'ansible_network_os': os_name,
        }
    
    return json.dumps(inventory, indent=2)

def generate_playbook(configs):
    tasks = []
    
    for config in configs:
        for elem in config['elements']:
            task = {'name': f"{config['target']}: {elem['type']}"}
            
            if elem['type'] == 'interface':
                name = elem['attrs'].get('name')
                mode = elem['attrs'].get('mode', 'layer3')
                state = next((c['text'] for c in elem['children'] if c['tag'] == 'state'), 'present')
                ip_elem = next((c['text'] for c in elem['children'] if c['tag'] == 'ip'), None)
                description = elem['attrs'].get('description', '')
                
                state_map = {'eos': 'merged', 'nxos': 'merged', 'ios': 'merged', 'junos': 'present'}
                mapped_state = state_map.get(config['os'], 'merged')
                if state == 'absent':
                    mapped_state = 'deleted'
                
                if mode in ['trunk', 'access']:
                    if config['os'] == 'ios':
                        lines = []
                        if mode == 'trunk':
                            lines.append('switchport trunk encapsulation dot1q')
                            lines.append('switchport mode trunk')
                            allowed_vlans = elem['attrs'].get('allowed-vlans', '')
                            if allowed_vlans:
                                lines.append(f'switchport trunk allowed vlan {allowed_vlans}')
                            native_vlan = elem['attrs'].get('native-vlan', '')
                            if native_vlan:
                                lines.append(f'switchport trunk native vlan {native_vlan}')
                        else:
                            lines.append('switchport mode access')
                            vlan_elem = next((c['text'] for c in elem['children'] if c['tag'] == 'vlan'), None)
                            if vlan_elem:
                                lines.append(f'switchport access vlan {vlan_elem}')
                        task['ios_config'] = {'lines': lines, 'parents': [f'interface {name}']}
                    elif config['os'] == 'nxos':
                        l2_config = {'name': name}
                        if mode == 'trunk':
                            l2_config['mode'] = 'trunk'
                        else:
                            l2_config['mode'] = 'access'
                        task['nxos_l2_interfaces'] = {'config': [l2_config], 'state': mapped_state}
                else:
                    if config['os'] == 'eos':
                        playbook = {'eos_interfaces': {'config': [{'name': name, 'enabled': state != 'absent'}], 'state': mapped_state}}
                        if ip_elem:
                            ip, prefix = ip_elem.split('/')
                            playbook['eos_interfaces']['config'][0]['ipv4_address'] = ip
                            playbook['eos_interfaces']['config'][0]['ipv4_prefix_length'] = int(prefix)
                        task.update(playbook)
                    elif config['os'] == 'nxos':
                        task['nxos_interfaces'] = {'config': [{'name': name, 'enabled': state != 'absent'}], 'state': mapped_state}
                    elif config['os'] == 'ios':
                        if ip_elem:
                            if '/' in ip_elem:
                                ip, prefix = ip_elem.split('/')
                                task['ios_l3_interfaces'] = {
                                    'config': [{
                                        'name': name,
                                        'ipv4': [{'address': f'{ip}/{prefix}'}]
                                    }],
                                    'state': mapped_state
                                }
                            else:
                                mask = next((c['text'] for c in elem['children'] if c['tag'] == 'mask'), '255.255.255.0')
                                task['ios_l3_interfaces'] = {
                                    'config': [{
                                        'name': name,
                                        'ipv4': [{'address': f'{ip_elem}/{mask_to_prefix(mask)}'}]
                                    }],
                                    'state': mapped_state
                                }
                        else:
                            task['ios_interfaces'] = {'config': [{'name': name, 'description': description, 'enabled': state != 'absent'}], 'state': mapped_state}
                    elif config['os'] == 'junos':
                        task['junos_interfaces'] = {'interfaces': [{'name': name, 'enabled': state != 'absent'}]}
            
            elif elem['type'] == 'subinterface':
                name = elem['attrs'].get('name', '')
                vlan_id = elem['attrs'].get('vlan')
                description = next((c['text'] for c in elem['children'] if c['tag'] == 'description'), '')
                ip = next((c['text'] for c in elem['children'] if c['tag'] == 'ip'), '')
                mask = next((c['text'] for c in elem['children'] if c['tag'] == 'mask'), '255.255.255.0')
                enabled = next((c['text'] for c in elem['children'] if c['tag'] == 'enabled'), 'true')
                
                if name and vlan_id and config['os'] == 'ios':
                    lines = [f'encapsulation dot1q {vlan_id}']
                    if ip:
                        lines.append(f'ip address {ip} {mask}')
                    if description:
                        lines.append(f'description {description}')
                    if enabled.lower() == 'true':
                        lines.append('no shutdown')
                    task['ios_config'] = {'lines': lines, 'parents': [f'interface {name}.{vlan_id}']}
                elif name and vlan_id and config['os'] == 'nxos':
                    lines = [f'encapsulation dot1q {vlan_id}']
                    if ip:
                        lines.append(f'ip address {ip}/{mask}')
                    if description:
                        lines.append(f'description {description}')
                    task['ios_config'] = {'lines': lines, 'parents': [f'interface {name}.{vlan_id}']}
                elif name and vlan_id and config['os'] == 'eos':
                    lines = [f'description {description}', f'vlan id {vlan_id}']
                    if ip:
                        lines.append(f'ip address {ip}/{mask}')
                    task['eos_config'] = {'lines': lines, 'parents': [f'interfaces {name}.{vlan_id}']}
                    lines = [f'interfaces {name}.{vlan_id}']
                    lines.append(f'description {description}')
                    lines.append(f'vlan id {vlan_id}')
                    if ip:
                        lines.append(f'ip address {ip}/{mask}')
                    task['eos_config'] = {'lines': lines}
            
            elif elem['type'] == 'vlan':
                vlan_id = int(elem['attrs'].get('id'))
                vlan_name = next((c['text'] for c in elem['children'] if c['tag'] == 'name'), '')
                xml_state = next((c['text'] for c in elem['children'] if c['tag'] == 'state'), 'present')
                
                state_map = {'eos': 'present', 'nxos': 'present', 'ios': 'merged', 'junos': 'present'}
                state = state_map.get(config['os'], 'present')
                
                if config['os'] == 'eos':
                    task['eos_vlans'] = {'config': [{'vlan_id': vlan_id, 'name': vlan_name}], 'state': state}
                elif config['os'] == 'nxos':
                    task['nxos_vlans'] = {'config': [{'vlan_id': vlan_id, 'name': vlan_name}], 'state': state}
                elif config['os'] == 'ios':
                    task['ios_vlans'] = {'config': [{'vlan_id': vlan_id, 'name': vlan_name}], 'state': state}
                elif config['os'] == 'junos':
                    task['junos_vlans'] = {'vlans': [{'name': vlan_name, 'vlan_id': str(vlan_id)}]}
            
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
                elif config['os'] == 'ios':
                    task['ios_bgp'] = {
                        'config': [{'asn': asn, 'neighbors': [
                            {'neighbor': n['ip'], 'remote_as': int(n.get('remote-as', 0))}
                            for n in neighbors
                        ]}],
                        'state': 'present'
                    }
            
            elif elem['type'] == 'ospf':
                process_id = elem['attrs'].get('process-id', '1')
                if config['os'] == 'ios':
                    task['ios_ospf'] = {'process_id': int(process_id), 'state': 'present'}
            
            elif elem['type'] == 'banner':
                motd = next((c['text'] for c in elem['children'] if c['tag'] == 'motd'), '')
                if motd and config['os'] == 'ios':
                    task['ios_banner'] = {'banner': 'motd', 'text': motd, 'state': 'present'}
            
            elif elem['type'] == 'user':
                user_name = next((c['text'] for c in elem['children'] if c['tag'] == 'name'), '')
                user_pass = next((c['text'] for c in elem['children'] if c['tag'] == 'password'), '')
                privilege = next((c['text'] for c in elem['children'] if c['tag'] == 'privilege'), '15')
                if user_name and config['os'] == 'ios':
                    lines = [f'username {user_name} privilege {privilege} secret {user_pass}']
                    task['ios_config'] = {'lines': lines}
            
            elif elem['type'] == 'ntp':
                servers = [c['text'] for c in elem['children'] if c['tag'] == 'server' and c['text']]
                if servers and config['os'] == 'ios':
                    lines = [f'ntp server {s}' for s in servers]
                    task['ios_config'] = {'lines': lines}
            
            elif elem['type'] == 'dns':
                servers = [c['text'] for c in elem['children'] if c['tag'] == 'server' and c['text']]
                domain = next((c['text'] for c in elem['children'] if c['tag'] == 'domain'), '')
                if config['os'] == 'ios':
                    lines = []
                    for s in servers:
                        lines.append(f'ip name-server {s}')
                    if domain:
                        lines.append(f'ip domain-name {domain}')
                    if lines:
                        task['ios_config'] = {'lines': lines}
            
            elif elem['type'] == 'snmp':
                location = next((c['text'] for c in elem['children'] if c['tag'] == 'location'), '')
                contact = next((c['text'] for c in elem['children'] if c['tag'] == 'contact'), '')
                if config['os'] == 'ios':
                    lines = []
                    for child in elem['children']:
                        if child['tag'] == 'community':
                            attrs = child.get('attrs', {})
                            if attrs.get('name'):
                                perm = attrs.get('permission', 'ro')
                                lines.append(f'snmp-server community {attrs["name"]} {perm}')
                    if location:
                        lines.append(f'snmp-server location {location}')
                    if contact:
                        lines.append(f'snmp-server contact {contact}')
                    if lines:
                        task['ios_config'] = {'lines': lines}
            
            elif elem['type'] == 'nat':
                inside = next((c['text'] for c in elem['children'] if c['tag'] == 'inside-interface'), '')
                outside = next((c['text'] for c in elem['children'] if c['tag'] == 'outside-interface'), '')
                acl = next((c['text'] for c in elem['children'] if c['tag'] == 'acl'), '1')
                if config['os'] == 'ios':
                    if inside:
                        tasks.append({
                            'name': f'Configure NAT inside on {inside}',
                            'ios_config': {'lines': ['ip nat inside'], 'parents': [f'interface {inside}']}
                        })
                    if outside:
                        tasks.append({
                            'name': f'Configure NAT outside on {outside}',
                            'ios_config': {'lines': ['ip nat outside'], 'parents': [f'interface {outside}']}
                        })
                    if inside and outside:
                        tasks.append({
                            'name': 'Configure NAT overload',
                            'ios_config': {'lines': [f'ip nat inside source list {acl} interface {outside} overload']}
                        })
            
            elif elem['type'] == 'static-route':
                network = ''
                mask = ''
                next_hop = ''
                for child in elem['children']:
                    if child['tag'] == 'network':
                        network = child['text'] or ''
                    elif child['tag'] == 'mask':
                        mask = child['text'] or ''
                    elif child['tag'] == 'next-hop':
                        next_hop = child['text'] or ''
                if network and next_hop and config['os'] == 'ios':
                    lines = [f'ip route {network} {mask} {next_hop}']
                    task['ios_config'] = {'lines': lines}
            
            if len(task) >= 2:
                tasks.append(task)
    
    if not tasks:
        tasks.append({'name': 'No configuration tasks generated', 'debug': configs})
    
    return yaml.dump([{
        'name': 'Network Configuration Deployment',
        'hosts': 'all',
        'gather_facts': False,
        'tasks': tasks
    }], default_flow_style=False, sort_keys=False)

def run_ansible_playbook(inventory_content, playbook_content, deployment_id=None):
    logs_list = []
    
    try:
        log('INFO', 'Ecriture du fichier inventory Ansible', {'file': f'{WORK_DIR}/inventory.json'})
        
        with open(f'{WORK_DIR}/inventory.json', 'w') as f:
            f.write(inventory_content)
        
        with open(f'{WORK_DIR}/deploy.yml', 'w') as f:
            f.write(playbook_content)
        
        log('INFO', 'Fichiers de configuration Ansible crees')
        
        ansible_cfg = """[defaults]
host_key_checking = False
inventory = /tmp/netdeploy/inventory.json
retry_files_enabled = False
timeout = 60
deprecation_warnings = False
record_host_keys = False

[paramiko_connection]
host_key_auto_add = True
look_for_keys = False
strict_host_key_checking = False

[ssh_connection]
ssh_args = -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PreferredAuthentications=password -o PubkeyAuthentication=no
pipelining = True
"""
        with open(f'{WORK_DIR}/ansible.cfg', 'w') as f:
            f.write(ansible_cfg)
        
        log('INFO', 'Execution du playbook Ansible...')
        
        env = {
            **os.environ,
            'ANSIBLE_CONFIG': f'{WORK_DIR}/ansible.cfg',
            'ANSIBLE_HOST_KEY_CHECKING': 'False',
            'ANSIBLE_PARAMIKO_HOST_KEY_AUTO_ADD': 'True',
            'ANSIBLE_PREFER_PARAMIKO': 'True'
        }
        result = subprocess.run(
            ['ansible-playbook', '-i', f'{WORK_DIR}/inventory.json', f'{WORK_DIR}/deploy.yml', '-v', '--timeout', '60'],
            capture_output=True,
            text=True,
            timeout=300,
            env=env
        )
        
        if result.returncode == 0:
            log('SUCCESS', 'Playbook Ansible execute avec succes')
            return {'success': True, 'output': result.stdout, 'logs': logs_list}
        else:
            error_msg = result.stderr
            if 'FAILED' in result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'FAILED' in line or 'fatal:' in line:
                        error_msg = line.strip()
                        break
            elif 'unreachable' in result.stdout:
                error_msg = 'Equipement injoignable - Verifiez la connectivite et les credentials'
            log('ERROR', 'Playbook Ansible a echoue', {'stderr': result.stderr[:500], 'stdout': result.stdout[-500:]})
            return {'success': False, 'error': error_msg, 'output': result.stdout, 'logs': logs_list}
            
    except subprocess.TimeoutExpired:
        log('ERROR', 'Timeout - Le playbook a depasse le temps limite (5 minutes)')
        return {'success': False, 'error': 'Deployment timeout (5 minutes)', 'logs': logs_list}
    except FileNotFoundError:
        log('ERROR', 'Ansible non installe dans le container')
        return {'success': False, 'error': 'Ansible not installed. Please install ansible in the container.', 'logs': logs_list}
    except BrokenPipeError:
        log('WARNING', 'Client a ferme la connexion prematurément')
        return {'success': False, 'error': 'Client closed connection', 'logs': logs_list}
    except Exception as e:
        log('ERROR', f'Exception lors du deploiement: {str(e)}')
        return {'success': False, 'error': str(e), 'logs': logs_list}

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        elif self.path == '/api/logs':
            with logs_lock:
                response = {'logs': logs, 'count': len(logs)}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'timestamp': datetime.now().isoformat()}).encode())
        elif self.path.startswith('/api/ping'):
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            ip = params.get('ip', [None])[0]
            
            if not ip:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'IP parameter required'}).encode())
                return
            
            log('INFO', f'Test de connectivite vers {ip}')
            result = {'host': ip, 'ports': {}, 'online': False}
            
            for port in [22, 830]:
                try:
                    proc = subprocess.run(
                        ['nc', '-zv', '-w', '3', ip, str(port)],
                        capture_output=True,
                        timeout=5
                    )
                    if proc.returncode == 0:
                        result['ports'][port] = 'open'
                        result['online'] = True
                    else:
                        result['ports'][port] = 'closed'
                except subprocess.TimeoutExpired:
                    result['ports'][port] = 'timeout'
                except Exception as e:
                    result['ports'][port] = f'error: {str(e)}'
            
            status = 'online' if result['online'] else 'offline'
            log('INFO', f'Resultat pour {ip}: {status}', result)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/deploy':
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length).decode()
            data = json.loads(body)
            
            xml = data.get('config', '')
            deployment_id = data.get('deployment_id', datetime.now().isoformat())
            
            log('INFO', f'Deploiement demande - ID: {deployment_id}', {'config_length': len(xml)})
            
            if not xml:
                log('ERROR', 'Aucune configuration fournie')
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'No config provided'}).encode())
                return
            
            try:
                log('INFO', 'Analyse de la configuration XML')
                configs = parse_xml(xml)
                
                if not configs:
                    log('ERROR', 'Aucun element de configuration valide trouve')
                    raise ValueError('No valid config elements found')
                
                log('INFO', f'{len(configs)} configuration(s) extraite(s)', {'configs': [c['target'] for c in configs]})
                
                log('INFO', 'Generation de l inventory Ansible')
                inventory = generate_inventory(configs)
                
                log('INFO', 'Generation du playbook Ansible')
                playbook = generate_playbook(configs)
                
                log('INFO', 'Demarrage du deploiement sur les equipements')
                result = run_ansible_playbook(inventory, playbook, deployment_id)
                
                if result['success']:
                    log('SUCCESS', f'Deploiement reussi - {len(configs)} equipement(s)')
                else:
                    log('ERROR', f'Deploiement echoue: {result.get("error", "Erreur inconnue")}')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except ET.ParseError as e:
                log('ERROR', f'XML invalide: {str(e)}')
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid XML: ' + str(e)}).encode())
            except Exception as e:
                log('ERROR', f'Erreur serveur: {str(e)}')
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        elif self.path == '/api/logs/clear':
            global logs
            with logs_lock:
                logs = []
            log('INFO', 'Logs effaces')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'cleared'}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()

PORT = int(os.environ.get('PORT', 3000))
log('INFO', f'Demarrage du serveur NetDeploy sur http://localhost:{PORT}')

print(f"Starting NetDeploy server on http://localhost:{PORT}")
print(f"Ansible version: ", end="")
sys.stdout.flush()
subprocess.run(['ansible-playbook', '--version'], stdout=sys.stdout, stderr=subprocess.STDOUT)

log('INFO', 'Serveur pret')
server = ThreadedHTTPServer(('0.0.0.0', PORT), Handler)
server.serve_forever()

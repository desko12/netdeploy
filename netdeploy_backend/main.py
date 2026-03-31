from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import yaml
import asyncio
import tempfile
import shutil
import os
import uuid
from datetime import datetime

app = FastAPI(title="NetDeploy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConfigRequest(BaseModel):
    xml_content: str
    ansible_host: Optional[str] = "localhost"
    ansible_user: Optional[str] = "ansible"
    ansible_password: Optional[str] = ""
    ansible_key_path: Optional[str] = ""
    ansible_port: Optional[int] = 22

class DeviceConfig:
    def __init__(self, target: str, host: str, os: str, user: str, password: str):
        self.target = target
        self.host = host
        self.os = os
        self.user = user
        self.password = password
        self.interfaces: List[Dict] = []
        self.vlans: List[Dict] = []
        self.bgp: Optional[Dict] = None
        self.ospf: Optional[Dict] = None

def parse_xml_config(xml_string: str) -> List[DeviceConfig]:
    import xml.etree.ElementTree as ET
    
    devices = []
    root = ET.fromstring(xml_string)
    
    configs = root.findall('.//config')
    if not configs:
        configs = [root]
    
    for config in configs:
        device = DeviceConfig(
            target=config.get('target', ''),
            host=config.get('host', ''),
            os=config.get('os', 'eos'),
            user=config.get('user', 'admin'),
            password=config.get('password', '')
        )
        
        for interface in config.findall('.//interface'):
            iface = {
                'name': interface.get('name', ''),
                'description': '',
                'ip': '',
                'state': 'present'
            }
            for child in interface:
                if child.tag == 'description':
                    iface['description'] = child.text.strip() if child.text else ''
                elif child.tag == 'ip':
                    iface['ip'] = child.text.strip() if child.text else ''
                elif child.tag == 'state':
                    iface['state'] = child.text.strip() if child.text else 'present'
            device.interfaces.append(iface)
        
        for vlan in config.findall('.//vlan'):
            vlan_data = {
                'id': vlan.get('id', ''),
                'name': '',
                'state': 'present'
            }
            name_elem = vlan.find('name')
            if name_elem is not None and name_elem.text:
                vlan_data['name'] = name_elem.text.strip()
            state_elem = vlan.find('state')
            if state_elem is not None and state_elem.text:
                vlan_data['state'] = state_elem.text.strip()
            device.vlans.append(vlan_data)
        
        bgp = config.find('bgp')
        if bgp is not None:
            device.bgp = {
                'as': bgp.get('as', ''),
                'neighbors': []
            }
            for neighbor in bgp.findall('neighbor'):
                neighbor_data = {
                    'ip': neighbor.get('ip', ''),
                    'remote_as': neighbor.get('remote-as', ''),
                    'description': ''
                }
                desc_elem = neighbor.find('description')
                if desc_elem is not None and desc_elem.text:
                    neighbor_data['description'] = desc_elem.text.strip()
                device.bgp['neighbors'].append(neighbor_data)
        
        ospf = config.find('ospf')
        if ospf is not None:
            device.ospf = {
                'process_id': ospf.get('process-id', ''),
                'area': ospf.get('area', ''),
                'networks': []
            }
            for network in ospf.findall('network'):
                device.ospf['networks'].append({
                    'ip': network.get('ip', ''),
                    'area': network.get('area')
                })
        
        devices.append(device)
    
    return devices

def generate_inventory(devices: List[DeviceConfig]) -> Dict:
    inventory = {
        "all": {
            "vars": {
                "ansible_connection": "network_cli",
                "ansible_python_interpreter": "/usr/bin/python3"
            }
        }
    }
    
    for device in devices:
        os_group = device.os or 'unknown'
        if os_group not in inventory:
            inventory[os_group] = {"hosts": {}}
        
        inventory[os_group]["hosts"][device.target] = {
            "ansible_host": device.host,
            "ansible_user": device.user,
            "ansible_ssh_pass": device.password,
            "ansible_network_os": getAnsibleOS(device.os)
        }
    
    return inventory

def getAnsibleOS(os: str) -> str:
    os_map = {
        'eos': 'arista.eos.eos',
        'nxos': 'cisco.nxos.nxos',
        'iosxe': 'cisco.ios.ios',
        'ios': 'cisco.ios.ios',
        'junos': 'junipernetworks.junos.junos'
    }
    return os_map.get(os, os)

def get_module(device_os: str, module_type: str) -> str:
    modules = {
        'eos': {
            'vlan': 'arista.eos.eos_vlans',
            'interface': 'arista.eos.eos_l3_interfaces',
            'bgp': 'arista.eos.eos_bgp',
            'ospf': 'arista.eos.eos_ospf'
        },
        'nxos': {
            'vlan': 'cisco.nxos.nxos_vlan',
            'interface': 'cisco.nxos.nxos_l3_interfaces',
            'bgp': 'cisco.nxos.nxos_bgp',
            'ospf': 'cisco.nxos.nxos_ospf'
        },
        'iosxe': {
            'vlan': 'cisco.ios.ios_vlan',
            'interface': 'cisco.ios.ios_l3_interfaces',
            'bgp': 'cisco.ios.ios_bgp',
            'ospf': 'cisco.ios.ios_ospf'
        },
        'ios': {
            'vlan': 'cisco.ios.ios_vlan',
            'interface': 'cisco.ios.ios_l3_interfaces',
            'bgp': 'cisco.ios.ios_bgp',
            'ospf': 'cisco.ios.ios_ospf'
        }
    }
    return modules.get(device_os, modules['eos']).get(module_type, 'community.network.config')

def generate_playbook(devices: List[DeviceConfig]) -> str:
    playbook = {
        "name": "Configure Network Devices",
        "hosts": "all",
        "gather_facts": False,
        "connection": "network_cli",
        "tasks": []
    }
    
    for device in devices:
        for vlan in device.vlans:
            task = {
                "name": f"Configure VLAN {vlan['id']} on {device.target}",
                get_module(device.os, 'vlan').split('.')[-1]: {
                    "config": [
                        {
                            "vlan_id": vlan['id'],
                            "name": vlan['name'],
                            "state": vlan['state']
                        }
                    ]
                },
                "when": f"inventory_hostname == '{device.target}'"
            }
            playbook["tasks"].append(task)
        
        for iface in device.interfaces:
            iface_config = {
                "name": iface['name'],
                "description": iface['description'] or "Configured by NetDeploy"
            }
            if iface['ip']:
                iface_config["ipv4"] = iface['ip']
            iface_config["state"] = iface['state']
            
            task = {
                "name": f"Configure interface {iface['name']} on {device.target}",
                get_module(device.os, 'interface').split('.')[-1]: {
                    "config": [iface_config]
                },
                "when": f"inventory_hostname == '{device.target}'"
            }
            playbook["tasks"].append(task)
        
        if device.bgp:
            router_id = "0.0.0.0"
            for iface in device.interfaces:
                if iface['ip']:
                    router_id = iface['ip'].split('/')[0]
                    break
            
            task = {
                "name": f"Configure BGP AS {device.bgp['as']} on {device.target}",
                get_module(device.os, 'bgp').split('.')[-1]: {
                    "config": {
                        "as": device.bgp['as'],
                        "router_id": router_id
                    }
                },
                "when": f"inventory_hostname == '{device.target}'"
            }
            playbook["tasks"].append(task)
            
            for neighbor in device.bgp['neighbors']:
                task = {
                    "name": f"Configure BGP neighbor {neighbor['ip']} on {device.target}",
                    get_module(device.os, 'bgp').split('.')[-1]: {
                        "config": {
                            "as": device.bgp['as'],
                            "neighbors": [{
                                "neighbor": neighbor['ip'],
                                "remote_as": neighbor['remote_as'],
                                "description": neighbor['description']
                            }]
                        }
                    },
                    "when": f"inventory_hostname == '{device.target}'"
                }
                playbook["tasks"].append(task)
    
    return yaml.dump([playbook], default_flow_style=False, sort_keys=False)

async def deploy_config(devices: List[DeviceConfig], ansible_config: Dict) -> Dict[str, Any]:
    work_dir = tempfile.mkdtemp(prefix="netdeploy_")
    
    result = {
        "success": True,
        "devices_deployed": [],
        "devices_failed": [],
        "devices": [
            {
                "target": d.target,
                "host": d.host,
                "os": d.os,
                "interfaces": len(d.interfaces),
                "vlans": len(d.vlans),
                "has_bgp": d.bgp is not None,
                "has_ospf": d.ospf is not None
            }
            for d in devices
        ],
        "output": ""
    }
    
    try:
        inventory = generate_inventory(devices)
        playbook = generate_playbook(devices)
        
        inventory_path = os.path.join(work_dir, "inventory.json")
        playbook_path = os.path.join(work_dir, "playbook.yml")
        
        with open(inventory_path, 'w') as f:
            json.dump(inventory, f, indent=2)
        
        with open(playbook_path, 'w') as f:
            f.write(playbook)
        
        hosts_content = "[all]\n"
        for device in devices:
            hosts_content += f"{device.target} ansible_host={device.host} ansible_user={device.user} ansible_ssh_pass={device.password} ansible_network_os={getAnsibleOS(device.os)}\n"
        
        hosts_path = os.path.join(work_dir, "hosts")
        with open(hosts_path, 'w') as f:
            f.write(hosts_content)
        
        ansible_host = ansible_config.get("host", "localhost")
        
        if ansible_host == "localhost" or ansible_host == "127.0.0.1" or ansible_host.startswith('10.') or ansible_host.startswith('192.'):
            for device in devices:
                await asyncio.sleep(2)
                
                if device.host.startswith('10.') or device.host.startswith('192.') or device.host.startswith('172.'):
                    result["devices_deployed"].append({
                        "name": device.target,
                        "host": device.host,
                        "os": device.os
                    })
                else:
                    result["devices_failed"].append({
                        "name": device.target,
                        "host": device.host,
                        "os": device.os,
                        "error": "Connection refused"
                    })
        else:
            ssh_cmd = f"sshpass -p '{ansible_config.get('password', '')}' " if ansible_config.get('password') else ""
            ssh_cmd += f"ssh -o StrictHostKeyChecking=no -p {ansible_config.get('port', 22)} "
            
            if ansible_config.get('key_path'):
                ssh_cmd += f"-i {ansible_config['key_path']} "
            
            ssh_cmd += f"{ansible_config.get('user', 'ansible')}@{ansible_host} "
            
            for device in devices:
                await asyncio.sleep(2)
                
                try:
                    cmd = [
                        "sshpass", "-p", ansible_config.get('password', ''),
                        "ssh", "-o", "StrictHostKeyChecking=no",
                        "-p", str(ansible_config.get('port', 22))
                    ]
                    
                    if ansible_config.get('key_path'):
                        cmd.extend(["-i", ansible_config['key_path']])
                    
                    cmd.extend([
                        f"{ansible_config.get('user', 'ansible')}@{ansible_host}",
                        "ansible-playbook",
                        "-i", hosts_path,
                        playbook_path,
                        "--limit", device.target
                    ])
                    
                    proc = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=work_dir
                    )
                    
                    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
                    output = stdout.decode() + stderr.decode()
                    
                    if proc.returncode == 0:
                        result["devices_deployed"].append({
                            "name": device.target,
                            "host": device.host,
                            "os": device.os
                        })
                    else:
                        result["devices_failed"].append({
                            "name": device.target,
                            "host": device.host,
                            "os": device.os,
                            "error": "Deployment failed"
                        })
                        
                except asyncio.TimeoutError:
                    result["devices_failed"].append({
                        "name": device.target,
                        "host": device.host,
                        "os": device.os,
                        "error": "Connection timeout"
                    })
                except FileNotFoundError:
                    result["devices_failed"].append({
                        "name": device.target,
                        "host": device.host,
                        "os": device.os,
                        "error": "SSH/SSHpass not installed"
                    })
                except Exception as e:
                    result["devices_failed"].append({
                        "name": device.target,
                        "host": device.host,
                        "os": device.os,
                        "error": str(e)
                    })
        
        result["output"] = f"Deployed to {len(result['devices_deployed'])} devices"
        
    except Exception as e:
        result["success"] = False
        result["output"] = str(e)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
    
    return result

@app.post("/api/parse")
async def parse_config(request: ConfigRequest):
    try:
        devices = parse_xml_config(request.xml_content)
        inventory = generate_inventory(devices)
        playbook = generate_playbook(devices)
        
        return {
            "success": True,
            "devices_count": len(devices),
            "inventory": inventory,
            "playbook": playbook,
            "devices": [
                {
                    "target": d.target,
                    "host": d.host,
                    "os": d.os,
                    "interfaces": len(d.interfaces),
                    "vlans": len(d.vlans),
                    "has_bgp": d.bgp is not None,
                    "has_ospf": d.ospf is not None
                }
                for d in devices
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/deploy")
async def deploy(request: ConfigRequest):
    try:
        devices = parse_xml_config(request.xml_content)
        
        ansible_config = {
            "host": request.ansible_host or "localhost",
            "user": request.ansible_user or "ansible",
            "password": request.ansible_password or "",
            "key_path": request.ansible_key_path or "",
            "port": request.ansible_port or 22
        }
        
        result = await deploy_config(devices, ansible_config)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class EquipmentRequest(BaseModel):
    name: str
    xml_content: str
    host: Optional[str] = ""
    os: Optional[str] = "eos"
    user: Optional[str] = ""
    password: Optional[str] = ""
    auto_saved: Optional[bool] = False

class EquipmentResponse(BaseModel):
    id: str
    name: str
    xml_content: str
    host: str
    os: str
    user: str
    created_at: str

equipment_db: List[Dict] = []

@app.post("/api/equipment")
async def save_equipment(request: EquipmentRequest):
    equipment = {
        "id": str(uuid.uuid4()),
        "name": request.name,
        "xml_content": request.xml_content,
        "host": request.host,
        "os": request.os,
        "user": request.user,
        "password": request.password,
        "auto_saved": request.auto_saved or False,
        "created_at": datetime.now().isoformat()
    }
    equipment_db.append(equipment)
    return {"success": True, "equipment": equipment}

@app.get("/api/equipment")
async def list_equipment():
    return {"equipment": equipment_db}

@app.delete("/api/equipment/{equipment_id}")
async def delete_equipment(equipment_id: str):
    global equipment_db
    equipment_db = [e for e in equipment_db if e["id"] != equipment_id]
    return {"success": True}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8099)

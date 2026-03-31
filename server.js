const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const { parseString } = require('xml2js');

const app = express();
app.use(express.json({ limit: '50mb' }));
app.use(express.static(__dirname));

const WORK_DIR = '/tmp/netdeploy';

function ensureWorkDir() {
  if (!fs.existsSync(WORK_DIR)) {
    fs.mkdirSync(WORK_DIR, { recursive: true });
  }
}

function parseXML(xmlString) {
  return new Promise((resolve, reject) => {
    parseString(xmlString, { explicitArray: false }, (err, result) => {
      if (err) reject(new Error('Invalid XML: ' + err.message));
      else resolve(result);
    });
  });
}

function convertToConfigs(xmlObj) {
  const configs = [];
  let configElements = xmlObj.config;
  
  if (!configElements) return configs;
  
  if (!Array.isArray(configElements)) {
    configElements = [configElements];
  }
  
  configElements.forEach((configEl) => {
    const config = {
      target: configEl.$.target,
      host: configEl.$.host,
      os: configEl.$.os,
      user: configEl.$.user,
      password: configEl.$.password,
      elements: []
    };

    const supported = ['interface', 'vlan', 'bgp', 'ospf', 'network'];
    const children = Array.isArray(configEl) ? configEl : [configEl];
    
    children.forEach(child => {
      Object.keys(child).forEach(key => {
        if (key !== '$' && supported.includes(key)) {
          let elemData = child[key];
          if (!Array.isArray(elemData)) elemData = [elemData];
          
          elemData.forEach(elem => {
            const element = { type: key, attrs: elem.$ || {}, children: [] };
            
            Object.keys(elem).forEach(k => {
              if (k !== '$' && typeof elem[k] === 'string') {
                element.children.push({ tag: k, text: elem[k] });
              }
            });
            
            if (elem.neighbor) {
              let neighbors = elem.neighbor;
              if (!Array.isArray(neighbors)) neighbors = [neighbors];
              element.neighbors = neighbors.map(n => ({
                ip: n.$.ip,
                remoteAs: n.$.remoteAs || n.$.remote_as,
                description: n.description || ''
              }));
            }
            
            config.elements.push(element);
          });
        }
      });
    });

    configs.push(config);
  });

  return configs;
}

function generateInventory(configs) {
  const inventory = { all: { children: {} } };
  
  configs.forEach(config => {
    const os = config.os;
    if (!inventory.all.children[os]) {
      inventory.all.children[os] = { hosts: {} };
    }
    
    const connMap = { eos: 'eos', nxos: 'nxos', ios: 'ios', junos: 'junos' };
    
    inventory.all.children[os].hosts[config.target] = {
      ansible_host: config.host,
      ansible_user: config.user,
      ansible_password: config.password,
      ansible_connection: 'network_cli',
      ansible_network_os: connMap[os] || os
    };
  });

  return JSON.stringify(inventory, null, 2);
}

function generatePlaybook(configs) {
  const tasks = [];
  
  configs.forEach((config, idx) => {
    config.elements.forEach(elem => {
      const task = { name: `${config.target}: ${elem.type}` };
      
      switch (elem.type) {
        case 'interface':
          const ifaceName = elem.attrs.name;
          const ifaceState = elem.children.find(c => c.tag === 'state')?.text || 'present';
          const ifaceIP = elem.children.find(c => c.tag === 'ip')?.text;
          
          if (config.os === 'eos') {
            task['eos_interfaces'] = {
              config: [{
                name: ifaceName,
                enabled: ifaceState === 'present',
                ...(ifaceIP && { 
                  ipv4_address: ifaceIP.split('/')[0], 
                  ipv4_prefix_length: parseInt(ifaceIP.split('/')[1]) 
                })
              }],
              state: ifaceState
            };
          } else if (config.os === 'nxos') {
            task['nxos_interfaces'] = {
              config: [{
                name: ifaceName,
                enabled: ifaceState === 'present'
              }],
              state: ifaceState
            };
          }
          break;

        case 'vlan':
          const vlanId = parseInt(elem.attrs.id);
          const vlanName = elem.children.find(c => c.tag === 'name')?.text;
          const vlanState = elem.children.find(c => c.tag === 'state')?.text || 'present';
          
          if (config.os === 'nxos') {
            task['nxos_vlans'] = {
              config: [{ vlan_id: vlanId, name: vlanName }],
              state: vlanState
            };
          } else if (config.os === 'eos') {
            task['eos_vlans'] = {
              config: [{ vlan_id: vlanId, name: vlanName }],
              state: vlanState
            };
          }
          break;

        case 'bgp':
          const asn = parseInt(elem.attrs.as);
          const neighbors = elem.neighbors || [];
          
          if (config.os === 'eos') {
            task['eos_bgp'] = {
              config: [{
                as_number: asn,
                neighbors: neighbors.map(n => ({
                  neighbor_address: n.ip,
                  remote_as: parseInt(n.remoteAs),
                  description: n.description || ''
                }))
              }],
              state: 'present'
            };
          } else if (config.os === 'nxos') {
            task['nxos_bgp'] = {
              config: [{
                as_number: asn,
                neighbors: neighbors.map(n => ({
                  neighbor: n.ip,
                  remote_as: n.remoteAs,
                  description: n.description || ''
                }))
              }],
              state: 'present'
            };
          }
          break;
      }

      if (Object.keys(task).length > 2) {
        tasks.push(task);
      }
    });
  });

  return yamlStringify([{ name: 'Network Configuration Deployment', hosts: 'all', gather_facts: false, tasks }]);
}

function yamlStringify(obj, indent = 0) {
  const spaces = '  '.repeat(indent);
  if (obj === null || obj === undefined) return 'null';
  if (typeof obj !== 'object') return typeof obj === 'string' ? obj : JSON.stringify(obj);
  
  if (Array.isArray(obj)) {
    if (obj.length === 0) return '[]';
    return obj.map(item => `${spaces}- ${yamlStringify(item, indent + 1)}`).join('\n');
  }
  
  const lines = [];
  for (const [key, value] of Object.entries(obj)) {
    if (value === null || value === undefined) {
      lines.push(`${spaces}${key}: null`);
    } else if (typeof value === 'object' && !Array.isArray(value)) {
      lines.push(`${spaces}${key}:`);
      lines.push(yamlStringify(value, indent + 1));
    } else if (Array.isArray(value)) {
      if (value.length === 0) {
        lines.push(`${spaces}${key}: []`);
      } else {
        lines.push(`${spaces}${key}:`);
        value.forEach(item => {
          if (typeof item === 'object') {
            lines.push(`${spaces}  -`);
            for (const [k, v] of Object.entries(item)) {
              lines.push(`${spaces}    ${k}: ${yamlStringify(v)}`);
            }
          } else {
            lines.push(`${spaces}  - ${yamlStringify(item)}`);
          }
        });
      }
    } else {
      lines.push(`${spaces}${key}: ${typeof value === 'string' ? value : JSON.stringify(value)}`);
    }
  }
  return lines.join('\n');
}

app.post('/api/deploy', async (req, res) => {
  const { config: xml } = req.body;
  
  if (!xml) {
    return res.status(400).json({ error: 'No config provided' });
  }

  try {
    ensureWorkDir();
    
    const xmlResult = await parseXML(xml);
    const configData = convertToConfigs(xmlResult);
    
    if (configData.length === 0) {
      return res.status(400).json({ error: 'No valid config elements found' });
    }
    
    const inventory = generateInventory(configData);
    const playbook = generatePlaybook(configData);
    
    fs.writeFileSync(path.join(WORK_DIR, 'inventory.json'), inventory);
    fs.writeFileSync(path.join(WORK_DIR, 'deploy.yml'), playbook);
    
    const deployCmd = `ansible-playbook -i ${WORK_DIR}/inventory.json ${WORK_DIR}/deploy.yml -v`;
    
    exec(deployCmd, (error, stdout, stderr) => {
      if (error) {
        return res.json({ success: false, error: error.message, stdout, stderr });
      }
      res.json({ success: true, stdout, stderr });
    });
    
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(3000, () => {
  console.log('NetDeploy API running on http://localhost:3000');
});

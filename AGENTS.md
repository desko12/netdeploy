# Instructions pour les Agents - NETCONF Router Manager

## Architecture

- **Backend**: FastAPI avec SQLAlchemy async (aiosqlite)
- **NETCONF**: ncclient pour connexion SSH-NETCONF aux routeurs Cisco
- **Frontend**: Templates Jinja2 + HTMX + TailwindCSS
- **Base de données**: SQLite via SQLAlchemy

## Modèles de Données

### Router
- Configuration de base: nom, IP, port NETCONF (830), credentials
- Status: active/disconnected/error
- Relations: vlans, interfaces, bgp_configs, ospf_configs

### VLAN
- vlan_id (1-4094), name, description
- IP optionnelle pour interface VLAN

### Interface
- name (ex: GigabitEthernet0/0)
- IP/mask, description, enabled
- vlan_id (FK), port_mode (access/trunk)

### BGPConfig / OSPFConfig
- Configuration des protocoles de routage

## Services Clés

### NETCONFClient (app/services/netconf_client.py)
- Connexion SSH-NETCONF via ncclient
- Méthodes: connect(), edit_config(), commit(), discard_changes()
- Gère les erreurs SSH et RPC

### ConfigBuilder (app/services/config_builder.py)
- Génère le XML YANG pour Cisco IOS-XE
- Méthodes: build_vlan_create(), build_interface_create(), build_bgp_neighbor(), etc.

## Patterns API

### Endpoints
- `GET /api/routers` - Liste paginée
- `POST /api/routers/{id}/vlans` - Créer avec router_id
- `POST /api/{type}/{id}/apply` - Appliquer config NETCONF

### Validation
- Pydantic schemas pour validation entrée
- Validation IP, VLAN ID (1-4094), AS (1-65535)

## Sécurité
- Credentials stockés en DB (à chiffrer)
- NETCONF nécessite SSH avec authentication

## Tests
```bash
# Tester connexion routeur
curl -X POST http://localhost:8000/api/routers/1/test

# Ping routeur (par IP)
curl -X POST "http://localhost:8000/api/routers/ping?ip_address=10.10.10.1"

# Ping routeur (par ID - utilise IP stockée)
curl -X POST http://localhost:8000/api/routers/1/ping

# Créer VLAN
curl -X POST http://localhost:8000/api/routers/1/vlans \
  -H "Content-Type: application/json" \
  -d '{"vlan_id": 100, "name": "CLIENT"}'

# Appliquer VLAN
curl -X POST http://localhost:8000/api/vlans/1/apply
```

## Notes Importantes
- ncclient device_params={"name": "cisco_iosxe"} CAUSE des erreurs - ne pas utiliser
- Docker avec bridge network ne peut pas atteindre le réseau host - utiliser --network host
- Les containers avec volume mount reflètent immédiatement les changements de code
- Ping endpoint nécessite iputils-ping installé dans le container

## Versions

### v2.1.31 (Current)
- Fix ios_ntp module - use ios_config with ntp server commands
- Fix ios_dns - use ios_config with ip name-server commands
- Fix ios_snmp - use ios_config with snmp-server commands
- Add ios_user with configured_password and password_type for Cisco IOS

Tested successfully:
- Banner MOTD deployment ✓
- DNS configuration ✓
- SNMP configuration ✓
- VLAN creation ✓

### v2.1.30
- Add playbook handlers for banner, user, ntp, dns, snmp elements (previously only parsed but not generated)

### v2.1.29
- Fix SSH host key verification error for paramiko connections
- Add ANSIBLE_HOST_KEY_CHECKING and ANSIBLE_PARAMIKO_HOST_KEY_AUTO_ADD environment variables
- Add additional paramiko connection settings (look_for_keys, strict_host_key_checking, record_host_keys)

### v2.1.28
- Added 10 default XML configurations:
  - VLAN Creation
  - Access Port
  - Trunk Port
  - L3 Interface IP
  - Static Route
  - Banner MOTD
  - User Account
  - NTP Server
  - DNS Configuration
  - SNMP Configuration

### v2.1.27
- Fix XML configs - ios_l2_interfaces for trunk, ios_l3_interfaces for IP

### v2.1.26
- Separate history/configs, add nc connectivity test, netcat installed

### v2.1.25
- Add default equipment and sample config for testing

### v2.1.24
- Show deployments (history_) in Mes configs section

### v2.1.23
- Fix config loading - handle raw XML format and null element errors

### v2.1.22
- Debug saved configs loading and fixing config modification

### v2.1.21
- Fix template button click - add pointer-events-none to Lucide icons

### v2.1.20
- Fix ios_interfaces state - use merged instead of present

### v2.1.19
- Improve Ansible error messages and handle BrokenPipe

### v2.1.18
- Fix multi-equipment XML wrapper orphan vlan bug

### v2.1.17
- Fix paramiko host key verification for SSH connections

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

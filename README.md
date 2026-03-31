# NetDeploy - Gestionnaire de Configuration Réseau

![Version](https://img.shields.io/badge/version-2.1-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**NetDeploy** est une application web moderne pour gérer et déployer des configurations réseau sur vos équipements (routeurs, switches, firewalls) de manière intuitive et automatisée. L'utilisateur crée des configurations XML qui sont automatiquement converties en playbooks Ansible en arrière-plan.

## Table des matières

1. [Fonctionnalités](#fonctionnalités)
2. [Architecture](#architecture)
3. [Déploiement](#déploiement)
4. [Format des Templates XML](#format-des-templates-xml)
5. [Prérequis Réseau](#prérequis-réseau)
6. [Structure du Projet](#structure-du-projet)
7. [API Endpoints](#api-endpoints)
8. [Sécurité](#sécurité)
9. [Licence](#licence)

---

## Fonctionnalités

### Dashboard
- Vue d'ensemble des équipements réseau
- Statut en temps réel (en ligne / hors ligne)
- Indicateurs clés : nombre d'équipements, déploiements réussis/échoués
- Historique des derniers déploiements

### Gestion des Équipements
- Ajout, modification et suppression d'équipements
- Support multi-constructeurs : Cisco, Juniper, Aruba, Fortinet
- Test de connectivité en un clic
- Champs : nom, IP, type, OS, port NETCONF, credentials

### Éditeur XML NETCONF
- Éditeur de code avec coloration syntaxique
- Templates prédéfinis par constructeur et type de configuration
- Validation XML en temps réel
- Sauvegarde et gestion des templates

### Déploiement
- Sélection multi-équipements
- Association template XML
- Confirmation avant déploiement
- Suivi en temps réel (barre de progression, logs)
- Statut par équipement (succès / échec)

### Historique
- Liste complète des déploiements
- Détails : équipements, template, date, statut
- Redéploiement en 1 clic

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (index.html)                     │
│                 HTML + TailwindCSS + CodeMirror                   │
│                  Single-Page Application JavaScript                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP POST /api/deploy
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend Python (server.py)                     │
│              HTTP Server + XML Parser + Ansible Runner            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Ansible (transparent)                         │
│      Playbooks générés dynamiquement → Exécution SSH             │
│      Collections: cisco.ios, arista.eos, cisco.nxos             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Équipements Réseau                             │
│     Cisco IOS-XE │ Juniper JunOS │ Aruba EOS │ FortiOS           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Déploiement

### Option 1 : Docker (Recommandé)

```bash
# Cloner le repo
git clone git@github.com:desko12/netdeploy.git
cd netdeploy

# Démarrer avec Docker Compose
docker compose up -d

# L'application est accessible sur http://localhost:3000
```

### Option 2 : Python Direct

```bash
# Cloner le repo
git clone git@github.com:desko12/netdeploy.git
cd netdeploy

# Installer les dépendances Python
pip install ansible pyyaml paramiko

# Installer les collections Ansible (optionnel)
ansible-galaxy collection install cisco.ios arista.eos cisco.nxos

# Lancer le serveur
python3 server.py
```

### Option 3 : Backend FastAPI (NETCONF)

Pour utiliser le backend NETCONF complet avec ncclient :

```bash
# Cloner le repo
git clone git@github.com:desko12/netdeploy.git
cd netdeploy

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### URLs d'accès

| Service | URL |
|---------|-----|
| Interface Web (Ansible) | http://localhost:3000 |
| Interface Web (FastAPI) | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

## Format des Templates XML

### Configuration VLAN (Cisco IOS-XE)

```xml
<config target="router-01" host="192.168.1.1" os="ios" user="admin" password="password">
  <vlan id="100">
    <name>CLIENT_VLAN</name>
    <state>present</state>
  </vlan>
</config>
```

### Configuration Interface

```xml
<config target="switch-01" host="192.168.1.10" os="ios" user="admin" password="password">
  <interface name="GigabitEthernet0/0">
    <description>Uplink to Core</description>
    <ip>10.0.0.1</ip>
    <mask>255.255.255.0</mask>
    <enabled>true</enabled>
  </interface>
</config>
```

### Configuration BGP

```xml
<config target="router-01" host="192.168.1.1" os="ios" user="admin" password="password">
  <bgp as="65001">
    <neighbor ip="192.168.1.2" remote-as="65002">
      <description>Peer EBGP</description>
    </neighbor>
  </bgp>
</config>
```

### Configuration OSPF

```xml
<config target="router-01" host="192.168.1.1" os="ios" user="admin" password="password">
  <ospf process-id="1">
    <area id="0">
      <network>10.0.0.0</network>
      <wildcard>0.0.0.255</wildcard>
    </area>
  </ospf>
</config>
```

---

## Prérequis Réseau

- Les équipements doivent avoir **NETCONF** ou **SSH** activé
- Les credentials (username/password) doivent avoir les droits nécessaires
- Le serveur doit pouvoir atteindre les équipements sur le réseau

### Cisco IOS-XE

```ios
! Activer NETCONF
configure terminal
netconf-yang
end
write memory
```

### Juniper JunOS

```bash
set system services netconf ssh
```

---

## Structure du Projet

```
netdeploy/
├── index.html              # Frontend complet (single-page app)
├── server.py               # Backend HTTP + XML Parser + Ansible
├── Dockerfile              # Image Docker
├── docker-compose.yml      # Orchestration Docker
├── requirements.txt        # Dépendances Python (FastAPI)
├── README.md               # Ce fichier
├── AGENTS.md               # Instructions pour agents IA
├── SPEC.md                 # Spécifications techniques
│
├── app/                    # Application FastAPI principale
│   ├── main.py            # Point d'entrée FastAPI
│   ├── config.py          # Configuration
│   ├── models/
│   │   ├── database.py    # Modèles SQLAlchemy
│   │   ├── schemas.py     # Schémas Pydantic
│   │   └── db_session.py  # Session base de données
│   ├── routers/
│   │   ├── routers.py      # API inventaire routeurs
│   │   ├── vlans.py       # API configuration VLANs
│   │   ├── interfaces.py   # API configuration interfaces
│   │   ├── routing.py      # API BGP/OSPF
│   │   ├── config_logs.py # API historique
│   │   └── web.py         # Routes interface web
│   ├── services/
│   │   ├── netconf_client.py   # Client NETCONF (ncclient)
│   │   └── config_builder.py   # Générateur XML YANG
│   └── templates/         # Templates Jinja2
│
└── netdeploy_backend/      # Backend Ansible alternatif
    ├── main.py
    └── Dockerfile
```

---

## API Endpoints

### Backend FastAPI

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/routers` | Liste des routeurs |
| POST | `/api/routers` | Ajouter un routeur |
| GET | `/api/routers/{id}` | Détail d'un routeur |
| POST | `/api/routers/{id}/test` | Tester connexion NETCONF |
| POST | `/api/routers/{id}/ping` | Ping routeur |
| POST | `/api/routers/{id}/vlans` | Créer un VLAN |
| POST | `/api/vlans/{id}/apply` | Appliquer VLAN au routeur |

### Backend Ansible

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Interface Web |
| POST | `/api/deploy` | Déployer une configuration XML |

### Exemples curl

```bash
# Ajouter un routeur (FastAPI)
curl -X POST http://localhost:8000/api/routers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Routeur-Paris",
    "ip_address": "192.168.1.1",
    "username": "admin",
    "password": "motdepasse",
    "netconf_port": 830
  }'

# Tester connexion
curl -X POST http://localhost:8000/api/routers/1/test

# Créer un VLAN
curl -X POST http://localhost:8000/api/routers/1/vlans \
  -H "Content-Type: application/json" \
  -d '{"vlan_id": 100, "name": "CLIENT-FINANCE"}'

# Appliquer le VLAN
curl -X POST http://localhost:8000/api/vlans/1/apply
```

---

## Sécurité

### Recommandations

1. **HTTPS** : Utiliser un reverse proxy (nginx, traefik) avec SSL en production
2. **Credentials** : Ne pas stocker les mots de passe en clair
3. **Réseau** : Isoler l'application dans un réseau sécurisé
4. **Accès** : Ajouter une authentification (optionnel)
5. **Firewall** : Limiter l'accès aux équipements réseau uniquement

### Configuration HTTPS avec Nginx

```nginx
server {
    listen 443 ssl;
    server_name netdeploy.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Licence

MIT License - Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## Support

Pour signaler un bug ou demander de l'aide, ouvrez une issue sur GitHub.

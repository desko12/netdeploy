# NetDeploy v2.1 - Documentation d'Exploitation

## Table des Matières

1. [Présentation](#présentation)
2. [Architecture](#architecture)
3. [Installation et Démarrage](#installation-et-démarrage)
4. [Interface Utilisateur](#interface-utilisateur)
5. [Gestion des Équipements](#gestion-des-équipements)
6. [Gestion des Configurations](#gestion-des-configurations)
7. [Déploiement de Configurations](#déploiement-de-configurations)
8. [Historique des Déploiements](#historique-des-déploiements)
9. [Monitoring et Logs](#monitoring-et-logs)
10. [Configuration XML](#configuration-xml)
11. [API Backend](#api-backend)
12. [Dépannage](#dépannage)

---

## 1. Présentation

**NetDeploy** est une application web de gestion et déploiement de configurations réseau. Elle permet de:

- Gérer un parc d'équipements réseau (routeurs, switches Cisco)
- Stocker des configurations XML paramétrables
- Déployer des configurations sur un ou plusieurs équipements via Ansible
- Suivre l'historique des déploiements
- Monitorer l'état de connectivity des équipements

### Fonctionnalités Principales

| Fonctionnalité | Description |
|----------------|-------------|
| Gestion des équipements | Ajout, modification, suppression d'équipements réseau |
| Configurations templates | 10 configurations par défaut (VLAN, ports, routes, etc.) |
| Éditeur XML | Validation syntaxique en temps réel |
| Déploiement Ansible | Génération et exécution automatique de playbooks |
| Historique | Journal complet des déploiements |
| Monitoring | Test de connectivité SSH/NETCONF |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (SPA)                          │
│                    index.html + TailwindCSS                      │
│                   CodeMirror (Éditeur XML)                      │
└────────────────────────────┬────────────────────────────────────┘
                           │ HTTP/JSON
┌────────────────────────────▼────────────────────────────────────┐
│                      Backend (Python)                           │
│                    server.py (HTTP Server)                      │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐ │
│  │ parse_xml()  │generate_play │ run_ansible  │   logs     │ │
│  │              │    book()    │ _playbook()   │            │ │
│  └──────┬───────┴──────────────┴──────────────┴────────────┘ │
└─────────┼─────────────────────────────────────────────────────┘
          │ Ansible Playbooks
┌─────────▼─────────────────────────────────────────────────────┐
│                    Équipements Réseau                         │
│              (Cisco IOS/IOS-XE via SSH/NETCONF)               │
└─────────────────────────────────────────────────────────────────┘
```

### Stack Technique

| Composant | Technologie |
|-----------|-------------|
| Frontend | HTML5, JavaScript vanilla, TailwindCSS |
| Éditeur | CodeMirror 5 |
| Backend | Python 3, HTTP Server intégré |
| Déploiement | Ansible, collection cisco.ios |
| Transport | SSH (paramiko/network_cli) |

---

## 3. Installation et Démarrage

### Prérequis

- Docker et Docker Compose
- Python 3.12+ (pour exécution directe)
- Ansible (dans le container ou sur l'hôte)
- Connectivité réseau vers les équipements

### Démarrage avec Docker

```bash
# Cloner le repository
git clone https://github.com/desko12/netdeploy.git
cd netdeploy

# Démarrer l'application
docker compose up -d

# Vérifier le statut
docker compose ps

# Voir les logs
docker compose logs -f app
```

### Démarrage Direct

```bash
# Installer les dépendances
pip install pyyaml

# Lancer le serveur
python server.py

# L'application est accessible sur http://localhost:3000
```

### Ports

| Port | Service | Description |
|------|---------|-------------|
| 3000 | HTTP | Interface web NetDeploy |
| 22 | SSH | Connexion aux équipements réseau |

---

## 4. Interface Utilisateur

### Navigation

L'interface est structurée en sections accessibles via le menu latéral:

```
┌──────────────────────────────────────────────────────────┐
│  ☰ NetDeploy                              [●] Déconnecté │
├──────────┬───────────────────────────────────────────────┤
│          │                                               │
│ 📊 Tableau│          CONTENU PRINCIPAL                   │
│    de bord│                                               │
│          │                                               │
│ 🖥️ Équipements│                                          │
│          │                                               │
│ 📋 Configs│                                             │
│          │                                               │
│ 📜 Historique│                                            │
│          │                                               │
│ 📝 Logs   │                                               │
│          │                                               │
└──────────┴───────────────────────────────────────────────┘
```

### Tableau de Bord

Le tableau de bord affiche:

- **Nombre total d'équipements**
- **Nombre de déploiements réussis** (vert)
- **Nombre de déploiements échoués** (rouge)
- **Liste des équipements** avec indicateur de statut (en ligne/hors ligne)

---

## 5. Gestion des Équipements

### Ajout d'un Équipement

1. Cliquer sur **"Ajouter un équipement"** dans la section Équipements
2. Remplir le formulaire:

| Champ | Description | Obligatoire |
|-------|-------------|-------------|
| Nom | Nom de l'équipement | Oui |
| IP | Adresse IP de gestion | Oui |
| OS | Système d'exploitation (ios/nxos/eos) | Oui |
| Port | Port SSH (défaut: 22) | Non |
| Username | Nom d'utilisateur SSH | Oui |
| Password | Mot de passe SSH | Oui |

3. Cliquer sur **"Ajouter"**

### Modification

1. Cliquer sur l'icône ✏️ de l'équipement
2. Modifier les champs nécessaires
3. Cliquer sur **"Enregistrer"**

### Suppression

1. Cliquer sur l'icône 🗑️ de l'équipement
2. Confirmer la suppression

### Test de Connectivité

- Cliquer sur l'icône 🔌 pour tester la connexion
- Le statut est mis à jour (en ligne/hors ligne)
- Ports testés: **22 (SSH)** et **830 (NETCONF)**

### États de Connectivité

| État | Description |
|------|-------------|
| 🟢 Connecté | Au moins un port (22 ou 830) répond |
| 🔴 Hors ligne | Aucun port ne répond |
| ⚠️ Auth échouée | Connexion établie mais authentification refusée |

---

## 6. Gestion des Configurations

### Configurations par Défaut

L'application propose 16 configurations templates:

| # | Nom | Description |
|---|-----|-------------|
| 1 | VLAN Creation | Créer un VLAN sur un switch |
| 2 | Access Port | Configurer un port en mode access |
| 3 | Trunk Port | Configurer un port en mode trunk |
| 4 | L3 Interface IP | Assigner une IP à une interface L3 |
| 5 | Static Route | Ajouter une route statique |
| 6 | Banner MOTD | Définir une bannière de connexion |
| 7 | User Account | Créer un compte utilisateur local |
| 8 | NTP Server | Configurer les serveurs NTP |
| 9 | DNS Configuration | Configurer les serveurs DNS |
| 10 | SNMP Configuration | Configurer SNMP |
| 11 | NAT/PAT Configuration | Configurer NAT/PAT (routeurs uniquement) |
| 12 | Sub-Interface IOS | Créer une sous-interface sur IOS/IOS-XE |
| 13 | Sub-Interface NX-OS | Créer une sous-interface sur NX-OS |
| 14 | Sub-Interface EOS | Créer une sous-interface sur Arista EOS |
| 15 | Delete Sub-Interface IOS | Supprimer une sous-interface sur IOS/IOS-XE |
| 16 | Delete Sub-Interface NX-OS | Supprimer une sous-interface sur NX-OS |
| 17 | Delete Sub-Interface EOS | Supprimer une sous-interface sur Arista EOS |

### Création d'une Configuration

1. Se rendre dans la section **"Mes Configurations"**
2. Cliquer sur **"Nouvelle Configuration"**
3. Choisir un **template** ou partir de zéro
4. Modifier le XML selon les besoins
5. Donner un **nom** à la configuration
6. Cliquer sur **"Sauvegarder"**

### Modification

1. Cliquer sur une configuration dans la liste
2. Modifier le XML dans l'éditeur
3. Cliquer sur **"Mettre à jour"**

### Suppression

1. Cliquer sur l'icône 🗑️ de la configuration
2. Confirmer la suppression

---

## 7. Déploiement de Configurations

### Processus de Déploiement

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Sélection  │───▶│  Injection  │───▶│ Génération  │───▶│  Exécution  │
│ équipements │    │    XML      │    │  Ansible    │    │  Ansible    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Étapes de Déploiement

#### Étape 1: Sélection des Équipements

1. Cocher un ou plusieurs équipements dans la liste
2. Les équipements sélectionnés apparaissent dans la section "Configuration à déployer"

#### Étape 2: Choix de la Configuration

1. Sélectionner une configuration dans la liste déroulante
2. L'éditeur XML affiche le contenu
3. Modifier si nécessaire

#### Étape 3: Déploiement

1. Cliquer sur **"Déployer la Configuration"**
2. Le système:
   - Injecte les données d'équipement dans le XML
   - Génère le playbook Ansible
   - Exécute le déploiement
   - Affiche le résultat en temps réel

### Déploiement Multi-Équipements

- Sélectionner plusieurs équipements
- Chaque équipement reçoit une configuration personnalisée
- Les déploiements s'exécutent en parallèle
- Les résultats sont affichés individuellement

### Validation XML

L'éditeur valide le XML en temps réel:
- ✅ XML valide: bouton "Déployer" actif
- ❌ XML invalide: message d'erreur affiché

---

## 8. Historique des Déploiements

### Consultation

1. Se rendre dans la section **"Historique"**
2. La liste affiche:
   - Date et heure
   - Équipement cible
   - Nom de la configuration
   - Statut (succès/échec)

### Détails d'un Déploiement

Cliquer sur un déploiement pour voir:
- Configuration XML utilisée
- Sortie Ansible complète
- Logs d'exécution
- Horodatage

### Re-déploiement

1. Ouvrir un déploiement historique
2. Cliquer sur **"Re-déployer"**
3. Le déploiement est relancé avec les mêmes paramètres

---

## 9. Monitoring et Logs

### Logs en Temps Réel

La section **"Logs"** affiche:
- Messages INFO (informations)
- Messages WARNING (avertissements)
- Messages ERROR (erreurs)
- Horodatage de chaque entrée

### API Logs

```bash
# Consulter les logs via API
curl http://localhost:3000/api/logs
```

### Test de Connectivité API

```bash
# Ping un équipement
curl "http://localhost:3000/api/ping?ip=10.10.10.2"

# Réponse
{
  "host": "10.10.10.2",
  "ports": {"22": "open", "830": "open"},
  "online": true
}
```

---

## 10. Configuration XML

### Format XML

```xml
<configurations>
  <config 
    target="SwMgnt" 
    host="10.10.10.2" 
    os="ios" 
    user="desko" 
    password="desko">
    
    <!-- Élément de configuration -->
    <element>
      <!-- Paramètres -->
    </element>
    
  </config>
</configurations>
```

### Attributs de `<config>`

| Attribut | Description | Exemple |
|----------|-------------|---------|
| target | Nom de l'équipement | SwMgnt |
| host | IP de gestion | 10.10.10.2 |
| os | OS (ios/nxos/eos) | ios |
| user | Username SSH | desko |
| password | Mot de passe SSH | desko |

### Éléments de Configuration

#### VLAN

```xml
<vlan id="100">
  <name>CLIENT_VLAN</name>
</vlan>
```

#### Interface Access

```xml
<interface name="GigabitEthernet0/1" mode="access">
  <description>Port Client</description>
  <vlan>100</vlan>
  <enabled>true</enabled>
</interface>
```

#### Interface Trunk

```xml
<interface name="GigabitEthernet0/24" mode="trunk">
  <description>Uplink to Core</description>
  <allowed-vlans>10,20,30,100</allowed-vlans>
  <native-vlan>10</native-vlan>
  <enabled>true</enabled>
</interface>
```

#### Interface L3 avec IP

```xml
<interface name="GigabitEthernet0/0">
  <description>WAN Interface</description>
  <ip>10.0.0.1</ip>
  <mask>255.255.255.0</mask>
  <enabled>true</enabled>
  <no-shutdown/>
</interface>
```

#### Sous-Interface (Sub-Interface)

```xml
<subinterface name="GigabitEthernet0/0" vlan="10">
  <description>Sub-interface VLAN 10</description>
  <ip>192.168.10.1</ip>
  <mask>255.255.255.0</mask>
  <enabled>true</enabled>
</subinterface>
```

**Attributs de `<subinterface>`:**

| Attribut | Description | Exemple |
|----------|-------------|---------|
| name | Nom de l'interface parent | GigabitEthernet0/0 |
| vlan | ID du VLAN (encapsulation) | 10 |

**Éléments enfants:**

| Élément | Description |
|---------|-------------|
| description | Description de la sous-interface |
| ip | Adresse IP |
| mask | Masque de sous-réseau |
| enabled | true/false pour no shutdown |

#### Supprimer une Sous-Interface (Delete Sub-Interface)

```xml
<delete-subinterface name="GigabitEthernet0/0.10"/>
```

**Attributs de `<delete-subinterface>`:**

| Attribut | Description | Exemple |
|----------|-------------|---------|
| name | Nom complet de la sous-interface | GigabitEthernet0/0.10 |

**Commande générée:** `no interface GigabitEthernet0/0.10`

#### Route Statique

```xml
<static-route>
  <network>192.168.100.0</network>
  <mask>255.255.255.0</mask>
  <next-hop>10.10.10.254</next-hop>
</static-route>
```

#### Banner MOTD

```xml
<banner>
  <motd>===== AUTHORIZED ACCESS ONLY =====</motd>
</banner>
```

#### Utilisateur Local

```xml
<user>
  <name>netadmin</name>
  <password>SecurePass123</password>
  <privilege>15</privilege>
</user>
```

#### NTP

```xml
<ntp>
  <server>0.fr.pool.ntp.org</server>
  <server>1.fr.pool.ntp.org</server>
</ntp>
```

#### DNS

```xml
<dns>
  <server>8.8.8.8</server>
  <server>1.1.1.1</server>
  <domain>local.network</domain>
</dns>
```

#### SNMP

```xml
<snmp>
  <community name="public" permission="ro"/>
  <community name="private" permission="rw"/>
  <location>DataCenter Rack-01</location>
  <contact>admin@network.local</contact>
</snmp>
```

#### NAT/PAT

```xml
<nat>
  <inside-interface>GigabitEthernet0/0</inside-interface>
  <outside-interface>GigabitEthernet0/1</outside-interface>
  <acl>1</acl>
</nat>
```

> **Note**: NAT nécessite un routeur ou switch L3. Ne fonctionne pas sur switches L2.

---

## 11. API Backend

### Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Interface web |
| GET | `/api/health` | Vérification santé |
| GET | `/api/logs` | Liste des logs |
| POST | `/api/deploy` | Déployer une configuration |
| POST | `/api/logs/clear` | Effacer les logs |
| GET | `/api/ping?ip=X` | Tester connectivité |

### Déploiement via API

```bash
curl -X POST http://localhost:3000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "config": "<configurations><config os=\"ios\" host=\"10.10.10.2\" target=\"SwMgnt\" user=\"desko\" password=\"desko\"><vlan id=\"100\"><name>TEST</name></vlan></config></configurations>"
  }'
```

### Réponse

```json
{
  "success": true,
  "output": "PLAY [Network Configuration Deployment]...",
  "logs": []
}
```

### Codes d'Erreur

| Code | Message | Cause |
|------|---------|-------|
| 400 | No config provided | XML manquant |
| 400 | Invalid XML | XML malformé |
| 400 | No valid config elements found | Aucun élément valide |
| 500 | Deployment timeout | Timeout (5 minutes) |

---

## 12. Dépannage

### Problèmes Courants

#### "No authentication methods available"

**Cause**: Credentials SSH non passés correctement à Ansible

**Solution**: Vérifier que les attributs `user` et `password` sont dans le XML:
```xml
<config user="desko" password="desko" ...>
```

#### "Authentication failed"

**Cause**: Mauvais identifiants

**Solution**: Vérifier username/password dans l'équipement

#### "Command timeout"

**Cause**: L'équipement ne répond pas ou commande trop longue

**Solution**: 
- Vérifier la connectivité réseau
- Augmenter le timeout dans `ansible.cfg`

#### "Incomplete command"

**Cause**: Commande IOS invalide

**Solution**: Vérifier la syntaxe de la configuration XML

### Logs Serveur

```bash
# Voir les logs en direct
docker compose logs -f app

# Consulter les logs Ansible
cat /tmp/netdeploy/deploy.yml
cat /tmp/netdeploy/inventory.json
```

### Vérification Ansible

```bash
# Tester manuellement une connexion
ansible all -i inventory.json -m ping -u desko -k

# Exécuter un playbook manuellement
ansible-playbook -i inventory.json playbook.yml -u desko -k -v
```

---

## Annexe: Versions

| Version | Date | Description |
|---------|------|-------------|
| v2.1.35 | 2026-04-02 | Ajout suppression sous-interfaces (IOS/NX-OS/EOS) |
| v2.1.34 | 2026-04-02 | Ajout configuration sous-interfaces (IOS/NX-OS/EOS) |
| v2.1.33 | 2026-04-02 | Corrections handler user et parser SNMP |
| v2.1.32 | 2026-04-02 | Correction ios_l2_interfaces pour trunk |
| v2.1.31 | 2026-04-02 | Corrections handlers NTP/DNS/SNMP/User |
| v2.1.30 | 2026-04-02 | Ajout handlers pour banner/user/ntp/dns/snmp |
| v2.1.29 | 2026-04-02 | Correction host key verification |
| v2.1.28 | 2026-04-02 | 10 configurations XML par défaut |

---

*Document mis à jour le 2026-04-02*

# Configurations Lab - NetDeploy

Ce dossier contient des configurations réseau prédéfinies prêtes à être déployées.

## Fichiers disponibles

| Fichier | Description | Complexité |
|---------|-------------|------------|
| `soho-lab.xml` | Petit bureau - 1 routeur + 2 switches, 3 VLANs | Débutant |
| `site-paris.md` | Documentation - Site Paris avec documentation | Guide |
| `datacenter-lab.xml` | Datacenter - Core switches + EtherChannel + HSRP | Avancé |
| `campus-lab.xml` | Campus multi-bâtiment - Building A & B | Intermédiaire |
| `wan-l3vpn-lab.xml` | WAN L3VPN - Multi-sites (Paris, Lyon, Marseille) | Expert |

## Utilisation

1. Ouvrir le fichier XML souhaité
2. Modifier les IPs, credentials et VLANs selon votre infrastructure
3. Copier le contenu dans l'éditeur NetDeploy
4. Déployer sur les équipements cibles

## Topologies

### SOHO Lab
```
Internet → SOHO-Router → Distribution-SW-01/SW-02
                    ↓
              VLAN 10 (MGMT)
              VLAN 20 (DATA)  
              VLAN 30 (GUEST)
```

### Campus Lab
```
                    ┌──────────────┐
                    │ Campus-Core  │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              ↓                         ↓
        ┌─────┴─────┐             ┌─────┴─────┐
        │  Dist-A   │             │  Dist-B   │
        │ Building A │             │ Building B │
        └─────┬─────┘             └─────┬─────┘
              ↓                         ↓
         VLAN 10-50                 VLAN 10-50
```

### WAN L3VPN
```
    Paris                Lyon               Marseille
   ┌──────┐           ┌──────┐           ┌──────┐
   │  PE  │◄────────►│  PE  │◄────────►│  PE  │
   └──┬───┘           └──┬───┘           └──┬───┘
      │                    │                    │
      ▼                    ▼                    ▼
   ┌──────┐           ┌──────┐           ┌──────┐
   │  CE  │           │  CE  │           │  CE  │
   └──────┘           └──────┘           └──────┘
```

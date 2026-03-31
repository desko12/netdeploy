---
title: Configuration Lab - Site Paris
description: Configuration VLAN et routing pour le site de Paris
author: NetDeploy
version: 1.0
---

# Configuration Lab - Site Paris

## Équipements
- Core-Router-01 (192.168.1.1) - Cisco ISR 4331
- Distribution-SW-01 (192.168.1.10) - Cisco Catalyst 2960
- Distribution-SW-02 (192.168.1.11) - Cisco Catalyst 2960

## VLANs

### VLAN 10 - Management
```
VLAN 10 - MGMT
IP: 10.10.10.0/24
```

### VLAN 20 - Data
```
VLAN 20 - DATA
IP: 10.20.20.0/24
```

### VLAN 30 - Voix
```
VLAN 30 - VOICE
IP: 10.30.30.0/24
```

## Configuration XML

```xml
<!-- Core Router -->
<config target="Core-Router-01" host="192.168.1.1" os="ios" user="admin" password="cisco123">
  <vlan id="10"><name>MGMT</name></vlan>
  <vlan id="20"><name>DATA</name></vlan>
  <vlan id="30"><name>VOICE</name></vlan>
  <interface name="GigabitEthernet0/0">
    <description>WAN Interface</description>
    <ip>192.168.1.1</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <bgp as="65001">
    <router-id>192.168.1.1</router-id>
    <neighbor ip="192.168.1.2" remote-as="65002">
      <description>ISP Peer</description>
    </neighbor>
  </bgp>
</config>

<!-- Distribution Switch 1 -->
<config target="Distribution-SW-01" host="192.168.1.10" os="ios" user="admin" password="cisco123">
  <vlan id="10"><name>MGMT</name></vlan>
  <vlan id="20"><name>DATA</name></vlan>
  <vlan id="30"><name>VOICE</name></vlan>
  <interface name="GigabitEthernet0/1" mode="trunk">
    <description>Uplink to Core</description>
    <allowed-vlans>10,20,30</allowed-vlans>
  </interface>
</config>

<!-- Distribution Switch 2 -->
<config target="Distribution-SW-02" host="192.168.1.11" os="ios" user="admin" password="cisco123">
  <vlan id="10"><name>MGMT</name></vlan>
  <vlan id="20"><name>DATA</name></vlan>
  <vlan id="30"><name>VOICE</name></vlan>
  <interface name="GigabitEthernet0/1" mode="trunk">
    <description>Uplink to Core</description>
    <allowed-vlans>10,20,30</allowed-vlans>
  </interface>
</config>
```

## Schéma Réseau

```
                    ┌─────────────────┐
                    │   INTERNET       │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │  Core-Router-01  │
                    │  192.168.1.1    │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
    ┌─────────┴─────────┐       ┌─────────┴─────────┐
    │ Distribution-SW-01│       │ Distribution-SW-02│
    │ 192.168.1.10     │       │ 192.168.1.11     │
    └─────────┬─────────┘       └─────────┬─────────┘
              │                             │
    VLAN 10 (MGMT)              VLAN 10 (MGMT)
    VLAN 20 (DATA)              VLAN 20 (DATA)
    VLAN 30 (VOICE)              VLAN 30 (VOICE)
```

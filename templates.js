// Templates Database - NetDeploy v2.1
const templatesDB = [
    // ==================== CISCO ====================
    {
        id: 'cisco_vlan_basic',
        name: 'Cisco - VLAN Simple',
        vendor: 'cisco',
        category: 'vlan',
        description: 'Créer un VLAN basique sur un switch Cisco IOS-XE',
        icon: 'layers',
        xml: `<config target="switch-01" host="192.168.1.10" os="ios" user="admin" password="password">
  <vlan id="100">
    <name>CLIENT_VLAN</name>
  </vlan>
</config>`
    },
    {
        id: 'cisco_vlan_full',
        name: 'Cisco - VLAN avec Interface',
        vendor: 'cisco',
        category: 'vlan',
        description: 'Créer un VLAN et l\'assigner à une interface access',
        icon: 'layers',
        xml: `<config target="switch-01" host="192.168.1.10" os="ios" user="admin" password="password">
  <vlan id="100">
    <name>CLIENT_VLAN</name>
  </vlan>
  <interface name="GigabitEthernet0/1" mode="access">
    <description>Port Client</description>
    <vlan>100</vlan>
    <enabled>true</enabled>
  </interface>
</config>`
    },
    {
        id: 'cisco_interface',
        name: 'Cisco - Interface L3',
        vendor: 'cisco',
        category: 'interface',
        description: 'Configurer une interface Layer 3 avec IP',
        icon: 'network',
        xml: `<config target="router-01" host="192.168.1.1" os="ios" user="admin" password="password">
  <interface name="GigabitEthernet0/0">
    <description>WAN Interface</description>
    <ip>10.0.0.1</ip>
    <mask>255.255.255.0</mask>
    <enabled>true</enabled>
    <no-shutdown/>
  </interface>
</config>`
    },
    {
        id: 'cisco_trunk',
        name: 'Cisco - Port Trunk',
        vendor: 'cisco',
        category: 'interface',
        description: 'Configurer un port en mode trunk avec VLANs',
        icon: 'git-branch',
        xml: `<config target="switch-01" host="192.168.1.10" os="ios" user="admin" password="password">
  <interface name="GigabitEthernet0/24" mode="trunk">
    <description>Uplink to Core</description>
    <allowed-vlans>10,20,30,100</allowed-vlans>
    <native-vlan>10</native-vlan>
    <enabled>true</enabled>
  </interface>
</config>`
    },
    {
        id: 'cisco_bgp',
        name: 'Cisco - BGP Peer',
        vendor: 'cisco',
        category: 'routing',
        description: 'Configurer un neighbor BGP eBGP',
        icon: 'globe',
        xml: `<config target="router-01" host="192.168.1.1" os="ios" user="admin" password="password">
  <bgp as="65001">
    <router-id>10.0.0.1</router-id>
    <neighbor ip="192.168.1.2" remote-as="65002">
      <description>Peer EBGP</description>
    </neighbor>
  </bgp>
</config>`
    },
    {
        id: 'cisco_ospf',
        name: 'Cisco - OSPF Area',
        vendor: 'cisco',
        category: 'routing',
        description: 'Configurer OSPF sur une aire',
        icon: 'share-2',
        xml: `<config target="router-01" host="192.168.1.1" os="ios" user="admin" password="password">
  <ospf process-id="1" router-id="10.0.0.1">
    <area id="0">
      <network>10.0.0.0</network>
      <wildcard>0.0.0.255</wildcard>
    </area>
    <area id="1">
      <network>172.16.0.0</network>
      <wildcard>0.0.255.255</wildcard>
    </area>
  </ospf>
</config>`
    },
    {
        id: 'cisco_acl',
        name: 'Cisco - ACL Standard',
        vendor: 'cisco',
        category: 'security',
        description: 'Créer une ACL standard pour filtrer le trafic',
        icon: 'shield',
        xml: `<config target="router-01" host="192.168.1.1" os="ios" user="admin" password="password">
  <acl name="ACL_BLOCK_HOST">
    <rule direction="in">
      <action>deny</action>
      <source>192.168.100.50</source>
      <wildcard>0.0.0.0</wildcard>
    </rule>
    <rule direction="in">
      <action>permit</action>
      <source>192.168.0.0</source>
      <wildcard>0.0.255.255</wildcard>
    </rule>
  </acl>
</config>`
    },
    {
        id: 'cisco_static_route',
        name: 'Cisco - Route Statique',
        vendor: 'cisco',
        category: 'routing',
        description: 'Ajouter une route statique',
        icon: 'route',
        xml: `<config target="router-01" host="192.168.1.1" os="ios" user="admin" password="password">
  <static-route>
    <network>10.10.0.0</network>
    <mask>255.255.0.0</mask>
    <next-hop>192.168.1.254</next-hop>
    <distance>1</distance>
  </static-route>
</config>`
    },
    {
        id: 'cisco_hsrp',
        name: 'Cisco - HSRP',
        vendor: 'cisco',
        category: 'redundancy',
        description: 'Configurer HSRP pour la redondance de passerelle',
        icon: 'heart-handshake',
        xml: `<config target="router-01" host="192.168.1.1" os="ios" user="admin" password="password">
  <interface name="GigabitEthernet0/0">
    <hsrp>
      <group>10</group>
      <priority>110</priority>
      <ip>192.168.1.254</ip>
      <preempt/>
    </hsrp>
  </interface>
</config>`
    },
    {
        id: 'cisco_etherchannel',
        name: 'Cisco - EtherChannel',
        vendor: 'cisco',
        category: 'interface',
        description: 'Configurer un port-channel LACP',
        icon: 'cable',
        xml: `<config target="switch-01" host="192.168.1.10" os="ios" user="admin" password="password">
  <interface name="Port-channel1">
    <description>Port-Channel to Core</description>
    <mode>layer3</mode>
    <ip>10.1.1.1</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <interface name="GigabitEthernet0/1" channel-group="1" mode="active">
    <description>Member Port 1</description>
  </interface>
  <interface name="GigabitEthernet0/2" channel-group="1" mode="active">
    <description>Member Port 2</description>
  </interface>
</config>`
    },

    // ==================== JUNIPER ====================
    {
        id: 'juniper_vlan',
        name: 'Juniper - VLAN',
        vendor: 'juniper',
        category: 'vlan',
        description: 'Créer un VLAN sur Juniper EX',
        icon: 'layers',
        xml: `<config target="switch-01" host="192.168.2.1" os="junos" user="admin" password="password">
  <vlan id="100">
    <name>DATA_VLAN</name>
    <description>Data Network VLAN</description>
    <vlan-id>100</vlan-id>
  </vlan>
</config>`
    },
    {
        id: 'juniper_interface',
        name: 'Juniper - Interface L3',
        vendor: 'juniper',
        category: 'interface',
        description: 'Configurer une interface avec IP sur Juniper',
        icon: 'network',
        xml: `<config target="router-01" host="192.168.2.1" os="junos" user="admin" password="password">
  <interface name="ge-0/0/0">
    <description>WAN Interface</description>
    <unit number="0">
      <family>
        <inet>
          <address>10.0.0.1/24</address>
        </inet>
      </family>
    </unit>
  </interface>
</config>`
    },
    {
        id: 'juniper_irb',
        name: 'Juniper - IRB Interface',
        vendor: 'juniper',
        category: 'interface',
        description: 'Configurer une interface IRB pour VLAN routing',
        icon: 'layers',
        xml: `<config target="switch-01" host="192.168.2.1" os="junos" user="admin" password="password">
  <irb>
    <unit id="100">
      <family>
        <inet>
          <address>192.168.100.1/24</address>
        </inet>
      </family>
    </unit>
  </irb>
  <vlan id="100">
    <name>DATA_VLAN</name>
    <l3-interface>irb.100</l3-interface>
  </vlan>
</config>`
    },
    {
        id: 'juniper_bgp',
        name: 'Juniper - BGP Peer',
        vendor: 'juniper',
        category: 'routing',
        description: 'Configurer un neighbor BGP sur JunOS',
        icon: 'globe',
        xml: `<config target="router-01" host="192.168.2.1" os="junos" user="admin" password="password">
  <protocols>
    <bgp>
      <group name="EBGP_PEERS">
        <type>external</type>
        <neighbor address="192.168.1.2">
          <description>EBGP Peer</description>
          <peer-as>65002</peer-as>
        </neighbor>
      </group>
    </bgp>
  </protocols>
</config>`
    },
    {
        id: 'juniper_ospf',
        name: 'Juniper - OSPF Area',
        vendor: 'juniper',
        category: 'routing',
        description: 'Configurer OSPF sur JunOS',
        icon: 'share-2',
        xml: `<config target="router-01" host="192.168.2.1" os="junos" user="admin" password="password">
  <protocols>
    <ospf>
      <area name="0.0.0.0">
        <interface name="ge-0/0/0.0"/>
        <interface name="lo0.0" passive="true"/>
      </area>
    </ospf>
  </protocols>
</config>`
    },
    {
        id: 'juniper_static_route',
        name: 'Juniper - Route Statique',
        vendor: 'juniper',
        category: 'routing',
        description: 'Ajouter une route statique sur JunOS',
        icon: 'route',
        xml: `<config target="router-01" host="192.168.2.1" os="junos" user="admin" password="password">
  <routing-options>
    <static-route>10.10.0.0/16</static-route>
      <next-hop>192.168.1.254</next-hop>
      <metric>10</metric>
  </routing-options>
</config>`
    },

    // ==================== ARUBA ====================
    {
        id: 'aruba_vlan',
        name: 'Aruba - VLAN',
        vendor: 'aruba',
        category: 'vlan',
        description: 'Créer un VLAN sur Aruba AOS-CX',
        icon: 'layers',
        xml: `<config target="switch-aruba" host="192.168.3.1" os="eos" user="admin" password="password">
  <vlan id="100">
    <name>CORP_VLAN</name>
    <description>Corporate Network</description>
  </vlan>
</config>`
    },
    {
        id: 'aruba_interface',
        name: 'Aruba - Interface avec VLAN',
        vendor: 'aruba',
        category: 'interface',
        description: 'Configurer une interface access ou trunk',
        icon: 'network',
        xml: `<config target="switch-aruba" host="192.168.3.1" os="eos" user="admin" password="password">
  <interface name="1/1/1" mode="access">
    <description>Server Port</description>
    <vlan-access>100</vlan-access>
    <enabled>true</enabled>
  </interface>
  <interface name="1/1/24" mode="trunk">
    <description>Uplink Core</description>
    <vlan-trunk>10,20,30,100</vlan-trunk>
    <vlan-native>10</vlan-native>
  </interface>
</config>`
    },
    {
        id: 'aruba_static_route',
        name: 'Aruba - Route Statique',
        vendor: 'aruba',
        category: 'routing',
        description: 'Ajouter une route statique sur Aruba',
        icon: 'route',
        xml: `<config target="switch-aruba" host="192.168.3.1" os="eos" user="admin" password="password">
  <ip-route>
    <ipv4-route>
      <destination>10.0.0.0/8</destination>
      <next-hop>192.168.3.254</next-hop>
    </ipv4-route>
  </ip-route>
</config>`
    },

    // ==================== FORTINET ====================
    {
        id: 'fortinet_interface',
        name: 'Fortinet - Interface',
        vendor: 'fortinet',
        category: 'interface',
        description: 'Configurer une interface FortiGate',
        icon: 'network',
        xml: `<config target="fortigate-01" host="192.168.4.1" os="fortios" user="admin" password="password">
  <system>
    <interface name="port1">
      <vdom>root</vdom>
      <ip>192.168.4.1 255.255.255.0</ip>
      <description>WAN Interface</description>
      <role>wan</role>
    </interface>
  </system>
</config>`
    },
    {
        id: 'fortinet_policy',
        name: 'Fortinet - Policy',
        vendor: 'fortinet',
        category: 'security',
        description: 'Créer une policy de firewall',
        icon: 'shield',
        xml: `<config target="fortigate-01" host="192.168.4.1" os="fortios" user="admin" password="password">
  <firewall>
    <policy>
      <name>Allow_LAN_WAN</name>
      <srcintf>internal</srcintf>
      <dstintf>wan1</dstintf>
      <srcaddr>all</srcaddr>
      <dstaddr>all</dstaddr>
      <action>accept</action>
      <schedule>always</schedule>
      <service>ALL</service>
    </policy>
  </firewall>
</config>`
    },
    {
        id: 'fortinet_static_route',
        name: 'Fortinet - Route Statique',
        vendor: 'fortinet',
        category: 'routing',
        description: 'Ajouter une route statique sur FortiGate',
        icon: 'route',
        xml: `<config target="fortigate-01" host="192.168.4.1" os="fortios" user="admin" password="password">
  <router>
    <static>
      <route>
        <dst>10.0.0.0 255.0.0.0</dst>
        <gateway>192.168.4.254</gateway>
        <device>port1</device>
      </route>
    </static>
  </router>
</config>`
    },

    // ==================== MIKROTIK ====================
    {
        id: 'mikrotik_vlan',
        name: 'MikroTik - VLAN',
        vendor: 'mikrotik',
        category: 'vlan',
        description: 'Créer un VLAN sur MikroTik',
        icon: 'layers',
        xml: `<config target="router-mikrotik" host="192.168.5.1" os="routeros" user="admin" password="password">
  <interface>
    <vlan>
      <name>vlan100</name>
      <interface>ether1</interface>
      <vlan-id>100</vlan-id>
    </vlan>
  </interface>
  <ip>
    <address>
      <address>192.168.100.1/24</address>
      <interface>vlan100</interface>
    </address>
  </ip>
</config>`
    },
    {
        id: 'mikrotik_firewall',
        name: 'MikroTik - Firewall',
        vendor: 'mikrotik',
        category: 'security',
        description: 'Ajouter une règle firewall',
        icon: 'shield',
        xml: `<config target="router-mikrotik" host="192.168.5.1" os="routeros" user="admin" password="password">
  <ip>
    <firewall>
      <filter>
        <rule>
          <chain>input</chain>
          <action>accept</action>
          <protocol>tcp</protocol>
          <dst-port>22,80,443</dst-port>
        </rule>
      </filter>
    </firewall>
  </ip>
</config>`
    },

    // ==================== PALO ALTO ====================
    {
        id: 'paloalto_interface',
        name: 'Palo Alto - Interface',
        vendor: 'paloalto',
        category: 'interface',
        description: 'Configurer une interface sur Palo Alto',
        icon: 'network',
        xml: `<config target="fw-paloalto" host="192.168.6.1" os="panos" user="admin" password="password">
  <devices>
    <entry name="localhost.localdomain">
      <network>
        <interfaces>
          <entry name="ethernet1/1">
            <layer3>
              <ip>10.0.0.1/24</ip>
            </layer3>
          </entry>
        </interfaces>
      </network>
    </entry>
  </devices>
</config>`
    },
    {
        id: 'paloalto_security_rule',
        name: 'Palo Alto - Security Rule',
        vendor: 'paloalto',
        category: 'security',
        description: 'Créer une règle de sécurité',
        icon: 'shield',
        xml: `<config target="fw-paloalto" host="192.168.6.1" os="panos" user="admin" password="password">
  <devices>
    <entry name="localhost.localdomain">
      <vsys>
        <entry name="vsys1">
          <security>
            <rules>
              <entry name="Allow-Web-Traffic">
                <source-user>any</source-user>
                <from>trust</from>
                <to>untrust</to>
                <source>any</source>
                <destination>any</destination>
                <application>web-browsing,ssl</application>
                <service>application-default</service>
                <action>allow</action>
              </entry>
            </rules>
          </security>
        </entry>
      </vsys>
    </entry>
  </devices>
</config>`
    },

    // ==================== GENERIC / COMMON ====================
    {
        id: 'multi_device_vlan',
        name: 'Multi-équipements - VLAN',
        vendor: 'generic',
        category: 'vlan',
        description: 'Déployer un même VLAN sur plusieurs équipements',
        icon: 'copy',
        xml: `<config target="switch-01" host="192.168.1.10" os="ios" user="admin" password="password">
  <vlan id="100">
    <name>PROD_VLAN</name>
  </vlan>
</config>
<config target="switch-02" host="192.168.1.11" os="ios" user="admin" password="password">
  <vlan id="100">
    <name>PROD_VLAN</name>
  </vlan>
</config>`
    },
    {
        id: 'dhcp_relay',
        name: 'Common - DHCP Relay',
        vendor: 'generic',
        category: 'network',
        description: 'Configurer un relay DHCP',
        icon: 'refresh-cw',
        xml: `<config target="router-01" host="192.168.1.1" os="ios" user="admin" password="password">
  <interface name="GigabitEthernet0/0">
    <ip-helper>
      <dhcp-server>192.168.10.10</dhcp-server>
    </ip-helper>
  </interface>
</config>`
    },
    {
        id: 'snmp_config',
        name: 'Common - SNMP',
        vendor: 'generic',
        category: 'monitoring',
        description: 'Configurer SNMP pour la supervision',
        icon: 'activity',
        xml: `<config target="router-01" host="192.168.1.1" os="ios" user="admin" password="password">
  <snmp>
    <community name="public">
      <acl>1</acl>
    </community>
    <location>Paris-Datacenter</location>
    <contact>admin@example.com</contact>
  </snmp>
</config>`
    },

    // ==================== LABS PRÉ-CONFIGURÉS ====================
    {
        id: 'lab_soho',
        name: 'Lab - SOHO (Petit Bureau)',
        vendor: 'lab',
        category: 'lab',
        description: '1 routeur + 2 switches, 3 VLANs. Idéal pour débuter.',
        icon: 'home',
        xml: `<config target="SOHO-Router" host="192.168.1.1" os="ios" user="admin" password="admin123">
  <vlan id="10"><name>MGMT</name></vlan>
  <vlan id="20"><name>DATA</name></vlan>
  <vlan id="30"><name>GUEST</name></vlan>
  <interface name="GigabitEthernet0/0">
    <description>WAN - ISP</description>
    <ip>dhcp</ip>
  </interface>
  <interface name="GigabitEthernet0/1">
    <description>LAN</description>
    <ip>192.168.10.1</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <ospf process-id="1" router-id="192.168.10.1">
    <area id="0">
      <network>192.168.10.0</network>
      <wildcard>0.0.0.255</wildcard>
    </area>
  </ospf>
</config>
<config target="Access-SW-01" host="192.168.1.10" os="ios" user="admin" password="admin123">
  <vlan id="10"><name>MGMT</name></vlan>
  <vlan id="20"><name>DATA</name></vlan>
  <vlan id="30"><name>GUEST</name></vlan>
  <interface name="GigabitEthernet0/1" mode="trunk">
    <description>Uplink to Router</description>
    <allowed-vlans>10,20,30</allowed-vlans>
  </interface>
</config>`
    },
    {
        id: 'lab_datacenter',
        name: 'Lab - Datacenter',
        vendor: 'lab',
        category: 'lab',
        description: 'Core switches avec EtherChannel et HSRP. Redondance complète.',
        icon: 'database',
        xml: `<config target="Core-SW-01" host="10.0.0.1" os="ios" user="admin" password="dc-admin">
  <vlan id="100"><name>SRV_PROD</name></vlan>
  <vlan id="200"><name>SRV_DEV</name></vlan>
  <vlan id="999"><name>NATIVE</name></vlan>
  <interface name="Vlan100">
    <description>SVI Production</description>
    <ip>10.100.0.1</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <interface name="Vlan200">
    <description>SVI Development</description>
    <ip>10.200.0.1</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <interface name="Port-channel1">
    <description>EtherChannel to Access</description>
    <mode>layer3</mode>
    <ip>10.10.10.1</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <bgp as="65100">
    <router-id>10.0.0.1</router-id>
    <neighbor ip="10.0.0.2" remote-as="65100">
      <description>iBGP Peer</description>
    </neighbor>
  </bgp>
</config>
<config target="Core-SW-02" host="10.0.0.2" os="ios" user="admin" password="dc-admin">
  <vlan id="100"><name>SRV_PROD</name></vlan>
  <vlan id="200"><name>SRV_DEV</name></vlan>
  <vlan id="999"><name>NATIVE</name></vlan>
  <interface name="Vlan100">
    <ip>10.100.0.2</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <interface name="Vlan200">
    <ip>10.200.0.2</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <interface name="Port-channel1">
    <description>EtherChannel to Access</description>
    <mode>layer3</mode>
    <ip>10.10.20.1</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <hsrp>
    <group>100</group>
    <priority>110</priority>
    <ip>10.100.0.254</ip>
    <preempt/>
  </hsrp>
  <bgp as="65100">
    <router-id>10.0.0.2</router-id>
    <neighbor ip="10.0.0.1" remote-as="65100">
      <description>iBGP Peer</description>
    </neighbor>
  </bgp>
</config>
<config target="Access-SW-01" host="10.10.10.2" os="ios" user="admin" password="dc-admin">
  <vlan id="100"><name>SRV_PROD</name></vlan>
  <vlan id="200"><name>SRV_DEV</name></vlan>
  <interface name="GigabitEthernet0/1" channel-group="1" mode="active"/>
  <interface name="GigabitEthernet0/2" channel-group="1" mode="active"/>
  <interface name="GigabitEthernet0/3" mode="access">
    <description>Server Production</description>
    <vlan>100</vlan>
    <spanning-tree portfast/>
  </interface>
</config>`
    },
    {
        id: 'lab_campus',
        name: 'Lab - Campus',
        vendor: 'lab',
        category: 'lab',
        description: 'Campus multi-bâtiment avec distribution redondante.',
        icon: 'building',
        xml: `<config target="Campus-Core" host="10.0.0.1" os="ios" user="admin" password="campus">
  <vlan id="10"><name>MGMT</name></vlan>
  <vlan id="20"><name>STAFF</name></vlan>
  <vlan id="30"><name>STUDENTS</name></vlan>
  <vlan id="40"><name>WIFI</name></vlan>
  <vlan id="50"><name>SECURITY</name></vlan>
  <interface name="GigabitEthernet0/0">
    <description>WAN - ISP</description>
    <ip>203.0.113.1</ip>
    <mask>255.255.255.252</mask>
  </interface>
  <ospf process-id="1" router-id="10.0.0.1">
    <area id="0">
      <network>10.0.0.0</network>
      <wildcard>0.0.255.255</wildcard>
    </area>
  </ospf>
</config>
<config target="Dist-A-01" host="10.10.1.1" os="ios" user="admin" password="campus">
  <vlan id="10"><name>MGMT</name></vlan>
  <vlan id="20"><name>STAFF</name></vlan>
  <vlan id="30"><name>STUDENTS</name></vlan>
  <vlan id="40"><name>WIFI</name></vlan>
  <vlan id="50"><name>SECURITY</name></vlan>
  <interface name="Vlan10">
    <ip>10.10.1.1</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <interface name="GigabitEthernet0/1" mode="trunk">
    <description>Uplink Core</description>
    <allowed-vlans>10,20,30,40,50</allowed-vlans>
  </interface>
  <interface name="GigabitEthernet0/2" mode="trunk">
    <description>Backup Uplink</description>
    <allowed-vlans>10,20,30,40,50</allowed-vlans>
  </interface>
</config>
<config target="Dist-B-01" host="10.10.2.1" os="ios" user="admin" password="campus">
  <vlan id="10"><name>MGMT</name></vlan>
  <vlan id="20"><name>STAFF</name></vlan>
  <vlan id="30"><name>STUDENTS</name></vlan>
  <vlan id="40"><name>WIFI</name></vlan>
  <vlan id="50"><name>SECURITY</name></vlan>
  <interface name="Vlan10">
    <ip>10.10.2.1</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <interface name="GigabitEthernet0/1" mode="trunk">
    <description>Uplink Core</description>
    <allowed-vlans>10,20,30,40,50</allowed-vlans>
  </interface>
</config>`
    },
    {
        id: 'lab_wan_l3vpn',
        name: 'Lab - WAN L3VPN',
        vendor: 'lab',
        category: 'lab',
        description: 'Multi-sites avec BGP. Paris, Lyon, Marseille.',
        icon: 'globe',
        xml: `<config target="PE-Paris" host="10.0.1.1" os="ios" user="admin" password="wan123">
  <interface name="GigabitEthernet0/0">
    <description>WAN</description>
    <ip>10.0.1.1</ip>
    <mask>255.255.255.252</mask>
  </interface>
  <interface name="Loopback0">
    <ip>1.1.1.1</ip>
    <mask>255.255.255.255</mask>
  </interface>
  <bgp as="65101">
    <router-id>1.1.1.1</router-id>
    <neighbor ip="10.0.1.2" remote-as="65000">
      <description>ISP RR</description>
    </neighbor>
  </bgp>
</config>
<config target="PE-Lyon" host="10.0.2.1" os="ios" user="admin" password="wan123">
  <interface name="GigabitEthernet0/0">
    <description>WAN</description>
    <ip>10.0.2.1</ip>
    <mask>255.255.255.252</mask>
  </interface>
  <interface name="Loopback0">
    <ip>2.2.2.2</ip>
    <mask>255.255.255.255</mask>
  </interface>
  <bgp as="65102">
    <router-id>2.2.2.2</router-id>
    <neighbor ip="10.0.2.2" remote-as="65000">
      <description>ISP RR</description>
    </neighbor>
  </bgp>
</config>
<config target="PE-Marseille" host="10.0.3.1" os="ios" user="admin" password="wan123">
  <interface name="GigabitEthernet0/0">
    <description>WAN</description>
    <ip>10.0.3.1</ip>
    <mask>255.255.255.252</mask>
  </interface>
  <interface name="Loopback0">
    <ip>3.3.3.3</ip>
    <mask>255.255.255.255</mask>
  </interface>
  <bgp as="65103">
    <router-id>3.3.3.3</router-id>
    <neighbor ip="10.0.3.2" remote-as="65000">
      <description>ISP RR</description>
    </neighbor>
  </bgp>
</config>
<config target="CE-Paris" host="192.168.100.1" os="ios" user="admin" password="wan123">
  <interface name="GigabitEthernet0/0">
    <description>LAN</description>
    <ip>192.168.100.1</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <interface name="GigabitEthernet0/1">
    <description>WAN to PE</description>
    <ip>192.168.1.1</ip>
    <mask>255.255.255.252</mask>
  </interface>
  <bgp as="65201">
    <router-id>192.168.100.1</router-id>
    <neighbor ip="192.168.1.2" remote-as="65101">
      <description>PE Paris</description>
    </neighbor>
  </bgp>
</config>`
    },
    {
        id: 'lab_infrastructure',
        name: 'Lab - Infrastructure Base',
        vendor: 'lab',
        category: 'lab',
        description: 'Infrastructure de base multi-VLAN avec routing.',
        icon: 'server',
        xml: `<config target="Core-Router" host="192.168.1.1" os="ios" user="admin" password="admin">
  <vlan id="10"><name>MGMT</name></vlan>
  <vlan id="20"><name>DATA</name></vlan>
  <vlan id="30"><name>VOICE</name></vlan>
  <interface name="GigabitEthernet0/0">
    <description>WAN</description>
    <ip>192.168.1.1</ip>
    <mask>255.255.255.0</mask>
  </interface>
  <bgp as="65001">
    <router-id>192.168.1.1</router-id>
    <neighbor ip="192.168.1.2" remote-as="65002">
      <description>Peer EBGP</description>
    </neighbor>
  </bgp>
</config>
<config target="Distribution-SW-01" host="192.168.1.10" os="ios" user="admin" password="admin">
  <vlan id="10"><name>MGMT</name></vlan>
  <vlan id="20"><name>DATA</name></vlan>
  <vlan id="30"><name>VOICE</name></vlan>
  <interface name="GigabitEthernet0/1" mode="trunk">
    <description>Uplink to Core</description>
    <allowed-vlans>10,20,30</allowed-vlans>
  </interface>
  <interface name="GigabitEthernet0/2" mode="access">
    <description>User Port</description>
    <vlan>20</vlan>
  </interface>
</config>
<config target="Distribution-SW-02" host="192.168.1.11" os="ios" user="admin" password="admin">
  <vlan id="10"><name>MGMT</name></vlan>
  <vlan id="20"><name>DATA</name></vlan>
  <vlan id="30"><name>VOICE</name></vlan>
  <interface name="GigabitEthernet0/1" mode="trunk">
    <description>Uplink to Core</description>
    <allowed-vlans>10,20,30</allowed-vlans>
  </interface>
</config>`
    },

    // ==================== CISCO IOS-XE COMPREHENSIVE ====================
    {
        id: 'cisco_iosxe_interface',
        name: 'Cisco IOS-XE - Interface NETCONF',
        vendor: 'cisco',
        category: 'interface',
        description: 'Configuration interface L3 avec IP via NETCONF Cisco IOS-XE',
        icon: 'network',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces">
    <interface>
      <name>GigabitEthernet1</name>
      <description>WAN Uplink to Provider</description>
      <enabled>true</enabled>
      <ipv4 xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces">
        <address>
          <primary>
            <address>203.0.113.10</address>
            <mask>255.255.255.252</mask>
          </primary>
        </address>
      </ipv4>
    </interface>
    <interface>
      <name>GigabitEthernet2</name>
      <description>LAN Internal Network</description>
      <enabled>true</enabled>
      <ipv4>
        <address>
          <primary>
            <address>192.168.1.1</address>
            <mask>255.255.255.0</mask>
          </primary>
        </address>
      </ipv4>
    </interface>
  </interfaces>
</config>`
    },
    {
        id: 'cisco_iosxe_vlan',
        name: 'Cisco IOS-XE - VLANs NETCONF',
        vendor: 'cisco',
        category: 'vlan',
        description: 'Creation de VLANs multiples via NETCONF Cisco IOS-XE',
        icon: 'layers',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <vlans xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-vlan">
    <vlan>
      <id>100</id>
      <name>PRODUCTION_DATA</name>
      <status>active</status>
    </vlan>
    <vlan>
      <id>200</id>
      <name>VOICE_IP</name>
      <status>active</status>
    </vlan>
    <vlan>
      <id>300</id>
      <name>MGMT_NETWORK</name>
      <status>active</status>
    </vlan>
    <vlan>
      <id>999</id>
      <name>NATIVE_VLAN</name>
      <status>active</status>
    </vlan>
  </vlans>
</config>`
    },
    {
        id: 'cisco_iosxe_static_route',
        name: 'Cisco IOS-XE - Route Statique NETCONF',
        vendor: 'cisco',
        category: 'routing',
        description: 'Configuration route statique IPv4 via NETCONF',
        icon: 'share-2',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <routing xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-routing">
    <routing-instance>
      <name>default</name>
      <routing-protocols>
        <routing-protocol>
          <type>static</type>
          <name>1</name>
          <static-routes>
            <ipv4>
              <route>
                <destination-prefix>0.0.0.0/0</destination-prefix>
                <next-hop>
                  <address>203.0.113.1</address>
                  <route-preference>1</route-preference>
                </next-hop>
              </route>
              <route>
                <destination-prefix>192.168.100.0/24</destination-prefix>
                <next-hop>
                  <address>10.1.1.1</address>
                  <route-preference>1</route-preference>
                </next-hop>
              </route>
            </ipv4>
          </static-routes>
        </routing-protocol>
      </routing-protocols>
    </routing-instance>
  </routing>
</config>`
    },
    {
        id: 'cisco_iosxe_ntp',
        name: 'Cisco IOS-XE - NTP NETCONF',
        vendor: 'cisco',
        category: 'system',
        description: 'Configuration serveur NTP via NETCONF',
        icon: 'clock',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <ntp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ntp">
    <server>
      <address>10.10.10.1</address>
      <association-type>server</association-type>
      <prefer>true</prefer>
    </server>
    <server>
      <address>10.10.10.2</address>
      <association-type>server</association-type>
    </server>
    <server>
      <address>0.fr.pool.ntp.org</address>
      <association-type>server</association-type>
    </server>
    <server>
      <address>1.fr.pool.ntp.org</address>
      <association-type>server</association-type>
    </server>
  </ntp>
</config>`
    },
    {
        id: 'cisco_iosxe_dns',
        name: 'Cisco IOS-XE - DNS NETCONF',
        vendor: 'cisco',
        category: 'system',
        description: 'Configuration DNS et domain-name via NETCONF',
        icon: 'globe',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <dns xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-dns">
    <ipv4>
      <server>
        <ip-address>8.8.8.8</ip-address>
      </server>
      <server>
        <ip-address>8.8.4.4</ip-address>
      </server>
      <server>
        <ip-address>1.1.1.1</ip-address>
      </server>
    </ipv4>
    <domain>
      <name>network.local</name>
    </domain>
  </dns>
</config>`
    },
    {
        id: 'cisco_iosxe_banner',
        name: 'Cisco IOS-XE - Banniere NETCONF',
        vendor: 'cisco',
        category: 'security',
        description: 'Configuration banniere login et MOTD via NETCONF',
        icon: 'alert-triangle',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <banner xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-banner">
    <banner-input>
      <type>login</type>
      <message>###############################################################################
# ACCES RESTREINT - RESEAU ENTREPRISE
# Ce systeme est reserve aux utilisateurs autorises. Toute connexion non autorisee
# sera signalee et poursuitee conformement a la legislation en vigueur.
# Contact: admin@network.local | Urgence: +33 1 23 45 67 89
###############################################################################</message>
    </banner-input>
    <banner-input>
      <type>motd</type>
      <message>========================================
Bienvenue sur l'equipement de production
Date: \\D \\T
Utilisateur: \\u
========================================</message>
    </banner-input>
  </banner>
</config>`
    },
    {
        id: 'cisco_iosxe_user',
        name: 'Cisco IOS-XE - Utilisateurs NETCONF',
        vendor: 'cisco',
        category: 'security',
        description: 'Creation utilisateurs locaux avec privileges via NETCONF',
        icon: 'user',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <aaa xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-aaa">
    <userauthentication>
      <user>
        <name>netadmin</name>
        <privilege>15</privilege>
        <password>
          <encryption>5</encryption>
          <pass>$1$encrypted$hash</pass>
        </password>
      </user>
      <user>
        <name>operator</name>
        <privilege>7</privilege>
        <password>
          <encryption>5</encryption>
          <pass>$1$encrypted$hash</pass>
        </password>
      </user>
      <user>
        <name>monitoring</name>
        <privilege>5</privilege>
        <password>
          <encryption>5</encryption>
          <pass>$1$encrypted$hash</pass>
        </password>
      </user>
    </userauthentication>
  </aaa>
</config>`
    },
    {
        id: 'cisco_iosxe_snmp',
        name: 'Cisco IOS-XE - SNMP NETCONF',
        vendor: 'cisco',
        category: 'monitoring',
        description: 'Configuration SNMP v2c avec communautes et traps via NETCONF',
        icon: 'activity',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <snmp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-snmp">
    <community>
      <community-string>
        <name>public</name>
        <access-list>10</access-list>
        <view>readonly</view>
      </community-string>
      <community-string>
        <name>private</name>
        <access-list>10</access-list>
        <view>readwrite</view>
      </community-string>
    </community>
    <trap>
      <server>192.168.1.100</server>
      <community>public</community>
      <version>v2c</version>
    </trap>
    <location>Paris-DC-Rack01-POS01</location>
    <contact>admin@network.local | +33 1 23 45 67 89</contact>
  </snmp>
</config>`
    },

    // ==================== CISCO NX-OS COMPREHENSIVE ====================
    {
        id: 'cisco_nxos_interface',
        name: 'Cisco NX-OS - Interface NETCONF',
        vendor: 'cisco',
        category: 'interface',
        description: 'Configuration interface OpenConfig via NETCONF NX-OS',
        icon: 'network',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="http://openconfig.net/yang/interfaces">
    <interface>
      <name>Ethernet1/1</name>
      <config>
        <description>Server Uplink - Production</description>
        <enabled>true</enabled>
        <mtu>9000</mtu>
      </config>
    </interface>
    <interface>
      <name>Ethernet1/2</name>
      <config>
        <description>Uplink Core Switch</description>
        <enabled>true</enabled>
        <mtu>9000</mtu>
      </config>
    </interface>
  </interfaces>
</config>`
    },
    {
        id: 'cisco_nxos_vlan',
        name: 'Cisco NX-OS - VLANs NETCONF',
        vendor: 'cisco',
        category: 'vlan',
        description: 'Creation VLANs OpenConfig via NETCONF NX-OS',
        icon: 'layers',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <vlans xmlns="http://openconfig.net/yang/vlan">
    <vlan>
      <vlan-id>100</vlan-id>
      <config>
        <vlan-id>100</vlan-id>
        <name>PRODUCTION_DATA</name>
        <status>ACTIVE</status>
      </config>
    </vlan>
    <vlan>
      <vlan-id>200</vlan-id>
      <config>
        <vlan-id>200</vlan-id>
        <name>VOICE</name>
        <status>ACTIVE</status>
      </config>
    </vlan>
    <vlan>
      <vlan-id>999</vlan-id>
      <config>
        <vlan-id>999</vlan-id>
        <name>NATIVE</name>
        <status>ACTIVE</status>
      </config>
    </vlan>
  </vlans>
</config>`
    },
    {
        id: 'cisco_nxos_ntp',
        name: 'Cisco NX-OS - NTP NETCONF',
        vendor: 'cisco',
        category: 'system',
        description: 'Configuration NTP via NETCONF NX-OS',
        icon: 'clock',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <ntp xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
    <server>
      <address>10.10.10.1</address>
      <prefer>true</prefer>
    </server>
    <server>
      <address>10.10.10.2</address>
    </server>
  </ntp>
</config>`
    },
    {
        id: 'cisco_nxos_dns',
        name: 'Cisco NX-OS - DNS NETCONF',
        vendor: 'cisco',
        category: 'system',
        description: 'Configuration DNS via NETCONF NX-OS',
        icon: 'globe',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <ip xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
    <name-server>
      <address>8.8.8.8</address>
    </name-server>
    <name-server>
      <address>1.1.1.1</address>
    </name-server>
  </ip>
</config>`
    },
    {
        id: 'cisco_nxos_banner',
        name: 'Cisco NX-OS - Banniere NETCONF',
        vendor: 'cisco',
        category: 'security',
        description: 'Configuration banniere MOTD via NETCONF NX-OS',
        icon: 'alert-triangle',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <banner xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
    <motd-banner>#######################################################################
# RESEAU NATIONAL DE RECHERCHE
# Acces reserve aux personnels autorises. Toute tentative d'acces non autorise
# est interdite et fera l'objet de poursuites.
# NOC: noc@reseau.fr | 01 23 45 67 90
#######################################################################</motd-banner>
  </banner>
</config>`
    },
    {
        id: 'cisco_nxos_user',
        name: 'Cisco NX-OS - Utilisateurs NETCONF',
        vendor: 'cisco',
        category: 'security',
        description: 'Creation utilisateurs via NETCONF NX-OS',
        icon: 'user',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <aaa xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
    <authentication-login>
      <auth-mode>local</auth-mode>
    </authentication-login>
    <users>
      <user>
        <name>admin</name>
        <pwd>$1$encrypted$hash</pwd>
        <role>network-admin</role>
      </user>
      <user>
        <name>netops</name>
        <pwd>$1$encrypted$hash</pwd>
        <role>network-operator</role>
      </user>
    </users>
  </aaa>
</config>`
    },
    {
        id: 'cisco_nxos_snmp',
        name: 'Cisco NX-OS - SNMP NETCONF',
        vendor: 'cisco',
        category: 'monitoring',
        description: 'Configuration SNMP via NETCONF NX-OS',
        icon: 'activity',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <snmp-server xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
    <community>public</community>
    <community>private</community>
    <trap-cluster>192.168.1.100</trap-cluster>
    <location>DataCenter-Paris-Rack01-SW01</location>
    <contact>noc@reseau.fr</contact>
  </snmp-server>
</config>`
    },

    // ==================== JUNIPER JUNOS COMPREHENSIVE ====================
    {
        id: 'juniper_interface',
        name: 'Juniper JunOS - Interface NETCONF',
        vendor: 'juniper',
        category: 'interface',
        description: 'Configuration interfaces Layer 3 et trunk via NETCONF JunOS',
        icon: 'network',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <interfaces>
    <interface>
      <name>ge-0/0/0</name>
      <description>Uplink vers Routeur Core</description>
      <unit>
        <name>0</name>
        <family>
          <inet>
            <address>
              <name>10.10.10.2/30</name>
            </address>
          </inet>
        </family>
      </unit>
    </interface>
    <interface>
      <name>ge-0/0/1</name>
      <description>Downlink vers Access Switch</description>
      <mtu>9000</mtu>
      <unit>
        <name>0</name>
        <family>
          <ethernet-switching>
            <interface-mode>trunk</interface-mode>
            <vlan>
              <members>100</members>
              <members>200</members>
              <members>300</members>
            </vlan>
          </ethernet-switching>
        </family>
      </unit>
    </interface>
  </interfaces>
</config>`
    },
    {
        id: 'juniper_vlan',
        name: 'Juniper JunOS - VLANs NETCONF',
        vendor: 'juniper',
        category: 'vlan',
        description: 'Creation VLANs avec IRB et L3 via NETCONF JunOS',
        icon: 'layers',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <vlans>
    <vlan>
      <name>PROD_DATA</name>
      <vlan-id>100</vlan-id>
      <description>VLAN Production Donnees</description>
      <l3-interface>vlan.100</l3-interface>
    </vlan>
    <vlan>
      <name>VOICE</name>
      <vlan-id>200</vlan-id>
      <description>VLAN Voix IP</description>
      <l3-interface>vlan.200</l3-interface>
    </vlan>
    <vlan>
      <name>MGMT</name>
      <vlan-id>300</vlan-id>
      <description>VLAN Management</description>
      <l3-interface>vlan.300</l3-interface>
    </vlan>
  </vlans>
</config>`
    },
    {
        id: 'juniper_static_route',
        name: 'Juniper JunOS - Route Statique NETCONF',
        vendor: 'juniper',
        category: 'routing',
        description: 'Configuration routes statiques via NETCONF JunOS',
        icon: 'share-2',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <routing-options>
    <static>
      <route>
        <name>0.0.0.0/0</name>
        <next-table>inet.0</next-table>
        <qualified-next-hop>
          <address>10.10.10.1</address>
          <preference>1</preference>
        </qualified-next-hop>
      </route>
      <route>
        <name>192.168.0.0/16</name>
        <next-hop>10.1.1.1</next-hop>
        <preference>10</preference>
      </route>
      <route>
        <name>10.0.0.0/8</name>
        <next-hop>10.10.10.1</next-hop>
        <preference>5</preference>
      </route>
    </static>
  </routing-options>
</config>`
    },
    {
        id: 'juniper_ntp',
        name: 'Juniper JunOS - NTP NETCONF',
        vendor: 'juniper',
        category: 'system',
        description: 'Configuration NTP via NETCONF JunOS',
        icon: 'clock',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <system>
    <ntp>
      <boot-server>10.10.10.1</boot-server>
      <server>
        <name>10.10.10.1</name>
        <prefer/>
      </server>
      <server>
        <name>10.10.10.2</name>
      </server>
      <server>
        <name>0.fr.pool.ntp.org</name>
      </server>
      <server>
        <name>1.fr.pool.ntp.org</name>
      </server>
    </ntp>
  </system>
</config>`
    },
    {
        id: 'juniper_dns',
        name: 'Juniper JunOS - DNS NETCONF',
        vendor: 'juniper',
        category: 'system',
        description: 'Configuration DNS et domain-search via NETCONF JunOS',
        icon: 'globe',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <system>
    <name-server>
      <address>8.8.8.8</address>
    </name-server>
    <name-server>
      <address>8.8.4.4</address>
    </name-server>
    <name-server>
      <address>1.1.1.1</address>
    </name-server>
    <domain-name>juniper.local</domain-name>
    <domain-search>
      <list>network.local</list>
      <list>entreprise.fr</list>
    </domain-search>
  </system>
</config>`
    },
    {
        id: 'juniper_banner',
        name: 'Juniper JunOS - Banniere NETCONF',
        vendor: 'juniper',
        category: 'security',
        description: 'Configuration login et announcement banners via NETCONF',
        icon: 'alert-triangle',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <system>
    <login>
      <banner>
        <message>################################################################################
# ACCES AUTORISE UNIQUEMENT - SYSTEME PROTEGE
# Ce systeme appartient a l'entreprise et son utilisation est reservee aux
# employs autorises. Toute tentative d'acces non autorisee constitue une
# infraction penale et sera signalee aux autorites competentes.
# Contact Securite: security@entreprise.fr | Urgence: 01 23 45 67 89
################################################################################</message>
      </banner>
      <announcement>
<message>================================================================================
Bienvenue sur l'equipement Juniper - $(hostname)
Version Junos: $(version)
Derniere connexion: $(time)
================================================================================</message>
      </announcement>
    </login>
  </system>
</config>`
    },
    {
        id: 'juniper_user',
        name: 'Juniper JunOS - Utilisateurs NETCONF',
        vendor: 'juniper',
        category: 'security',
        description: 'Creation utilisateurs avec classes via NETCONF JunOS',
        icon: 'user',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <system>
    <login>
      <user>
        <name>admin</name>
        <uid>2000</uid>
        <class>super-user</class>
        <authentication>
          <encrypted-password>$1$encrypted$hash</encrypted-password>
        </authentication>
      </user>
      <user>
        <name>netadmin</name>
        <uid>2001</uid>
        <class>operator</class>
        <authentication>
          <encrypted-password>$1$encrypted$hash</encrypted-password>
        </authentication>
      </user>
      <user>
        <name>monitoring</name>
        <uid>2002</uid>
        <class>read-only</class>
        <authentication>
          <ssh-rsa>
            <name>ssh-rsa AAAAB3NzaC1... user@monitoring</name>
          </ssh-rsa>
        </authentication>
      </user>
    </login>
  </system>
</config>`
    },
    {
        id: 'juniper_snmp',
        name: 'Juniper JunOS - SNMP NETCONF',
        vendor: 'juniper',
        category: 'monitoring',
        description: 'Configuration SNMP avec communautes et trap-groups via NETCONF',
        icon: 'activity',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <snmp>
    <location>Paris-DC-Rack01-vMX-01</location>
    <contact>admin@juniper.local</contact>
    <community>
      <name>public</name>
      <authorization>read-only</authorization>
    </community>
    <community>
      <name>private</name>
      <authorization>read-write</authorization>
    </community>
    <trap-group>
      <name>NOC-TRAPS</name>
      <destination-address>
        <name>192.168.1.100</name>
      </destination-address>
      <destination-address>
        <name>192.168.1.101</name>
      </destination-address>
    </trap-group>
  </snmp>
</config>`
    },

    // ==================== ARUBA AOS COMPREHENSIVE ====================
    {
        id: 'aruba_interface',
        name: 'Aruba EOS - Interface NETCONF',
        vendor: 'aruba',
        category: 'interface',
        description: 'Configuration interface L3 via NETCONF Aruba EOS',
        icon: 'network',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <interface>
      <name>1/1/1</name>
      <config>
        <description>Uplink vers Distribution</description>
      </config>
      <subinterface>
        <id>0</id>
        <ipv4>
          <address>
            <ip>10.10.20.2</ip>
            <prefix-length>30</prefix-length>
          </address>
        </ipv4>
      </subinterface>
    </interface>
    <interface>
      <name>1/1/2</name>
      <config>
        <description>Port Access User</description>
      </config>
    </interface>
  </interfaces>
</config>`
    },
    {
        id: 'aruba_vlan',
        name: 'Aruba EOS - VLANs NETCONF',
        vendor: 'aruba',
        category: 'vlan',
        description: 'Creation VLANs via NETCONF Aruba EOS',
        icon: 'layers',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <vlans xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <vlan>
      <id>100</id>
      <name>CORP_DATA</name>
    </vlan>
    <vlan>
      <id>200</id>
      <name>CORP_VOICE</name>
    </vlan>
    <vlan>
      <id>300</id>
      <name>CORP_MGMT</name>
    </vlan>
  </vlans>
</config>`
    },
    {
        id: 'aruba_static_route',
        name: 'Aruba EOS - Route Statique NETCONF',
        vendor: 'aruba',
        category: 'routing',
        description: 'Configuration route statique via NETCONF Aruba EOS',
        icon: 'share-2',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <routing xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <static-routes>
      <ipv4>
        <route>
          <prefix>0.0.0.0/0</prefix>
          <next-hop>10.10.20.1</next-hop>
        </route>
        <route>
          <prefix>172.16.0.0/12</prefix>
          <next-hop>10.10.20.1</next-hop>
        </route>
      </ipv4>
    </static-routes>
  </routing>
</config>`
    },
    {
        id: 'aruba_ntp',
        name: 'Aruba EOS - NTP NETCONF',
        vendor: 'aruba',
        category: 'system',
        description: 'Configuration NTP via NETCONF Aruba EOS',
        icon: 'clock',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <system xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <ntp>
      <server>
        <address>10.10.10.1</address>
        <prefer>true</prefer>
      </server>
      <server>
        <address>10.10.10.2</address>
      </server>
    </ntp>
  </system>
</config>`
    },
    {
        id: 'aruba_dns',
        name: 'Aruba EOS - DNS NETCONF',
        vendor: 'aruba',
        category: 'system',
        description: 'Configuration DNS via NETCONF Aruba EOS',
        icon: 'globe',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <system xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <dns>
      <server>
        <address>8.8.8.8</address>
      </server>
      <server>
        <address>1.1.1.1</address>
      </server>
    </dns>
    <domain-name>aruba.local</domain-name>
  </system>
</config>`
    },
    {
        id: 'aruba_banner',
        name: 'Aruba EOS - Banniere NETCONF',
        vendor: 'aruba',
        category: 'security',
        description: 'Configuration banniere login via NETCONF Aruba',
        icon: 'alert-triangle',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <system xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <banners>
      <login>
<message>##############################################################################
# ACCES RESTREINT - RESEAU D'ENTREPRISE ARUBA
# Cet equipement est reserve aux personnalites autorisees.
# Toutes activites non autorisees seront signalees.
##############################################################################</message>
      </login>
    </banners>
  </system>
</config>`
    },
    {
        id: 'aruba_user',
        name: 'Aruba EOS - Utilisateurs NETCONF',
        vendor: 'aruba',
        category: 'security',
        description: 'Creation utilisateurs via NETCONF Aruba EOS',
        icon: 'user',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <system xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <aaa>
      <authentication>
        <user>
          <name>admin</name>
          <password>$1$encrypted$hash</password>
          <role>superuser</role>
        </user>
        <user>
          <name>netop</name>
          <password>$1$encrypted$hash</password>
          <role>manager</role>
        </user>
        <user>
          <name>guest</name>
          <password>$1$encrypted$hash</password>
          <role>guest</role>
        </user>
      </authentication>
    </aaa>
  </system>
</config>`
    },
    {
        id: 'aruba_snmp',
        name: 'Aruba EOS - SNMP NETCONF',
        vendor: 'aruba',
        category: 'monitoring',
        description: 'Configuration SNMP via NETCONF Aruba EOS',
        icon: 'activity',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <snmp xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <community>
      <name>public</name>
      <access-mode>read-only</access-mode>
    </community>
    <community>
      <name>private</name>
      <access-mode>read-write</access-mode>
    </community>
    <location>Aruba-SW-5400-Paris-Floor1</location>
    <contact>admin@aruba.local</contact>
  </snmp>
</config>`
    },

    // ==================== FORTINET FORTIOS COMPREHENSIVE ====================
    {
        id: 'fortinet_interface',
        name: 'Fortinet FortiOS - Interface NETCONF',
        vendor: 'fortinet',
        category: 'interface',
        description: 'Configuration interfaces physiques et VLANs via NETCONF FortiOS',
        icon: 'network',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <system>
    <interface>
      <name>port1</name>
      <ip>10.10.10.1 255.255.255.0</ip>
      <description>WAN - Connection ISP</description>
      <alias>WAN-UPLINK</alias>
      <芒聙聹ype>physical</芒聙聹ype>
      <芒聙聹tatus>up</芒聙聹tatus>
      <芒聙聹芒聙聹>9000</芒聙聹芒聙聹>
    </interface>
    <interface>
      <name>port2</name>
      <ip>192.168.1.1 255.255.255.0</ip>
      <description>LAN - Internal Network</description>
      <alias>LAN-INTERNAL</alias>
      <芒聙聹ype>physical</芒聙聹ype>
      <芒聙聹tatus>up</芒聙聹tatus>
    </interface>
    <interface>
      <name>port3</name>
      <description>DMZ - Serveurs</description>
      <alias>DMZ-SERVERS</alias>
      <芒聙聹ype>physical</芒聙聹ype>
      <芒聙聹tatus>up</芒聙聹tatus>
    </interface>
  </system>
</config>`
    },
    {
        id: 'fortinet_vlan',
        name: 'Fortinet FortiOS - VLAN NETCONF',
        vendor: 'fortinet',
        category: 'vlan',
        description: 'Creation interfaces VLAN via NETCONF FortiOS',
        icon: 'layers',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <system>
    <interface>
      <name>vlan100</name>
      <芒聙聹ype>vlan</芒聙聹ype>
      <芒聙聹tatus>up</芒聙聹tatus>
      <ip>192.168.100.1 255.255.255.0</ip>
      <description>DATA_VLAN</description>
      <vlanid>100</vlanid>
      <interface>port2</interface>
    </interface>
    <interface>
      <name>vlan200</name>
      <芒聙聹ype>vlan</芒聙聹ype>
      <芒聙聹tatus>up</芒聙聹tatus>
      <ip>192.168.200.1 255.255.255.0</ip>
      <description>VOICE_VLAN</description>
      <vlanid>200</vlanid>
      <interface>port2</interface>
    </interface>
  </system>
</config>`
    },
    {
        id: 'fortinet_static_route',
        name: 'Fortinet FortiOS - Route Statique NETCONF',
        vendor: 'fortinet',
        category: 'routing',
        description: 'Configuration routes statiques via NETCONF FortiOS',
        icon: 'share-2',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <router>
    <static>
      <seq-num>
        <id>1</id>
        <dst>0.0.0.0 0.0.0.0</dst>
        <gateway>10.10.10.254</gateway>
        <device>port1</device>
        <distance>10</distance>
        <芒聙聹atus>enable</芒聙聹atus>
      </seq-num>
      <seq-num>
        <id>2</id>
        <dst>192.168.50.0 255.255.255.0</dst>
        <gateway>192.168.1.254</gateway>
        <device>port2</device>
        <distance>10</distance>
      </seq-num>
      <seq-num>
        <id>3</id>
        <dst>10.0.0.0 255.0.0.0</dst>
        <gateway>10.10.10.1</gateway>
        <device>port1</device>
        <distance>5</distance>
      </seq-num>
    </static>
  </router>
</config>`
    },
    {
        id: 'fortinet_ntp',
        name: 'Fortinet FortiOS - NTP NETCONF',
        vendor: 'fortinet',
        category: 'system',
        description: 'Configuration NTP via NETCONF FortiOS',
        icon: 'clock',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <system>
    <ntpserver>
      <ntpserver-1>
        <server>10.10.10.1</server>
        <id>1</id>
        <prefer>enable</prefer>
        <status>enable</status>
      </ntpserver-1>
      <ntpserver-2>
        <server>10.10.10.2</server>
        <id>2</id>
        <status>enable</status>
      </ntpserver-2>
      <ntpserver-3>
        <server>0.fr.pool.ntp.org</server>
        <id>3</id>
        <status>enable</status>
      </ntpserver-3>
    </ntpserver>
    <ntp>
      <sync-interval>60</sync-interval>
    </ntp>
  </system>
</config>`
    },
    {
        id: 'fortinet_dns',
        name: 'Fortinet FortiOS - DNS NETCONF',
        vendor: 'fortinet',
        category: 'system',
        description: 'Configuration DNS via NETCONF FortiOS',
        icon: 'globe',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <system>
    <dns>
      <primary>8.8.8.8</primary>
      <secondary>8.8.4.4</secondary>
      <tertiary>1.1.1.1</tertiary>
    </dns>
  </system>
</config>`
    },
    {
        id: 'fortinet_banner',
        name: 'Fortinet FortiOS - Banniere NETCONF',
        vendor: 'fortinet',
        category: 'security',
        description: 'Configuration page de login via NETCONF FortiOS',
        icon: 'alert-triangle',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <system>
    <custom>
      <login-page>
<message>################################################################################
# RESEAU SECURISE - ACCES RESTREINT
# Ce reseau est surveille et protege. Tout acces non autorise est interdit
# et fera l'objet de poursuites conformement a la legislation en vigueur.
# Centre de Supervision: noc@fortinet.local | Tel: 01 23 45 67 89
################################################################################</message>
      </login-page>
    </custom>
  </system>
</config>`
    },
    {
        id: 'fortinet_user',
        name: 'Fortinet FortiOS - Utilisateurs NETCONF',
        vendor: 'fortinet',
        category: 'security',
        description: 'Creation utilisateurs locaux via NETCONF FortiOS',
        icon: 'user',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <user>
    <local>
      <name>admin</name>
      <type>password</type>
      <passwd>$1$encrypted$hash</passwd>
      <profile>super_admin</profile>
    </local>
    <local>
      <name>netadmin</name>
      <type>password</type>
      <passwd>$1$encrypted$hash</passwd>
      <profile>prof_admin</profile>
    </local>
    <local>
      <name>guest</name>
      <type>password</type>
      <passwd>$1$encrypted$hash</passwd>
      <profile>guest_admin</profile>
    </local>
  </user>
  <user>
    <group>
      <name>network-admins</name>
      <芒聙聹ype>firewall</芒聙聹ype>
      <member>admin</member>
      <member>netadmin</member>
    </group>
  </user>
</config>`
    },
    {
        id: 'fortinet_snmp',
        name: 'Fortinet FortiOS - SNMP NETCONF',
        vendor: 'fortinet',
        category: 'monitoring',
        description: 'Configuration SNMP via NETCONF FortiOS',
        icon: 'activity',
        xml: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <system>
    <snmp>
      <sysinfo>
        <status>enable</status>
        <location>Paris-DC-FW-01</location>
        <contact>admin@fortinet.local</contact>
      </sysinfo>
      <community>
        <name>public</name>
        <id>1</id>
        <芒聙聹ype>v1v2c</芒聙聹ype>
        <hosts>
          <host>
            <id>1</id>
            <ip>192.168.1.100 255.255.255.255</ip>
          </host>
        </hosts>
      </community>
      <community>
        <name>private</name>
        <id>2</id>
        <芒聙聹ype>v1v2c</芒聙聹ype>
        <hosts>
          <host>
            <id>1</id>
            <ip>192.168.1.100 255.255.255.255</ip>
          </host>
        </hosts>
      </community>
    </snmp>
  </system>
</config>`
    }
];

// Template helper functions
function getTemplatesByVendor(vendor) {
    if (vendor === 'all') return templatesDB;
    return templatesDB.filter(t => t.vendor === vendor);
}

function getTemplateById(id) {
    return templatesDB.find(t => t.id === id);
}

function getVendorColor(vendor) {
    const colors = {
        cisco: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/50' },
        juniper: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/50' },
        aruba: { bg: 'bg-cyan-500/20', text: 'text-cyan-400', border: 'border-cyan-500/50' },
        fortinet: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/50' },
        mikrotik: { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/50' },
        paloalto: { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500/50' },
        lab: { bg: 'bg-pink-500/20', text: 'text-pink-400', border: 'border-pink-500/50' },
        generic: { bg: 'bg-slate-500/20', text: 'text-slate-400', border: 'border-slate-500/50' }
    };
    return colors[vendor] || colors.generic;
}

function getCategoryIcon(category) {
    const icons = {
        vlan: 'layers',
        interface: 'network',
        routing: 'share-2',
        security: 'shield',
        redundancy: 'heart-handshake',
        monitoring: 'activity',
        network: 'cable'
    };
    return icons[category] || 'file-code';
}

// ==================== COMPREHENSIVE NETCONF CONFIGURATIONS ====================

// CISCO IOS-XE NETCONF
const ciscoIosxeNetconf = {
    interface: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces">
    <interface>
      <name>GigabitEthernet1</name>
      <description>WAN Uplink to Provider</description>
      <enabled>true</enabled>
      <ipv4 xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces">
        <address>
          <primary>
            <address>203.0.113.10</address>
            <mask>255.255.255.252</mask>
          </primary>
        </address>
      </ipv4>
    </interface>
  </interfaces>
</config>`,

    vlan: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <vlans xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-vlan">
    <vlan>
      <id>100</id>
      <name>DATA_VLAN</name>
      <status>active</status>
    </vlan>
    <vlan>
      <id>200</id>
      <name>VOICE_VLAN</name>
      <status>active</status>
    </vlan>
    <vlan>
      <id>300</id>
      <name>MGMT_VLAN</name>
      <status>active</status>
    </vlan>
  </vlans>
</config>`,

    staticRoute: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <routing xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-routing">
    <routing-instance xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-routing" xmlns:rv="http://cisco.com/ns/yang/Cisco-IOS-XE-routing">
      <name>default</name>
      <routing-protocols>
        <routing-protocol>
          <type>static</type>
          <name>1</name>
          <static-routes>
            <ipv4 xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-routing">
              <route>
                <destination-prefix>0.0.0.0/0</destination-prefix>
                <next-hop>
                  <address>203.0.113.1</address>
                  <route-preference>1</route-preference>
                </next-hop>
              </route>
              <route>
                <destination-prefix>192.168.100.0/24</destination-prefix>
                <next-hop>
                  <address>10.1.1.1</address>
                  <route-preference>1</route-preference>
                </next-hop>
              </route>
            </ipv4>
          </static-routes>
        </routing-protocol>
      </routing-protocols>
    </routing-instance>
  </routing>
</config>`,

    ntp: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <ntp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ntp">
    <server>
      <address>10.10.10.1</address>
      <association-type>server</association-type>
      <prefer>true</prefer>
    </server>
    <server>
      <address>10.10.10.2</address>
      <association-type>server</association-type>
      <prefer>false</prefer>
    </server>
    <server>
      <address>0.fr.pool.ntp.org</address>
      <association-type>server</association-type>
      <prefer>false</prefer>
    </server>
  </ntp>
</config>`,

    dns: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <dns xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-dns">
    <ipv4>
      <server>
        <ip-address>8.8.8.8</ip-address>
        <key/>
      </server>
      <server>
        <ip-address>8.8.4.4</ip-address>
        <key/>
      </server>
      <server>
        <ip-address>1.1.1.1</ip-address>
        <key/>
      </server>
    </ipv4>
    <domain>
      <name>network.local</name>
    </domain>
  </dns>
</config>`,

    banner: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <banner xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-banner">
    <banner-input>
      <type>login</type>
      <message>###############################################################################
# ACCES RESTREINT - RESEAU ENTREPRISE                                           #
#                                                                                #
# Ce systeme est reserve aux utilisateurs autorises. Toute connexion non autorisee #
# sera signalee et poursuitee conformement a la legislation en vigueur.           #
#                                                                                #
# Contact: admin@network.local | Urgence: +33 1 23 45 67 89                     #
###############################################################################</message>
    </banner-input>
    <banner-input>
      <type>motd</type>
      <message>========================================
Bienvenue sur l'equipement de production
Date: \\D \\T
Utilisateur: \\u
========================================</message>
    </banner-input>
  </banner>
</config>`,

    user: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <aaa xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-aaa">
    <userauthentication>
      <user>
        <name>netadmin</name>
        <privilege>15</privilege>
        <password>
          <encryption>5</encryption>
          <pass>$1$encrypted$hash</pass>
        </password>
      </user>
      <user>
        <name>operator</name>
        <privilege>7</privilege>
        <password>
          <encryption>5</encryption>
          <pass>$1$encrypted$hash</pass>
        </password>
      </user>
      <user>
        <name>monitoring</name>
        <privilege>5</privilege>
        <password>
          <encryption>5</encryption>
          <pass>$1$encrypted$hash</pass>
        </password>
      </user>
    </userauthentication>
  </aaa>
</config>`,

    snmp: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <snmp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-snmp">
    <community>
      <community-string>
        <name>public</name>
        <access-list>10</access-list>
        <view>readonly</view>
      </community-string>
      <community-string>
        <name>private</name>
        <access-list>10</access-list>
        <view>readwrite</view>
      </community-string>
    </community>
    <trap>
      <server>192.168.1.100</server>
      <community>public</community>
      <version>v2c</version>
    </trap>
    <location>Paris-DC-Rack01-POS01</location>
    <contact>admin@network.local | +33 1 23 45 67 89</contact>
    <chassis-id>CISCO-ISR-4331-K9</chassis-id>
  </snmp>
</config>`
};

// CISCO NX-OS NETCONF
const ciscoNxosNetconf = {
    interface: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="http://openconfig.net/yang/interfaces">
    <interface>
      <name> Ethernet1/1</name>
      <config>
        <description>Server Uplink - Production</description>
        <enabled>true</enabled>
        <mtu>9000</mtu>
      </config>
      <subinterfaces>
        <subinterface>
          <index>0</index>
          <config>
            <description>VLAN 100 - DATA</description>
            <enabled>true</enabled>
          </config>
        </subinterface>
      </subinterfaces>
    </interface>
  </interfaces>
</config>`,

    vlan: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <vlans xmlns="http://openconfig.net/yang/vlan">
    <vlan>
      <vlan-id>100</vlan-id>
      <config>
        <vlan-id>100</vlan-id>
        <name>PRODUCTION_DATA</name>
        <status>ACTIVE</status>
      </config>
    </vlan>
    <vlan>
      <vlan-id>200</vlan-id>
      <config>
        <vlan-id>200</vlan-id>
        <name>VOICE</name>
        <status>ACTIVE</status>
      </config>
    </vlan>
    <vlan>
      <vlan-id>999</vlan-id>
      <config>
        <vlan-id>999</vlan-id>
        <name>NATIVE</name>
        <status>ACTIVE</status>
      </config>
    </vlan>
  </vlans>
</config>`,

    staticRoute: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <routing-policy xmlns="http://openconfig.net/yang/routing-policy">
  </routing-policy>
</config>`,

    ntp: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <ntp xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
    <server>
      <address>10.10.10.1</address>
      <prefer>true</prefer>
    </server>
    <server>
      <address>10.10.10.2</address>
      <prefer>false</prefer>
    </server>
  </ntp>
</config>`,

    dns: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <ip xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
    <name-server>
      <address>8.8.8.8</address>
    </name-server>
    <name-server>
      <address>1.1.1.1</address>
    </name-server>
  </ip>
</config>`,

    banner: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <banner xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
    <motd-banner>#######################################################################
#                     RESEAU NATIONAL DE RECHERCHE                                 #
#                                                                                 #
#  Acces reserve aux personnels autorises. Toute tentative d'acces non autorise   #
#  est interdite et fera l'objet de poursuites conformement aux articles 323-1    #
#  et suivants du Code Penal.                                                    #
#                                                                                 #
#  En cas d'incident, contactez le NOC: noc@reseau.fr | 01 23 45 67 90          #
#######################################################################</motd-banner>
  </banner>
</config>`,

    user: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <aaa xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
    <authentication-login>
      <auth-mode>local</auth-mode>
    </authentication-login>
    <users>
      <user>
        <name>admin</name>
        <pwd>$1$encrypted$hash</pwd>
        <role>network-admin</role>
      </user>
      <user>
        <name>netops</name>
        <pwd>$1$encrypted$hash</pwd>
        <role>network-operator</role>
      </user>
      <user>
        <name>readonly</name>
        <pwd>$1$encrypted$hash</pwd>
        <role>vdc-operator</role>
      </user>
    </users>
  </aaa>
</config>`,

    snmp: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <snmp-server xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
    <community>public</community>
    <community>private</community>
    <trap-cluster>192.168.1.100</trap-cluster>
    <location>DataCenter-Paris-Rack01-SW01</location>
    <contact>noc@reseau.fr</contact>
  </snmp-server>
</config>`
};

// JUNIPER JUNOS NETCONF
const juniperJunosNetconf = {
    interface: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm" xmlns:junos="http://xml.juniper.net/junos/commit/1.1">
  <interfaces>
    <interface>
      <name>ge-0/0/0</name>
      <description>Uplink vers Routeur Core</description>
      <unit>
        <name>0</name>
        <family>
          <inet>
            <address>
              <name>10.10.10.2/30</name>
            </address>
          </inet>
        </family>
      </unit>
    </interface>
    <interface>
      <name>ge-0/0/1</name>
      <description>Downlink vers Access Switch</description>
      <mtu>9000</mtu>
      <unit>
        <name>0</name>
        <family>
          <ethernet-switching>
            <interface-mode>trunk</interface-mode>
            <vlan>
              <members>100</members>
              <members>200</members>
              <members>300</members>
            </vlan>
          </ethernet-switching>
        </family>
      </unit>
    </interface>
  </interfaces>
</config>`,

    vlan: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <vlans>
    <vlan>
      <name>PROD_DATA</name>
      <vlan-id>100</vlan-id>
      <description>VLAN Production Donnees</description>
      <l3-interface>vlan.100</l3-interface>
    </vlan>
    <vlan>
      <name>VOICE</name>
      <vlan-id>200</vlan-id>
      <description>VLAN Voix IP</description>
      <l3-interface>vlan.200</l3-interface>
    </vlan>
    <vlan>
      <name>MGMT</name>
      <vlan-id>300</vlan-id>
      <description>VLAN Management</description>
      <l3-interface>vlan.300</l3-interface>
    </vlan>
  </vlans>
</config>`,

    staticRoute: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <routing-options>
    <static>
      <route>
        <name>0.0.0.0/0</name>
        <next-table>inet.0</next-table>
        <qualified-next-hop>
          <address>10.10.10.1</address>
          <preference>1</preference>
        </qualified-next-hop>
      </route>
      <route>
        <name>192.168.0.0/16</name>
        <next-hop>10.1.1.1</next-hop>
        <preference>10</preference>
      </route>
      <route>
        <name>10.0.0.0/8</name>
        <next-hop>10.10.10.1</next-hop>
        <preference>5</preference>
      </route>
    </static>
  </routing-options>
</config>`,

    ntp: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <system>
    <ntp>
      <boot-server>10.10.10.1</boot-server>
      <server>
        <name>10.10.10.1</name>
        <prefer/>
      </server>
      <server>
        <name>10.10.10.2</name>
      </server>
      <server>
        <name>0.fr.pool.ntp.org</name>
      </server>
      <server>
        <name>1.fr.pool.ntp.org</name>
      </server>
    </ntp>
  </system>
</config>`,

    dns: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <system>
    <name-server>
      <address>8.8.8.8</address>
    </name-server>
    <name-server>
      <address>8.8.4.4</address>
    </name-server>
    <name-server>
      <address>1.1.1.1</address>
    </name-server>
    <domain-name>juniper.local</domain-name>
    <domain-search>
      <list>network.local</list>
      <list>entreprise.fr</list>
    </domain-search>
  </system>
</config>`,

    banner: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <system>
    <login>
      <banner>
        <message>################################################################################
#                                                                                #
#          ACCES AUTORISE UNIQUEMENT - SYSTEME PROTEGE                            #
#                                                                                #
#  Ce systeme appartient a l'entreprise et son utilisation est reservee aux       #
#  employs autorises. Toute tentative d'acces non autorisee constitue une        #
#  infraction penale et sera signalee aux autorites competentes.                 #
#                                                                                #
#  Contact Securite: security@entreprise.fr | Urgence: 01 23 45 67 89           #
#                                                                                #
################################################################################</message>
      </banner>
      <announcement>
<message>================================================================================
              Bienvenue sur l'equipement Juniper - $(hostname)
              Version Junos: $(version)
              Derniere connexion: $(time)
================================================================================</message>
      </announcement>
    </login>
  </system>
</config>`,

    user: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <system>
    <login>
      <user>
        <name>admin</name>
        <uid>2000</uid>
        <class>super-user</class>
        <authentication>
          <encrypted-password>$1$encrypted$hash</encrypted-password>
        </authentication>
      </user>
      <user>
        <name>netadmin</name>
        <uid>2001</uid>
        <class>operator</class>
        <authentication>
          <encrypted-password>$1$encrypted$hash</encrypted-password>
        </authentication>
      </user>
      <user>
        <name>monitoring</name>
        <uid>2002</uid>
        <class>read-only</class>
        <authentication>
          <ssh-rsa>
            <name>ssh-rsa AAAAB3NzaC1... user@monitoring</name>
          </ssh-rsa>
        </authentication>
      </user>
    </login>
  </system>
</config>`,

    snmp: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.juniper.net/xnm/1.1/xnm">
  <snmp>
    <location>Paris-DC-Rack01-vMX-01</location>
    <contact>admin@juniper.local</contact>
    <community>
      <name>public</name>
      <authorization>read-only</authorization>
    </community>
    <community>
      <name>private</name>
      <authorization>read-write</authorization>
    </community>
    <trap-group>
      <name>NOC-TRAPS</name>
      <destination-address>
        <name>192.168.1.100</name>
      </destination-address>
      <destination-address>
        <name>192.168.1.101</name>
      </destination-address>
    </trap-group>
  </snmp>
</config>`
};

// ARUBA AOS-S NETCONF
const arubaAosNetconf = {
    interface: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <interface>
      <name>1/1/1</name>
      <config>
        <description>Uplink vers Distribution</description>
        <type gigabitethernet/>
      </config>
      <subinterface>
        <id>0</id>
        <ipv4>
          <address>
            <ip>10.10.20.2</ip>
            <prefix-length>30</prefix-length>
          </address>
        </ipv4>
      </subinterface>
    </interface>
    <interface>
      <name>1/1/2</name>
      <config>
        <description>Port Access User</description>
        <type gigabitethernet/>
      </config>
    </interface>
  </interfaces>
</config>`,

    vlan: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <vlans xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <vlan>
      <id>100</id>
      <name>CORP_DATA</name>
    </vlan>
    <vlan>
      <id>200</id>
      <name>CORP_VOICE</name>
    </vlan>
    <vlan>
      <id>300</id>
      <name>CORP_MGMT</name>
    </vlan>
  </vlans>
</config>`,

    staticRoute: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <routing xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <static-routes>
      <ipv4>
        <route>
          <prefix>0.0.0.0/0</prefix>
          <next-hop>10.10.20.1</next-hop>
        </route>
        <route>
          <prefix>172.16.0.0/12</prefix>
          <next-hop>10.10.20.1</next-hop>
        </route>
      </ipv4>
    </static-routes>
  </routing>
</config>`,

    ntp: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <system xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <ntp>
      <server>
        <address>10.10.10.1</address>
        <prefer>true</prefer>
      </server>
      <server>
        <address>10.10.10.2</address>
      </server>
    </ntp>
  </system>
</config>`,

    dns: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <system xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <dns>
      <server>
        <address>8.8.8.8</address>
      </server>
      <server>
        <address>1.1.1.1</address>
      </server>
    </dns>
    <domain-name>aruba.local</domain-name>
  </system>
</config>`,

    banner: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <system xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <banners>
      <login>
<message>##############################################################################
#                                                                            #
#   ACCES RESTREINT - RESEAU D'ENTREPRISE ARUBA                              #
#                                                                            #
#   Cet equipement est reserve aux personnalites autorisees.                  #
#   Toutes activites non autorisees seront signalees.                         #
#                                                                            #
##############################################################################</message>
      </login>
    </banners>
  </system>
</config>`,

    user: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <system xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <aaa>
      <authentication>
        <user>
          <name>admin</name>
          <password>$1$encrypted$hash</password>
          <role>superuser</role>
        </user>
        <user>
          <name>netop</name>
          <password>$1$encrypted$hash</password>
          <role>manager</role>
        </user>
        <user>
          <name>guest</name>
          <password>$1$encrypted$hash</password>
          <role>guest</role>
        </user>
      </authentication>
    </aaa>
  </system>
</config>`,

    snmp: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <snmp xmlns="http://www.arubanetworks.com/yang/1.0/aruba-webui">
    <community>
      <name>public</name>
      <access-mode>read-only</access-mode>
    </community>
    <community>
      <name>private</name>
      <access-mode>read-write</access-mode>
    </community>
    <location>Aruba-SW-5400-Paris-Floor1</location>
    <contact>admin@aruba.local</contact>
  </snmp>
</config>`
};

// FORTINET FORTIOS NETCONF
const fortinetFortiosNetconf = {
    interface: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <system>
    <interface>
      <name>port1</name>
      <vdom>root</vdom>
      <ip>10.10.10.1 255.255.255.0</ip>
      <description>WAN -连接到ISP</description>
      <alias>WAN-UPLINK</alias>
      <芒聙聹ype>physical</芒聙聹ype>
      <芒聙聹tatus>up</芒聙聹tatus>
      <芒聙聹芒聙聹>9000</芒聙聹芒聙聹>
    </interface>
    <interface>
      <name>port2</name>
      <vdom>root</vdom>
      <ip>192.168.1.1 255.255.255.0</ip>
      <description>LAN - Internal Network</description>
      <alias>LAN-INTERNAL</alias>
      <芒聙聹ype>physical</芒聙聹ype>
      <芒聙聹tatus>up</芒聙聹tatus>
    </interface>
    <interface>
      <name>port3</name>
      <vdom>root</vdom>
      <description>DMZ - Serveurs</description>
      <alias>DMZ-SERVERS</alias>
      <芒聙聹ype>physical</芒聙聹ype>
      <芒聙聹tatus>up</芒聙聹tatus>
    </interface>
  </system>
</config>`,

    vlan: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <system>
    <interface>
      <name>vlan100</name>
      <vdom>root</vdom>
      <芒聙聹ype>vlan</芒聙聹ype>
      <芒聙聹tatus>up</芒聙聹tatus>
      <ip>192.168.100.1 255.255.255.0</ip>
      <description>DATA_VLAN</description>
      <vlanid>100</vlanid>
      <interface>port2</interface>
    </interface>
    <interface>
      <name>vlan200</name>
      <vdom>root</vdom>
      <芒聙聹ype>vlan</芒聙聹ype>
      <芒聙聹tatus>up</芒聙聹tatus>
      <ip>192.168.200.1 255.255.255.0</ip>
      <description>VOICE_VLAN</description>
      <vlanid>200</vlanid>
      <interface>port2</interface>
    </interface>
  </system>
</config>`,

    staticRoute: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <router>
    <static>
      <seq-num>
        <id>1</id>
        <dst>0.0.0.0 0.0.0.0</dst>
        <gateway>10.10.10.254</gateway>
        <device>port1</device>
        <distance>10</distance>
        <priority>0</priority>
        <芒聙聹atus>enable</芒聙聹atus>
      </seq-num>
      <seq-num>
        <id>2</id>
        <dst>192.168.50.0 255.255.255.0</dst>
        <gateway>192.168.1.254</gateway>
        <device>port2</device>
        <distance>10</distance>
      </seq-num>
      <seq-num>
        <id>3</id>
        <dst>10.0.0.0 255.0.0.0</dst>
        <gateway>10.10.10.1</gateway>
        <device>port1</device>
        <distance>5</distance>
      </seq-num>
    </static>
  </router>
</config>`,

    ntp: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <system>
    <ntpserver>
      <ntpserver-1>
        <server>10.10.10.1</server>
        <id>1</id>
        <prefer>enable</prefer>
        <status>enable</status>
      </ntpserver-1>
      <ntpserver-2>
        <server>10.10.10.2</server>
        <id>2</id>
        <status>enable</status>
      </ntpserver-2>
      <ntpserver-3>
        <server>0.fr.pool.ntp.org</server>
        <id>3</id>
        <status>enable</status>
      </ntpserver-3>
    </ntpserver>
    <ntp>
      <sync-interval>60</sync-interval>
    </ntp>
  </system>
</config>`,

    dns: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <system>
    <dns>
      <primary>8.8.8.8</primary>
      <secondary>8.8.4.4</secondary>
      <tertiary>1.1.1.1</tertiary>
    </dns>
    <dnsfilter>
      <dns-cache>enable</dns-cache>
    </dnsfilter>
  </system>
</config>`,

    banner: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <system>
    <custom>
      <login-page>
<message>################################################################################
#                                                                                #
#                    RESEAU SECURISE - ACCES RESTREINT                            #
#                                                                                #
#  Ce reseau est surveille et protege. Tout acces non autorise est interdit       #
#  et fera l'objet de poursuites conformement a la legislation en vigueur.       #
#                                                                                #
#  Centre de Supervision: noc@fortinet.local | Tel: 01 23 45 67 89               #
#                                                                                #
################################################################################</message>
      </login-page>
    </custom>
  </system>
</config>`,

    user: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <user>
    <local>
      <name>admin</name>
      <type>password</type>
      <passwd>$1$encrypted$hash</passwd>
      <profile>super_admin</profile>
      <two-factor>disable</two-factor>
    </local>
    <local>
      <name>netadmin</name>
      <type>password</type>
      <passwd>$1$encrypted$hash</passwd>
      <profile>prof_admin</profile>
    </local>
    <local>
      <name>guest</name>
      <type>password</type>
      <passwd>$1$encrypted$hash</passwd>
      <profile>guest_admin</profile>
    </local>
  </user>
  <user>
    <group>
      <name>network-admins</name>
      <芒聙聹ype>firewall</芒聙聹ype>
      <member>admin</member>
      <member>netadmin</member>
    </group>
  </user>
</config>`,

    snmp: `<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="http://xml.fortinet.com/2012/05/xsd">
  <system>
    <snmp>
      <sysinfo>
        <status>enable</status>
        <location>Paris-DC-FW-01</location>
        <contact>admin@fortinet.local</contact>
      </sysinfo>
      <community>
        <name>public</name>
        <id>1</id>
        <芒聙聹ype>v1v2c</芒聙聹ype>
        <hosts>
          <host>
            <id>1</id>
            <ip>192.168.1.100 255.255.255.255</ip>
          </host>
        </hosts>
      </community>
      <community>
        <name>private</name>
        <id>2</id>
        <芒聙聹ype>v1v2c</芒聙聹ype>
        <hosts>
          <host>
            <id>1</id>
            <ip>192.168.1.100 255.255.255.255</ip>
          </host>
        </hosts>
      </community>
      <v3rc>
        <mode>尊上</mode>
      </v3rc>
    </snmp>
  </system>
</config>`
};

// Export all templates
const netconfTemplates = {
    cisco: {
        'ios-xe': ciscoIosxeNetconf,
        'nxos': ciscoNxosNetconf
    },
    juniper: {
        'junos': juniperJunosNetconf
    },
    aruba: {
        'eos': arubaAosNetconf
    },
    fortinet: {
        'fortios': fortinetFortiosNetconf
    }
};

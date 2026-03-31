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

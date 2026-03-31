from typing import Optional


class ConfigBuilder:
    CISCO_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-native"

    @staticmethod
    def wrap_in_config(xml_content: str) -> str:
        return f'<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">{xml_content}</config>'

    @staticmethod
    def _vlan_list(vlan_id: int, name: str, description: Optional[str] = None) -> str:
        desc_xml = f"<name>{name}</name>"
        if description:
            desc_xml += f"<desc>{description}</desc>"
        return f"<vlan-list><id>{vlan_id}</id>{desc_xml}</vlan-list>"

    def build_vlan_create(self, vlan_id: int, name: str, description: Optional[str] = None) -> str:
        xml = f"""<native xmlns="{self.CISCO_NS}"><vlan>{self._vlan_list(vlan_id, name, description)}</vlan></native>"""
        return self.wrap_in_config(xml)

    def build_vlan_delete(self, vlan_id: int) -> str:
        xml = f"""<native xmlns="{self.CISCO_NS}"><vlan><vlan-list operation="delete"><id>{vlan_id}</id></vlan-list></vlan></native>"""
        return self.wrap_in_config(xml)

    def build_vlan_update(self, vlan_id: int, name: str, description: Optional[str] = None) -> str:
        return self.build_vlan_create(vlan_id, name, description)

    def build_interface_create(
        self,
        interface_name: str,
        description: Optional[str] = None,
        enabled: bool = True,
        ip_address: Optional[str] = None,
        subnet_mask: Optional[str] = None,
        vlan_id: Optional[int] = None,
        port_mode: str = "access"
    ) -> str:
        intf_type = self._get_interface_type(interface_name)
        intf_id = self._get_interface_id(interface_name)

        desc_xml = f"<description>{description}</description>" if description else ""
        # Sur certains IOS-XE, une interface (notamment SVI) peut rester en "shutdown"
        # si on ne précise pas explicitement l'état. On force donc l'état voulu.
        shutdown_xml = "<no><shutdown/></no>" if enabled else "<shutdown/>"

        ip_xml = ""
        if ip_address and subnet_mask:
            mask_bits = self._subnet_mask_to_bits(subnet_mask)
            ip_xml = f"<ip><address><primary><address>{ip_address}</address><mask>{mask_bits}</mask></primary></address></ip>"

        vlan_xml = ""
        if vlan_id:
            if port_mode == "access":
                vlan_xml = f"<switchport><access><vlan><vlan>{vlan_id}</vlan></vlan></access></switchport>"
            elif port_mode == "trunk":
                vlan_xml = f"<switchport><trunk><allowed><vlan><vlan>{vlan_id}</vlan></vlan></allowed></trunk></switchport>"

        xml = f"""<native xmlns="{self.CISCO_NS}"><interface><{intf_type}><name>{intf_id}</name>{desc_xml}{shutdown_xml}{ip_xml}{vlan_xml}</{intf_type}></interface></native>"""
        return self.wrap_in_config(xml)

    def build_interface_delete(self, interface_name: str) -> str:
        intf_type = self._get_interface_type(interface_name)
        intf_id = self._get_interface_id(interface_name)
        xml = f"""<native xmlns="{self.CISCO_NS}"><interface><{intf_type} operation="delete"><name>{intf_id}</name></{intf_type}></interface></native>"""
        return self.wrap_in_config(xml)

    def build_interface_ip(self, interface_name: str, ip_address: str, subnet_mask: str) -> str:
        intf_type = self._get_interface_type(interface_name)
        intf_id = self._get_interface_id(interface_name)
        mask_bits = self._subnet_mask_to_bits(subnet_mask)
        xml = f"""<native xmlns="{self.CISCO_NS}"><interface><{intf_type}><name>{intf_id}</name><ip><address><primary><address>{ip_address}</address><mask>{mask_bits}</mask></primary></address></ip></{intf_type}></interface></native>"""
        return self.wrap_in_config(xml)

    def build_interface_shutdown(self, interface_name: str, shutdown: bool = True) -> str:
        intf_type = self._get_interface_type(interface_name)
        intf_id = self._get_interface_id(interface_name)
        shutdown_xml = "<shutdown/>" if shutdown else "<no><shutdown/></no>"
        xml = f"""<native xmlns="{self.CISCO_NS}"><interface><{intf_type}><name>{intf_id}</name>{shutdown_xml}</{intf_type}></interface></native>"""
        return self.wrap_in_config(xml)

    def build_bgp_router(self, local_as: int, router_id: Optional[str] = None) -> str:
        router_id_xml = f"<router-id>{router_id}</router-id>" if router_id else ""
        xml = f"""<native xmlns="{self.CISCO_NS}"><router><bgp><as-native><as>{local_as}</as>{router_id_xml}</as-native></bgp></router></native>"""
        return self.wrap_in_config(xml)

    def build_bgp_neighbor(
        self,
        local_as: int,
        neighbor_ip: str,
        remote_as: int,
        description: Optional[str] = None,
        enabled: bool = True
    ) -> str:
        desc_xml = f"<description>{description}</description>" if description else ""
        xml = f"""<native xmlns="{self.CISCO_NS}"><router><bgp><as-native><as>{local_as}</as><neighbor><id>{neighbor_ip}</id><remote-as>{remote_as}</remote-as>{desc_xml}</neighbor></as-native></bgp></router></native>"""
        return self.wrap_in_config(xml)

    def build_bgp_neighbor_delete(self, local_as: int, neighbor_ip: str) -> str:
        xml = f"""<native xmlns="{self.CISCO_NS}"><router><bgp><as-native><as>{local_as}</as><neighbor operation="delete"><id>{neighbor_ip}</id></neighbor></as-native></bgp></router></native>"""
        return self.wrap_in_config(xml)

    def build_ospf_process(
        self,
        process_id: int,
        router_id: Optional[str] = None,
        area_id: int = 0,
        network: Optional[str] = None,
        wildcard: Optional[str] = None
    ) -> str:
        router_id_xml = f"<router-id>{router_id}</router-id>" if router_id else ""
        network_xml = ""
        if network and wildcard:
            network_xml = f"<network><ip>{network}</ip><wildcard>{wildcard}</wildcard><area>{area_id}</area></network>"
        xml = f"""<native xmlns="{self.CISCO_NS}"><router><ospf><ospf><process><id>{process_id}</id>{router_id_xml}{network_xml}</process></ospf></ospf></router></native>"""
        return self.wrap_in_config(xml)

    def build_ospf_network(self, process_id: int, network: str, wildcard: str, area_id: int) -> str:
        xml = f"""<native xmlns="{self.CISCO_NS}"><router><ospf><ospf><process><id>{process_id}</id><network><ip>{network}</ip><wildcard>{wildcard}</wildcard><area>{area_id}</area></network></process></ospf></ospf></router></native>"""
        return self.wrap_in_config(xml)

    def build_ospf_delete(self, process_id: int) -> str:
        xml = f"""<native xmlns="{self.CISCO_NS}"><router><ospf><ospf><process operation="delete"><id>{process_id}</id></process></ospf></ospf></router></native>"""
        return self.wrap_in_config(xml)

    def build_ip_routing_enable(self) -> str:
        # Active le routage IP sur l'équipement (utile pour l'inter-VLAN routing via SVIs).
        xml = f"""<native xmlns="{self.CISCO_NS}"><ip><routing/></ip></native>"""
        return self.wrap_in_config(xml)

    @staticmethod
    def _get_interface_type(interface_name: str) -> str:
        type_map = {
            "GigabitEthernet": "GigabitEthernet",
            "FastEthernet": "FastEthernet",
            "TenGigabitEthernet": "TenGigabitEthernet",
            "Ethernet": "Ethernet",
            "Loopback": "Loopback",
            "Vlan": "Vlan",
            "Port-channel": "Port-channel",
            "Tunnel": "Tunnel",
            "Serial": "Serial",
        }
        for prefix, interface_type in type_map.items():
            if interface_name.startswith(prefix):
                return interface_type
        return "Loopback"

    @staticmethod
    def _get_interface_id(interface_name: str) -> str:
        # Pour les interfaces VlanX, Cisco attend généralement uniquement l'ID numérique.
        # Exemple: "Vlan10" -> "10"
        if interface_name.startswith("Vlan"):
            return interface_name.replace("Vlan", "", 1) or interface_name

        parts = interface_name.split(" ")
        return parts[0] if parts else interface_name

    @staticmethod
    def _subnet_mask_to_bits(mask: str) -> str:
        mask_map = {
            "255.255.255.255": "/32",
            "255.255.255.254": "/31",
            "255.255.255.252": "/30",
            "255.255.255.248": "/29",
            "255.255.255.240": "/28",
            "255.255.255.224": "/27",
            "255.255.255.192": "/26",
            "255.255.255.128": "/25",
            "255.255.255.0": "/24",
            "255.255.254.0": "/23",
            "255.255.252.0": "/22",
            "255.255.248.0": "/21",
            "255.255.240.0": "/20",
            "255.255.224.0": "/19",
            "255.255.192.0": "/18",
            "255.255.128.0": "/17",
            "255.255.0.0": "/16",
            "255.254.0.0": "/15",
            "255.252.0.0": "/14",
            "255.248.0.0": "/13",
            "255.240.0.0": "/12",
            "255.224.0.0": "/11",
            "255.192.0.0": "/10",
            "255.128.0.0": "/9",
            "255.0.0.0": "/8",
            "254.0.0.0": "/7",
            "252.0.0.0": "/6",
            "248.0.0.0": "/5",
            "240.0.0.0": "/4",
            "224.0.0.0": "/3",
            "192.0.0.0": "/2",
            "128.0.0.0": "/1",
            "0.0.0.0": "/0",
        }
        if mask.startswith("/"):
            return mask
        return mask_map.get(mask, mask)

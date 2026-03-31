import pytest
from app.services.config_builder import ConfigBuilder


class TestConfigBuilder:
    def setup_method(self):
        self.builder = ConfigBuilder()

    def test_build_vlan_create(self):
        xml = self.builder.build_vlan_create(
            vlan_id=100,
            name="CLIENT-FINANCE",
            description="VLAN pour le département finance"
        )
        assert "<id>100</id>" in xml
        assert "<name>CLIENT-FINANCE</name>" in xml
        assert "native" in xml

    def test_build_interface_create_basic(self):
        xml = self.builder.build_interface_create(
            interface_name="GigabitEthernet0/0",
            description="Interface WAN",
            enabled=True
        )
        assert "GigabitEthernet" in xml
        assert "<description>Interface WAN</description>" in xml

    def test_build_interface_with_ip(self):
        xml = self.builder.build_interface_create(
            interface_name="GigabitEthernet0/0",
            ip_address="192.168.1.1",
            subnet_mask="255.255.255.0",
            enabled=True
        )
        assert "<address>192.168.1.1</address>" in xml
        assert "native" in xml

    def test_build_interface_with_vlan_access(self):
        xml = self.builder.build_interface_create(
            interface_name="GigabitEthernet0/1",
            vlan_id=100,
            port_mode="access"
        )
        assert "<vlan>100</vlan>" in xml
        assert "switchport" in xml

    def test_build_interface_with_vlan_trunk(self):
        xml = self.builder.build_interface_create(
            interface_name="GigabitEthernet0/1",
            vlan_id=100,
            port_mode="trunk"
        )
        assert "<vlan>100</vlan>" in xml
        assert "trunk" in xml

    def test_build_bgp_router(self):
        xml = self.builder.build_bgp_router(
            local_as=65001,
            router_id="10.0.0.1"
        )
        assert "<as>65001</as>" in xml
        assert "<router-id>10.0.0.1</router-id>" in xml

    def test_build_bgp_neighbor(self):
        xml = self.builder.build_bgp_neighbor(
            local_as=65001,
            neighbor_ip="192.168.1.2",
            remote_as=65002,
            description="Peer to Client A"
        )
        assert "<as>65001</as>" in xml
        assert "<id>192.168.1.2</id>" in xml
        assert "<remote-as>65002</remote-as>" in xml

    def test_build_ospf_process(self):
        xml = self.builder.build_ospf_process(
            process_id=1,
            router_id="10.0.0.1",
            area_id=0,
            network="192.168.0.0",
            wildcard="0.0.255.255"
        )
        assert "<id>1</id>" in xml
        assert "<area>0</area>" in xml

    def test_subnet_mask_to_bits(self):
        assert self.builder._subnet_mask_to_bits("255.255.255.0") == "/24"
        assert self.builder._subnet_mask_to_bits("255.255.0.0") == "/16"
        assert self.builder._subnet_mask_to_bits("/24") == "/24"

    def test_get_interface_type(self):
        assert self.builder._get_interface_type("GigabitEthernet0/0") == "GigabitEthernet"
        assert self.builder._get_interface_type("Loopback0") == "Loopback"
        assert self.builder._get_interface_type("Vlan100") == "Vlan"
        assert self.builder._get_interface_type("Port-channel1") == "Port-channel"


class TestNETCONFClientMock:
    def test_client_initialization(self):
        from app.services.netconf_client import NETCONFClient
        client = NETCONFClient(
            host="192.168.1.1",
            port=830,
            username="admin",
            password="password"
        )
        assert client.host == "192.168.1.1"
        assert client.port == 830
        assert client.username == "admin"
        assert not client.is_connected()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

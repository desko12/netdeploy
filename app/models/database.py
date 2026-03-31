from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class RouterStatus(str, enum.Enum):
    ACTIVE = "active"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    UNKNOWN = "unknown"


class InterfaceStatus(str, enum.Enum):
    UP = "up"
    DOWN = "down"
    DISABLED = "disabled"


class PortMode(str, enum.Enum):
    ACCESS = "access"
    TRUNK = "trunk"


class ConfigAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class ConfigStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class Router(Base):
    __tablename__ = "routers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    hostname = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=False, index=True)
    netconf_port = Column(Integer, default=830)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    device_type = Column(String(50), default="cisco_iosxe")
    default_vlan = Column(Integer, default=1)
    status = Column(SQLEnum(RouterStatus), default=RouterStatus.UNKNOWN)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vlans = relationship("VLAN", back_populates="router", cascade="all, delete-orphan")
    interfaces = relationship("Interface", back_populates="router", cascade="all, delete-orphan")
    bgp_configs = relationship("BGPConfig", back_populates="router", cascade="all, delete-orphan")
    ospf_configs = relationship("OSPFConfig", back_populates="router", cascade="all, delete-orphan")
    config_logs = relationship("ConfigLog", back_populates="router", cascade="all, delete-orphan")


class VLAN(Base):
    __tablename__ = "vlans"

    id = Column(Integer, primary_key=True, index=True)
    router_id = Column(Integer, ForeignKey("routers.id", ondelete="CASCADE"), nullable=False)
    vlan_id = Column(Integer, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    subnet_mask = Column(String(45), nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    router = relationship("Router", back_populates="vlans")
    interfaces = relationship("Interface", back_populates="vlan")


class Interface(Base):
    __tablename__ = "interfaces"

    id = Column(Integer, primary_key=True, index=True)
    router_id = Column(Integer, ForeignKey("routers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True)
    ip_address = Column(String(45), nullable=True)
    subnet_mask = Column(String(45), nullable=True)
    vlan_id = Column(Integer, ForeignKey("vlans.id", ondelete="SET NULL"), nullable=True)
    duplex = Column(String(20), default="auto")
    speed = Column(String(20), default="auto")
    port_mode = Column(SQLEnum(PortMode), default=PortMode.ACCESS)
    port_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    router = relationship("Router", back_populates="interfaces")
    vlan = relationship("VLAN", back_populates="interfaces")


class BGPConfig(Base):
    __tablename__ = "bgp_configs"

    id = Column(Integer, primary_key=True, index=True)
    router_id = Column(Integer, ForeignKey("routers.id", ondelete="CASCADE"), nullable=False)
    local_as = Column(Integer, nullable=False)
    router_id_address = Column(String(45), nullable=True)
    neighbor_ip = Column(String(45), nullable=False)
    neighbor_as = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    router = relationship("Router", back_populates="bgp_configs")


class OSPFConfig(Base):
    __tablename__ = "ospf_configs"

    id = Column(Integer, primary_key=True, index=True)
    router_id = Column(Integer, ForeignKey("routers.id", ondelete="CASCADE"), nullable=False)
    process_id = Column(Integer, nullable=False)
    router_id_address = Column(String(45), nullable=True)
    area_id = Column(Integer, nullable=False, default=0)
    network = Column(String(45), nullable=False)
    wildcard = Column(String(45), nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    router = relationship("Router", back_populates="ospf_configs")


class ConfigLog(Base):
    __tablename__ = "config_logs"

    id = Column(Integer, primary_key=True, index=True)
    router_id = Column(Integer, ForeignKey("routers.id", ondelete="CASCADE"), nullable=False)
    action = Column(SQLEnum(ConfigAction), nullable=False)
    config_type = Column(String(50), nullable=False)
    config_data = Column(Text, nullable=True)
    netconf_response = Column(Text, nullable=True)
    status = Column(SQLEnum(ConfigStatus), default=ConfigStatus.PENDING)
    user = Column(String(255), default="system")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    router = relationship("Router", back_populates="config_logs")

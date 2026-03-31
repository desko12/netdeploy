from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RouterStatus(str, Enum):
    ACTIVE = "active"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    UNKNOWN = "unknown"


class PortMode(str, Enum):
    ACCESS = "access"
    TRUNK = "trunk"


class ConfigAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class ConfigStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class RouterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    hostname: Optional[str] = Field(None, max_length=255)
    ip_address: str = Field(..., min_length=1, max_length=45)
    netconf_port: int = Field(default=830, ge=1, le=65535)
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=255)
    device_type: str = Field(default="cisco_iosxe", max_length=50)
    default_vlan: int = Field(default=1, ge=1, le=4094)
    location: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None

    @field_validator('ip_address')
    @classmethod
    def validate_ip(cls, v: str) -> str:
        parts = v.split('.')
        if len(parts) != 4:
            if ':' not in v:
                raise ValueError('Invalid IP address format')
        return v


class RouterCreate(RouterBase):
    pass


class RouterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    hostname: Optional[str] = Field(None, max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)
    netconf_port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, max_length=255)
    device_type: Optional[str] = Field(None, max_length=50)
    default_vlan: Optional[int] = Field(None, ge=1, le=4094)
    location: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class RouterResponse(RouterBase):
    id: int
    status: RouterStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RouterDetail(RouterResponse):
    vlans: List["VLANResponse"] = []
    interfaces: List["InterfaceResponse"] = []
    bgp_configs: List["BGPConfigResponse"] = []
    ospf_configs: List["OSPFConfigResponse"] = []


class VLANBase(BaseModel):
    vlan_id: int = Field(..., ge=1, le=4094)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    subnet_mask: Optional[str] = Field(None, max_length=45)
    status: str = Field(default="active")


class VLANCreate(VLANBase):
    router_id: int


class VLANUpdate(BaseModel):
    vlan_id: Optional[int] = Field(None, ge=1, le=4094)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    subnet_mask: Optional[str] = Field(None, max_length=45)
    status: Optional[str] = None


class VLANResponse(VLANBase):
    id: int
    router_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterfaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    enabled: bool = True
    ip_address: Optional[str] = Field(None, max_length=45)
    subnet_mask: Optional[str] = Field(None, max_length=45)
    vlan_id: Optional[int] = None
    duplex: str = Field(default="auto", max_length=20)
    speed: str = Field(default="auto", max_length=20)
    port_mode: PortMode = PortMode.ACCESS
    port_type: Optional[str] = Field(None, max_length=50)


class InterfaceCreate(InterfaceBase):
    router_id: int


class InterfaceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    enabled: Optional[bool] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    subnet_mask: Optional[str] = Field(None, max_length=45)
    vlan_id: Optional[int] = None
    duplex: Optional[str] = Field(None, max_length=20)
    speed: Optional[str] = Field(None, max_length=20)
    port_mode: Optional[PortMode] = None
    port_type: Optional[str] = Field(None, max_length=50)


class InterfaceResponse(InterfaceBase):
    id: int
    router_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BGPConfigBase(BaseModel):
    local_as: int = Field(..., ge=1, le=65535)
    router_id_address: Optional[str] = Field(None, max_length=45)
    neighbor_ip: str = Field(..., max_length=45)
    neighbor_as: int = Field(..., ge=1, le=4294967295)
    description: Optional[str] = None
    enabled: bool = True


class BGPConfigCreate(BGPConfigBase):
    router_id: int


class BGPConfigUpdate(BaseModel):
    local_as: Optional[int] = Field(None, ge=1, le=65535)
    router_id_address: Optional[str] = Field(None, max_length=45)
    neighbor_ip: Optional[str] = Field(None, max_length=45)
    neighbor_as: Optional[int] = Field(None, ge=1, le=4294967295)
    description: Optional[str] = None
    enabled: Optional[bool] = None


class BGPConfigResponse(BGPConfigBase):
    id: int
    router_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OSPFConfigBase(BaseModel):
    process_id: int = Field(..., ge=1, le=65535)
    router_id_address: Optional[str] = Field(None, max_length=45)
    area_id: int = Field(default=0, ge=0, le=4294967295)
    network: str = Field(..., max_length=45)
    wildcard: str = Field(..., max_length=45)
    description: Optional[str] = None
    enabled: bool = True


class OSPFConfigCreate(OSPFConfigBase):
    router_id: int


class OSPFConfigUpdate(BaseModel):
    process_id: Optional[int] = Field(None, ge=1, le=65535)
    router_id_address: Optional[str] = Field(None, max_length=45)
    area_id: Optional[int] = Field(None, ge=0, le=4294967295)
    network: Optional[str] = Field(None, max_length=45)
    wildcard: Optional[str] = Field(None, max_length=45)
    description: Optional[str] = None
    enabled: Optional[bool] = None


class OSPFConfigResponse(OSPFConfigBase):
    id: int
    router_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfigLogResponse(BaseModel):
    id: int
    router_id: int
    action: ConfigAction
    config_type: str
    config_data: Optional[str] = None
    netconf_response: Optional[str] = None
    status: ConfigStatus
    user: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NETCONFTestRequest(BaseModel):
    ip_address: str
    port: int = 830
    username: str
    password: str


class NETCONFTestResponse(BaseModel):
    success: bool
    message: str
    device_info: Optional[dict] = None


class ApplyConfigRequest(BaseModel):
    action: ConfigAction


RouterDetail.model_rebuild()

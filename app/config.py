from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "NETCONF Router Manager"
    app_version: str = "1.0.0"
    debug: bool = True
    
    database_url: str = "sqlite+aiosqlite:///./netconf_manager.db"
    
    default_netconf_port: int = 830
    default_device_type: str = "cisco_iosxe"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

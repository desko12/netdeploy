import logging
from typing import Optional, Dict, Any
from ncclient import manager
from ncclient.operations import RPCError
from ncclient.transport.errors import SSHError, AuthenticationError

logger = logging.getLogger(__name__)


class NETCONFClient:
    def __init__(
        self,
        host: str,
        port: int = 830,
        username: str = "",
        password: str = "",
        device_type: str = "cisco_iosxe",
        timeout: int = 30
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.device_type = device_type
        self.timeout = timeout
        self._manager: Optional[manager.Manager] = None

    def connect(self) -> tuple[bool, str]:
        try:
            self._manager = manager.connect(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                hostkey_verify=False,
                timeout=self.timeout,
                allow_agent=False,
                look_for_keys=False
            )
            logger.info(f"Connected to {self.host}:{self.port}")
            return True, "Connection successful"
        except AuthenticationError as e:
            logger.error(f"Authentication failed for {self.host}: {e}")
            return False, f"Authentication failed: {str(e)}"
        except SSHError as e:
            logger.error(f"SSH error connecting to {self.host}: {e}")
            return False, f"SSH connection error: {str(e)}"
        except Exception as e:
            logger.error(f"Error connecting to {self.host}: {e}")
            return False, f"Connection error: {str(e)}"

    def disconnect(self):
        if self._manager:
            self._manager.close_session()
            self._manager = None
            logger.info(f"Disconnected from {self.host}")

    def is_connected(self) -> bool:
        return self._manager is not None and self._manager.connected

    def get_config(self, filter_type: str = "subtree", filter_xml: Optional[str] = None) -> tuple[bool, str]:
        if not self.is_connected():
            return False, "Not connected"

        try:
            if filter_xml:
                config = self._manager.get_config(
                    source="running",
                    filter=("subtree", filter_xml)
                ).data_xml
            else:
                config = self._manager.get_config(source="running").data_xml
            return True, config
        except RPCError as e:
            logger.error(f"RPC error getting config: {e}")
            return False, f"RPC error: {str(e)}"
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return False, f"Error: {str(e)}"

    def edit_config(self, config_xml: str, target: str = "running") -> tuple[bool, str]:
        if not self.is_connected():
            return False, "Not connected"

        try:
            response = self._manager.edit_config(
                target=target,
                config=config_xml
            )
            if response.ok:
                return True, str(response)
            else:
                return False, f"Edit config failed: {response.error}"
        except RPCError as e:
            logger.error(f"RPC error editing config: {e}")
            return False, f"RPC error: {str(e)}"
        except Exception as e:
            logger.error(f"Error editing config: {e}")
            return False, f"Error: {str(e)}"

    def validate_config(self, config_xml: str) -> tuple[bool, str]:
        if not self.is_connected():
            return False, "Not connected"

        try:
            self._manager.validate(source="candidate")
            return True, "Validation successful"
        except RPCError as e:
            logger.error(f"RPC error validating config: {e}")
            return False, f"RPC error: {str(e)}"
        except Exception as e:
            logger.error(f"Error validating config: {e}")
            return False, f"Error: {str(e)}"

    def commit(self) -> tuple[bool, str]:
        if not self.is_connected():
            return False, "Not connected"

        try:
            response = self._manager.commit()
            if response.ok:
                return True, "Commit successful"
            else:
                return False, f"Commit failed: {response.error}"
        except RPCError as e:
            logger.error(f"RPC error committing: {e}")
            return False, f"RPC error: {str(e)}"
        except Exception as e:
            logger.error(f"Error committing: {e}")
            return False, f"Error: {str(e)}"

    def discard_changes(self) -> tuple[bool, str]:
        if not self.is_connected():
            return False, "Not connected"

        try:
            self._manager.discard_changes()
            return True, "Changes discarded"
        except RPCError as e:
            logger.error(f"RPC error discarding changes: {e}")
            return False, f"RPC error: {str(e)}"
        except Exception as e:
            logger.error(f"Error discarding changes: {e}")
            return False, f"Error: {str(e)}"

    def get_device_info(self) -> tuple[bool, Dict[str, Any]]:
        if not self.is_connected():
            return False, {}

        try:
            info = self._manager.get(operational=True).data
            return True, {"raw_data": info}
        except Exception as e:
            logger.error(f"Error getting device info: {e}")
            return False, {"error": str(e)}

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class NETCONFConnectionPool:
    _connections: Dict[str, NETCONFClient] = {}

    @classmethod
    def get_connection(
        cls,
        host: str,
        port: int = 830,
        username: str = "",
        password: str = "",
        device_type: str = "cisco_iosxe"
    ) -> NETCONFClient:
        key = f"{host}:{port}"
        if key not in cls._connections:
            cls._connections[key] = NETCONFClient(
                host=host,
                port=port,
                username=username,
                password=password,
                device_type=device_type
            )
        return cls._connections[key]

    @classmethod
    def release_connection(cls, host: str, port: int = 830):
        key = f"{host}:{port}"
        if key in cls._connections:
            cls._connections[key].disconnect()
            del cls._connections[key]

    @classmethod
    def close_all(cls):
        for conn in cls._connections.values():
            conn.disconnect()
        cls._connections.clear()

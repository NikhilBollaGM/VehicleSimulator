from kuksa_client.grpc import VSSClient, Datapoint
from typing import Optional, List
from models.signal_model import SignalObject
from Util.log_handler import Logger




class KuksaConnector:
    _instance = None

    def __new__(cls, ip: str, port: int):
        if cls._instance is None:
            cls._instance = super(KuksaConnector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, ip: str, port: int):
        if self._initialized:
            return

        self.ip = ip
        self.port = port
        self.client: Optional[VSSClient] = None
        self.connected: bool = False
        self._initialized = True

    def connect(self) -> bool:
        if self.connected:
            Logger.log(f"ℹ️ Already connected to {self.ip}:{self.port}")
            return True

        try:
            self.client = VSSClient(self.ip, self.port,)
            self.client.__enter__()
            self.connected = True
            Logger.log(f"✅ Connected to {self.ip}:{self.port}")
            return True
        except Exception as e:
            Logger.log(f"❌ Connection failed: {e}")
            self.client = None
            self.connected = False
            return False

    def disconnect(self):
        if self.client:
            self.client.__exit__(None, None, None)
            Logger.log("🔌 Disconnected.")
        self.connected = False

    def get_all_signal_objects(self) -> List[SignalObject]:
        if not self.connected or not self.client:
            Logger.log("⚠️ Not connected.")
            return []

        signal_objects = []
        try:
            all_metadata = self.client.get_metadata([""])

            for path, meta in all_metadata.items():
                allowed = None
                min_val = None
                max_val = None

                if meta.value_restriction:
                    allowed = meta.value_restriction.allowed_values
                    min_val = meta.value_restriction.min
                    max_val = meta.value_restriction.max

                signal = SignalObject(
                    name=path,
                    data_type=meta.data_type.name,
                    entry_type=meta.entry_type.name,
                    description=meta.description,
                    comment=meta.comment,
                    deprecation=meta.deprecation,
                    unit=meta.unit,
                    min_value=min_val,
                    max_value=max_val,
                    allowed_values=allowed
                )

                signal_objects.append(signal)

            return signal_objects
        except Exception as e:
            Logger.log(f"❌ Error while building signal objects: {e}")
            return []

    def set_vss_signal(self, signal_path: str, value) -> bool:
        if not self.connected or not self.client:
            Logger.log("⚠️ Not connected.")
            return False

        try:
            datapoint = Datapoint(value=value)
            self.client.set_current_values({signal_path: datapoint})
            Logger.log(f"📤 {signal_path} set to {value}")
            return True
        except Exception as e:
            Logger.log(f"⚠️ Failed to set {signal_path}: {e}")
            return False

    def get_vss_signal(self, signal_path: str) -> Optional[str]:
        if not self.connected or not self.client:
            Logger.log("⚠️ Not connected.")
            return None

        try:
            result = self.client.get_current_values([signal_path])
            value = result[signal_path].value
            Logger.log(f"📥 {signal_path} = {value}")
            return value
        except Exception as e:
            Logger.log(f"⚠️ Failed to fetch {signal_path}: {e}")
            return None


def establishKuksaConnection(ip: Optional[str], port: Optional[str]):
    Logger.log("📱 Attempting to connect...")

    # Validate input
    if not ip or not port or not port.isdigit():
        Logger.log("❌ Invalid IP or Port. Please provide valid connection parameters.")
        return None

    Logger.log(f"IP Address: {ip}")
    Logger.log(f"PORT: {port}")

    connector = KuksaConnector(ip, int(port))

    if connector.connect():
        Logger.log("✅ Connection successful")
        Logger.log(f"📦 Total Signal Objects: {len(connector.get_all_signal_objects())}")
    else:
        Logger.log("❌ Connection failed")

    return connector

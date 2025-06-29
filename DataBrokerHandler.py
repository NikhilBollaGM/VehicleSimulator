from kuksa_client.grpc import VSSClient, Datapoint
from typing import Optional, List

from models.signal_model import SignalObject

class KuksaConnector:
    _instance = None

    def __new__(cls, ip: str = "127.0.0.1", port: int = 55555):
    # def __new__(cls, ip: str = "host.docker.internal", port: int = 55555):

        if cls._instance is None:
            cls._instance = super(KuksaConnector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, ip: str = "127.0.0.1", port: int = 55555):
        if self._initialized:
            return

        self.ip = ip
        self.port = port
        self.client: Optional[VSSClient] = None
        self.connected: bool = False
        self._initialized = True

    def connect(self) -> bool:
        if self.connected:
            print(f"ℹ️ Already connected to {self.ip}:{self.port}")
            return True

        try:
            self.client = VSSClient(self.ip, self.port)
            self.client.__enter__()
            self.connected = True
            print(f"✅ Connected to {self.ip}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.client = None
            self.connected = False
            return False

    def disconnect(self):
        if self.client:
            self.client.__exit__(None, None, None)
            print("🔌 Disconnected.")
        self.connected = False

    def get_all_signal_objects(self) -> List[SignalObject]:
        if not self.connected or not self.client:
            print("⚠️ Not connected.")
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
                # print(f"✅ Created: {signal}")

            return signal_objects
        except Exception as e:
            print(f"❌ Error while building signal objects: {e}")
            return []

    def set_vss_signal(self, signal_path: str, value) -> bool:
        if not self.connected or not self.client:
            print("⚠️ Not connected.")
            return False

        try:
            datapoint = Datapoint(value=value)
            self.client.set_current_values({signal_path: datapoint})
            print(f"📤 {signal_path} set to {value}")
            return True
        except Exception as e:
            print(f"⚠️ Failed to set {signal_path}: {e}")
            return False

    def get_vss_signal(self, signal_path: str) -> Optional[str]:
        if not self.connected or not self.client:
            print("⚠️ Not connected.")
            return None

        try:
            result = self.client.get_current_values([signal_path])
            value = result[signal_path].value
            print(f"📥 {signal_path} = {value}")
            return value
        except Exception as e:
            print(f"⚠️ Failed to fetch {signal_path}: {e}")
            return None


def establishKuskaConnection(ip: str, port: int):
    print("📡 Attempting to connect...")
    print(f"IP Address: {ip}")
    print(f"PORT: {port}")

    connector = KuksaConnector(ip, port)

    if connector.connect():
        print("✅ Connection successful")
        signal_objects = connector.get_all_signal_objects()
        print(f"📦 Total Signal Objects: {len(signal_objects)}")
        print(signal_objects.pop().description)
    else:
        print("❌ Connection failed")

    return connector

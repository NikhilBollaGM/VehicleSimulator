from kuksa_client.grpc import VSSClient, Datapoint
from typing import Optional, List, Dict
import sys


class VSSSignal:
    def __init__(self, path: str, details: Dict):
        self.path = path
        self.details = details

    def __str__(self):
        return f"{self.path} - {self.details}"


class KuksaConnector:
    _instance = None

    def __new__(cls, ip: str = "127.0.0.1", port: int = 55555):
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

    def list_all_signals(self) -> List[VSSSignal]:
        if not self.connected or not self.client:
            print("⚠️ Not connected.")
            return []

        signals = []
        try:
            all_metadata = self.client.get_metadata([""])
            print("📋 All Available VSS Signals:")
            for path, details in all_metadata.items():
                signal_obj = VSSSignal(path, details)
                signals.append(signal_obj)
                print(signal_obj)
            return signals
        except Exception as e:
            print(f"❌ Failed to fetch VSS metadata: {e}")
            return []

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


if __name__ == "__main__":
    connector = KuksaConnector("127.0.0.1", 55555)
    if connector.connect():
        signals = connector.list_all_signals()

        test_signal = "Vehicle.Speed"
        if any(sig.path == test_signal for sig in signals):
            connector.set_vss_signal(test_signal, 55)
            connector.get_vss_signal(test_signal)
        else:
            print(f"⚠️ Signal '{test_signal}' not found in VSS")

        connector.disconnect()


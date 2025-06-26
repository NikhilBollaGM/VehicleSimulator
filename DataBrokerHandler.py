from kuksa_client.grpc import VSSClient
import sys

class DataBrokerConnection:
    # string ip_address;


    _instance = None

    # 
    def __new__(cls):
        if cls._instance is None:
            # print("Creating the singleton instance...")
            cls._instance = super(DataBrokerConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        
    
    
    def check_kuksa_connection(ip: str, port: int):
        try:
            with VSSClient(ip, port) as client:
                # Test access to a known VSS signal
                result = client.get_current_values(['Vehicle.Powertrain.CombustionEngine.DieselExhaustFluid.Capacity'])
                print(result)
                print("✅ Connection successful!")
                #print(f"📈 Sample data: Vehicle.Speed = {result['Vehicle.Speed'].value}")
                print(f"📈 Sample data: Vehicle.Speed = {result['Vehicle.Powertrain.CombustionEngine.DieselExhaustFluid.Capacity'].value}")
                # Create a single DataEntry for the signal and value
                # data = [DataEntry("Vehicle.Powertrain.CombustionEngine.DieselExhaustFluid.Capacity", 88.5)]  # Example: set Vehicle.Speed to 88.5

                # Publish the data
                # success = client.set(data)

                
        except Exception as e:
            print("❌ Could not connect to Kuksa Data Broker.")
            print(f"Error: {e}")
            return False

def establishKuskaConnection(ip: str,port: int):
    # ip = input("Enter Kuksa Data Broker IP address (default: 127.0.0.1): ").strip() or "127.0.0.1"
    # port_input = input("Enter port (default: 55555): ").strip()

    # port = int(port_input) if port_input else 55555

    print(port)
    print(ip)

    success = check_kuksa_connection(ip, port)

    if(success):
        print("success")
    else:
        print("failed")
    # sys.exit(0 if success else 1)

# from kuksa_client.grpc import VSSClient, Datapoint
# import sys

# def main():
#     print("📡 Connecting to Kuksa Data Broker...")
#     try:
#         with VSSClient('127.0.0.1', 55555) as client:
#             while True:
#                 # Get input from user
#                 vss_path = input("Enter VSS signal path (e.g., Vehicle.Speed): ").strip()
#                 if not vss_path:
#                     print("⚠️  Empty VSS path. Exiting.")
#                     break

#                 value_input = input("Enter value to set: ").strip()
#                 if not value_input:
#                     print("⚠️  Empty value. Exiting.")
#                     break

#                 # Try to convert value to appropriate type
#                 try:
#                     if '.' in value_input:
#                         value = float(value_input)
#                     else:
#                         value = int(value_input)
#                 except ValueError:
#                     value = value_input  # assume string

#                 # Send value
#                 try:
#                     client.set_current_values({vss_path: Datapoint(value)})
#                     print(f"✅ Set {vss_path} = {value}")
#                 except Exception as e:
#                     print(f"❌ Error setting value: {e}")

#     except Exception as conn_error:
#         print(f"❌ Could not connect to Kuksa Data Broker: {conn_error}")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()


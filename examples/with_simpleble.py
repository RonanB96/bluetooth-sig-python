#!/usr/bin/env python3
"""SimpleBLE integration example - alternative BLE library with SIG parsing.

This example demonstrates using SimpleBLE as an alternative BLE library combined
with bluetooth_sig for standards-compliant data parsing. SimpleBLE offers a 
different API design compared to Bleak.

Benefits:
- Alternative BLE library choice
- Cross-platform C++ library with Python bindings
- Pure SIG standards parsing
- Demonstrates framework-agnostic design

Requirements:
    pip install simplebluez  # Linux
    pip install simpleble    # Windows/macOS (if available)

Note: SimpleBLE availability varies by platform. This example shows the 
integration pattern even if the library is not installed.

Usage:
    python with_simpleble.py --scan
    python with_simpleble.py --address 12:34:56:78:9A:BC
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator

# Try to import SimpleBLE (availability varies by platform)
SIMPLEBLE_AVAILABLE = False
SIMPLEBLE_MODULE = None

try:
    import simpleble as simpleble_module
    SIMPLEBLE_AVAILABLE = True
    SIMPLEBLE_MODULE = simpleble_module
    print("✅ SimpleBLE module loaded")
except ImportError:
    try:
        import simplebluez as simpleble_module
        SIMPLEBLE_AVAILABLE = True
        SIMPLEBLE_MODULE = simpleble_module
        print("✅ SimpleBluez module loaded (Linux alternative)")
    except ImportError:
        print("⚠️  SimpleBLE not available. This is a demonstration of the integration pattern.")
        print("Install options:")
        print("  Linux: pip install simplebluez")
        print("  Other: pip install simpleble (if available)")


def scan_for_devices(timeout: float = 10.0) -> List[Dict]:
    """Scan for BLE devices using SimpleBLE.
    
    Returns:
        List of device information dictionaries
    """
    if not SIMPLEBLE_AVAILABLE:
        print("❌ SimpleBLE not available for scanning")
        return []
    
    devices = []
    
    try:
        print(f"🔍 Scanning for BLE devices using SimpleBLE ({timeout}s)...")
        
        # Get available adapters
        adapters = SIMPLEBLE_MODULE.Adapter.get_adapters()
        if not adapters:
            print("❌ No BLE adapters found")
            return devices
        
        adapter = adapters[0]  # Use first adapter
        print(f"📡 Using adapter: {adapter.identifier()}")
        
        # Start scanning
        adapter.scan_start()
        time.sleep(timeout)
        adapter.scan_stop()
        
        # Get scan results
        scan_results = adapter.scan_get_results()
        
        print(f"\n📡 Found {len(scan_results)} devices:")
        for i, peripheral in enumerate(scan_results, 1):
            try:
                name = peripheral.identifier() or "Unknown"
                address = peripheral.address() if hasattr(peripheral, 'address') else "Unknown"
                rssi = peripheral.rssi() if hasattr(peripheral, 'rssi') else "N/A"
                
                device_info = {
                    'name': name,
                    'address': address,
                    'rssi': rssi,
                    'peripheral': peripheral
                }
                devices.append(device_info)
                
                print(f"  {i}. {name} ({address}) - RSSI: {rssi}dBm")
                
            except Exception as e:
                print(f"  {i}. Error reading device info: {e}")
        
    except Exception as e:
        print(f"❌ Scanning failed: {e}")
    
    return devices


def read_and_parse_with_simpleble(address: str) -> Dict:
    """Read characteristics from a BLE device using SimpleBLE and parse with SIG standards.
    
    Args:
        address: BLE device address
        
    Returns:
        Dictionary of parsed characteristic data
    """
    if not SIMPLEBLE_AVAILABLE:
        print("❌ SimpleBLE not available for connections")
        return {}
    
    # Initialize SIG translator (connection-agnostic)
    translator = BluetoothSIGTranslator()
    results = {}
    
    print(f"🔵 Connecting to device using SimpleBLE: {address}")
    
    try:
        # Get adapter
        adapters = SIMPLEBLE_MODULE.Adapter.get_adapters()
        if not adapters:
            print("❌ No BLE adapters found")
            return results
        
        adapter = adapters[0]
        
        # Find the device (may need to scan first)
        print("🔍 Looking for device...")
        adapter.scan_start()
        time.sleep(5.0)  # Scan briefly
        adapter.scan_stop()
        
        scan_results = adapter.scan_get_results()
        target_peripheral = None
        
        for peripheral in scan_results:
            try:
                if hasattr(peripheral, 'address') and peripheral.address() == address:
                    target_peripheral = peripheral
                    break
                elif peripheral.identifier() == address:  # Some implementations use identifier
                    target_peripheral = peripheral
                    break
            except Exception:
                continue
        
        if not target_peripheral:
            print(f"❌ Device {address} not found in scan results")
            return results
        
        # Connect to device
        print("🔗 Connecting...")
        target_peripheral.connect()
        
        if not target_peripheral.is_connected():
            print("❌ Failed to connect")
            return results
        
        print(f"✅ Connected to {address}")
        
        # Discover services
        print("\n🔍 Discovering services...")
        services = target_peripheral.services()
        
        for service in services:
            try:
                service_uuid = service.uuid()
                print(f"\n🔧 Service: {service_uuid}")
                
                # Get characteristics for this service
                characteristics = service.characteristics()
                
                for char in characteristics:
                    try:
                        char_uuid = char.uuid()
                        
                        # Extract short UUID for SIG lookup
                        if len(char_uuid) > 8:
                            char_uuid_short = char_uuid[4:8].upper()
                        else:
                            char_uuid_short = char_uuid.upper()
                        
                        print(f"  📖 Reading characteristic {char_uuid_short}...")
                        
                        # Step 1: Read raw data (SimpleBLE handles the connection)
                        raw_data = char.read()
                        
                        if not raw_data:
                            print(f"     ⚠️  No data read")
                            continue
                        
                        # Convert to bytes if needed
                        if hasattr(raw_data, '__iter__') and not isinstance(raw_data, (str, bytes)):
                            raw_bytes = bytes(raw_data)
                        elif isinstance(raw_data, str):
                            raw_bytes = raw_data.encode('utf-8')
                        else:
                            raw_bytes = raw_data
                        
                        # Step 2: Parse with bluetooth_sig (pure SIG standards)  
                        result = translator.parse_characteristic(char_uuid_short, raw_bytes)
                        
                        # Step 3: Display results
                        if result.parse_success:
                            unit_str = f" {result.unit}" if result.unit else ""
                            print(f"     ✅ {result.name}: {result.value}{unit_str}")
                            print(f"     📄 Raw data: {raw_bytes.hex().upper()}")
                        else:
                            print(f"     ❌ Parse failed: {result.error_message}")
                            print(f"     📄 Raw data: {raw_bytes.hex().upper()}")
                        
                        results[char_uuid_short] = result
                        
                    except Exception as e:
                        print(f"     ❌ Error reading characteristic: {e}")
                
            except Exception as e:
                print(f"  ❌ Error processing service: {e}")
        
        # Disconnect
        target_peripheral.disconnect()
        print(f"\n🔌 Disconnected from {address}")
        print(f"✅ Successfully read {len(results)} characteristics")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    
    return results


def demonstrate_simpleble_patterns():
    """Demonstrate different SimpleBLE integration patterns."""
    print("\n🔧 SimpleBLE Integration Patterns")
    print("=" * 50)
    
    print("""
# Pattern 1: Simple device reading
def read_device_with_simpleble(address: str) -> dict:
    translator = BluetoothSIGTranslator()
    
    # SimpleBLE connection management
    adapters = simpleble.Adapter.get_adapters()
    adapter = adapters[0]
    
    # Scan and connect
    adapter.scan_start()
    time.sleep(5)
    adapter.scan_stop()
    
    peripherals = adapter.scan_get_results()
    target = next(p for p in peripherals if p.address() == address)
    
    target.connect()
    
    # Read and parse characteristics
    results = {}
    for service in target.services():
        for char in service.characteristics():
            raw_data = char.read()
            
            # bluetooth_sig handles SIG parsing
            uuid_short = char.uuid()[4:8]
            result = translator.parse_characteristic(uuid_short, bytes(raw_data))
            results[uuid_short] = result.value
    
    target.disconnect()
    return results

# Pattern 2: Service-specific reading
def read_battery_service(address: str) -> dict:
    translator = BluetoothSIGTranslator()
    
    # ... connection code ...
    
    # Find Battery Service (180F)
    battery_service = None
    for service in target.services():
        if "180F" in service.uuid().upper():
            battery_service = service
            break
    
    if battery_service:
        for char in battery_service.characteristics():
            if "2A19" in char.uuid().upper():  # Battery Level
                raw_data = char.read()
                result = translator.parse_characteristic("2A19", bytes(raw_data))
                return {"battery_level": result.value}
    
    return {}

# Pattern 3: Cross-platform compatibility
def get_ble_library_and_connect(address: str):
    translator = BluetoothSIGTranslator()
    
    # Try different BLE libraries based on availability
    if SIMPLEBLE_AVAILABLE:
        return read_with_simpleble(address, translator)
    elif BLEAK_AVAILABLE:
        return asyncio.run(read_with_bleak(address, translator))
    else:
        raise RuntimeError("No BLE library available")
    """)


def demonstrate_mock_usage():
    """Demonstrate the integration pattern even without SimpleBLE."""
    print("\n🎭 Mock SimpleBLE Integration (No Hardware Required)")
    print("=" * 55)
    
    # Mock data as if read from SimpleBLE
    mock_simpleble_data = {
        "2A19": [0x64],  # Battery Level: 100%
        "2A00": [0x53, 0x49, 0x47, 0x20, 0x44, 0x65, 0x76, 0x69, 0x63, 0x65],  # Device Name
        "2A6E": [0x64, 0x09],  # Temperature: 24.04°C
    }
    
    translator = BluetoothSIGTranslator()
    
    print("Simulating SimpleBLE characteristic reads:")
    print("(This shows the integration pattern)\n")
    
    for uuid_short, mock_data in mock_simpleble_data.items():
        # Simulate SimpleBLE read operation
        print(f"📖 simpleble_char.read() → {mock_data}")
        
        # Convert mock SimpleBLE data format to bytes
        raw_bytes = bytes(mock_data)
        
        # Parse with bluetooth_sig (same as real usage)
        result = translator.parse_characteristic(uuid_short, raw_bytes)
        
        if result.parse_success:
            unit_str = f" {result.unit}" if result.unit else ""
            print(f"✅ bluetooth_sig parsed: {result.name} = {result.value}{unit_str}")
        else:
            print(f"❌ Parse failed: {result.error_message}")
        print()


def main():
    """Main function demonstrating SimpleBLE + bluetooth_sig integration."""
    parser = argparse.ArgumentParser(description="SimpleBLE + bluetooth_sig integration example")
    parser.add_argument("--address", "-a", help="BLE device address to connect to")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument("--timeout", "-t", type=float, default=10.0, help="Scan timeout in seconds")
    
    args = parser.parse_args()
    
    print("🚀 SimpleBLE + Bluetooth SIG Integration Demo")
    print("=" * 50)
    
    try:
        if args.scan or not args.address:
            # Scan for devices
            devices = scan_for_devices(args.timeout)
            
            if not devices and SIMPLEBLE_AVAILABLE:
                print("\n❌ No devices found")
            elif not SIMPLEBLE_AVAILABLE:
                print("📝 Would scan for devices if SimpleBLE was available")
            
            if not args.address:
                print("\n💡 Use --address with a device address to connect")
                demonstrate_mock_usage()
                demonstrate_simpleble_patterns()
                return
        
        if args.address:
            # Connect and read characteristics
            print(f"\n🔗 Connecting to {args.address}...")
            results = read_and_parse_with_simpleble(args.address)
            
            if results:
                print(f"\n📋 Summary of parsed data:")
                for uuid, result in results.items():
                    if result.parse_success:
                        unit_str = f" {result.unit}" if result.unit else ""
                        print(f"  {result.name}: {result.value}{unit_str}")
        
        # Always show the integration patterns
        demonstrate_simpleble_patterns()
        
        # Show mock usage if SimpleBLE not available
        if not SIMPLEBLE_AVAILABLE:
            demonstrate_mock_usage()
        
        print("\n✅ Demo completed!")
        print("This example shows framework-agnostic SIG parsing with SimpleBLE.")
        print("The same bluetooth_sig parsing works with any BLE library!")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
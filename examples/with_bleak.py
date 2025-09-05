#!/usr/bin/env python3
"""Bleak integration example - demonstrates pure SIG parsing with Bleak BLE library.

This example shows how to combine Bleak for BLE connections with bluetooth_sig 
for standards-compliant data parsing. The separation of concerns allows you to 
use the best tool for each task:
- Bleak: Reliable BLE connection management  
- bluetooth_sig: Standards-compliant data interpretation

Requirements:
    pip install bleak

Usage:
    python with_bleak.py --address 12:34:56:78:9A:BC
    python with_bleak.py --scan  # Scan for devices first
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator

try:
    from bleak import BleakClient, BleakScanner
    BLEAK_AVAILABLE = True
except ImportError:
    print("❌ Bleak not available. Install with: pip install bleak")
    BLEAK_AVAILABLE = False


async def scan_for_devices(timeout: float = 10.0):
    """Scan for nearby BLE devices."""
    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available for scanning")
        return []
    
    print(f"🔍 Scanning for BLE devices ({timeout}s)...")
    devices = await BleakScanner.discover(timeout=timeout)
    
    print(f"\n📡 Found {len(devices)} devices:")
    for i, device in enumerate(devices, 1):
        name = device.name or "Unknown"
        print(f"  {i}. {name} ({device.address}) - RSSI: {device.rssi}dBm")
    
    return devices


async def read_and_parse_with_bleak(address: str, characteristic_uuids: list[str] = None):
    """Read characteristics from a BLE device and parse with SIG standards.
    
    Args:
        address: BLE device address (e.g., "12:34:56:78:9A:BC")
        characteristic_uuids: List of UUIDs to read, or None to discover all
    """
    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available for connections")
        return {}
    
    # Initialize SIG translator (connection-agnostic)
    translator = BluetoothSIGTranslator()
    results = {}
    
    print(f"🔵 Connecting to device: {address}")
    
    try:
        # Connection management: Bleak
        async with BleakClient(address, timeout=10.0) as client:
            print(f"✅ Connected to {address}")
            
            # Get device information
            if client.is_connected:
                print(f"📱 Device: {client.is_connected}")
                
                # Discover services and characteristics
                print("\n🔍 Discovering services and characteristics...")
                services = client.services
                
                if not services:
                    print("❌ No services found")
                    return results
                
                # Target specific characteristics or discover all
                target_uuids = characteristic_uuids or []
                if not target_uuids:
                    # Common characteristics to try
                    target_uuids = [
                        "2A19",  # Battery Level
                        "2A00",  # Device Name  
                        "2A01",  # Appearance
                        "2A6E",  # Temperature
                        "2A6F",  # Humidity
                        "2A6D",  # Pressure
                        "2A37",  # Heart Rate
                    ]
                
                print(f"\n📊 Reading and parsing characteristics...")
                
                for service in services:
                    service_name = service.description or "Unknown Service"
                    print(f"\n🔧 Service: {service_name} ({service.uuid})")
                    
                    for char in service.characteristics:
                        # Check if we should read this characteristic
                        char_uuid_short = char.uuid[4:8].upper() if len(char.uuid) > 8 else char.uuid.upper()
                        
                        if target_uuids and char_uuid_short not in target_uuids:
                            continue
                            
                        # Check if characteristic is readable
                        if "read" not in char.properties:
                            print(f"  ⏭️  {char.description} ({char_uuid_short}): Not readable")
                            continue
                        
                        try:
                            print(f"  📖 Reading {char.description} ({char_uuid_short})...")
                            
                            # Step 1: Read raw data (Bleak handles the connection)
                            raw_data = await client.read_gatt_char(char.uuid)
                            
                            # Step 2: Parse with bluetooth_sig (pure SIG standards)
                            result = translator.parse_characteristic(char_uuid_short, raw_data)
                            
                            # Step 3: Display results
                            if result.parse_success:
                                unit_str = f" {result.unit}" if result.unit else ""
                                print(f"     ✅ {result.name}: {result.value}{unit_str}")
                                print(f"     📄 Raw data: {raw_data.hex().upper()}")
                            else:
                                print(f"     ❌ Parse failed: {result.error_message}")
                                print(f"     📄 Raw data: {raw_data.hex().upper()}")
                            
                            results[char_uuid_short] = result
                            
                        except Exception as e:
                            print(f"     ❌ Error reading {char.description}: {e}")
                
                print(f"\n✅ Successfully read {len(results)} characteristics")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    
    return results


async def demonstrate_bleak_integration_patterns():
    """Demonstrate different integration patterns with Bleak."""
    print("\n🔧 Bleak Integration Patterns")
    print("=" * 50)
    
    # Show the basic pattern
    print("""
# Pattern 1: Simple characteristic reading
async def read_battery_level(address: str) -> int:
    translator = BluetoothSIGTranslator()
    
    async with BleakClient(address) as client:
        # Bleak handles connection
        raw_data = await client.read_gatt_char("2A19")  
        
        # bluetooth_sig handles parsing
        result = translator.parse_characteristic("2A19", raw_data)
        return result.value if result.parse_success else None

# Pattern 2: Service-based reading
async def read_environmental_sensors(address: str) -> dict:
    translator = BluetoothSIGTranslator()
    results = {}
    
    async with BleakClient(address) as client:
        # Read multiple environmental characteristics
        for uuid in ["2A6E", "2A6F", "2A6D"]:  # Temperature, Humidity, Pressure
            try:
                raw_data = await client.read_gatt_char(uuid)
                result = translator.parse_characteristic(uuid, raw_data)
                results[uuid] = result.value
            except Exception:
                pass  # Handle missing characteristics gracefully
    
    return results

# Pattern 3: Notification handling
async def handle_notifications(address: str):
    translator = BluetoothSIGTranslator()
    
    def notification_handler(sender, data):
        # Parse notifications using SIG standards
        uuid = sender.uuid[4:8]  # Extract short UUID
        result = translator.parse_characteristic(uuid, data)
        print(f"📨 {result.name}: {result.value} {result.unit}")
    
    async with BleakClient(address) as client:
        await client.start_notify("2A37", notification_handler)  # Heart rate
        await asyncio.sleep(30)  # Listen for 30 seconds
        await client.stop_notify("2A37")
    """)


async def main():
    """Main function to demonstrate Bleak + bluetooth_sig integration."""
    parser = argparse.ArgumentParser(description="Bleak + bluetooth_sig integration example")
    parser.add_argument("--address", "-a", help="BLE device address to connect to")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument("--timeout", "-t", type=float, default=10.0, help="Scan timeout in seconds")
    parser.add_argument("--uuids", "-u", nargs="+", help="Specific characteristic UUIDs to read")
    
    args = parser.parse_args()
    
    print("🚀 Bleak + Bluetooth SIG Integration Demo")
    print("=" * 50)
    
    if not BLEAK_AVAILABLE:
        print("\n❌ This example requires Bleak. Install with:")
        print("    pip install bleak")
        return
    
    try:
        if args.scan or not args.address:
            # Scan for devices
            devices = await scan_for_devices(args.timeout)
            
            if not devices:
                print("\n❌ No devices found")
                return
            
            if not args.address:
                print("\n💡 Use --address with one of the discovered addresses to connect")
                return
        
        if args.address:
            # Connect and read characteristics
            print(f"\n🔗 Connecting to {args.address}...")
            results = await read_and_parse_with_bleak(args.address, args.uuids)
            
            if results:
                print(f"\n📋 Summary of parsed data:")
                for uuid, result in results.items():
                    if result.parse_success:
                        unit_str = f" {result.unit}" if result.unit else ""
                        print(f"  {result.name}: {result.value}{unit_str}")
        
        # Show integration patterns
        await demonstrate_bleak_integration_patterns()
        
        print("\n✅ Demo completed!")
        print("This example shows how bluetooth_sig provides pure SIG parsing")
        print("while Bleak handles all BLE connection complexity.")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
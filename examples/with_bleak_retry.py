#!/usr/bin/env python3
"""Bleak-retry-connector integration example - robust BLE connections with SIG parsing.

This example demonstrates using bleak-retry-connector for reliable BLE connections
combined with bluetooth_sig for standards-compliant data parsing. This is the 
recommended pattern for production applications.

Benefits:
- Automatic retry logic for unreliable BLE connections
- Connection recovery and error handling
- Pure SIG standards parsing
- Production-ready robustness

Requirements:
    pip install bleak-retry-connector bleak

Usage:
    python with_bleak_retry.py --address 12:34:56:78:9A:BC
    python with_bleak_retry.py --scan
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator

try:
    from bleak import BleakClient, BleakScanner
    from bleak_retry_connector import establish_connection, BleakClientWithServiceCache
    BLEAK_RETRY_AVAILABLE = True
except ImportError:
    print("❌ Bleak-retry-connector not available. Install with:")
    print("    pip install bleak-retry-connector bleak")
    BLEAK_RETRY_AVAILABLE = False


async def robust_device_reading(address: str, retries: int = 3) -> dict:
    """Robust device reading with automatic retry and error recovery.
    
    Args:
        address: BLE device address
        retries: Number of connection retry attempts
        
    Returns:
        Dictionary of parsed characteristic data
    """
    if not BLEAK_RETRY_AVAILABLE:
        print("❌ Bleak-retry-connector not available")
        return {}
    
    # Initialize SIG translator (connection-agnostic)
    translator = BluetoothSIGTranslator()
    results = {}
    
    print(f"🔄 Establishing robust connection to {address} (max {retries} retries)...")
    
    try:
        # Use bleak-retry-connector for robust connection management
        async with establish_connection(
            BleakClientWithServiceCache, 
            address, 
            timeout=10.0,
            max_attempts=retries
        ) as client:
            print(f"✅ Robust connection established to {address}")
            
            # Discover all services and characteristics
            print("\n🔍 Discovering services...")
            services = client.services
            
            for service in services:
                # Get service information from SIG standards
                service_info = translator.get_service_info(service.uuid)
                service_name = service_info.name if service_info else "Unknown Service"
                
                print(f"\n🔧 Service: {service_name} ({service.uuid[:8]}...)")
                
                for char in service.characteristics:
                    # Check if characteristic is readable
                    if "read" not in char.properties:
                        continue
                    
                    # Extract short UUID for SIG lookup
                    char_uuid_short = char.uuid[4:8].upper() if len(char.uuid) > 8 else char.uuid.upper()
                    
                    try:
                        print(f"  📖 Reading {char.description} ({char_uuid_short})...")
                        
                        # Robust read with retry logic built-in
                        raw_data = await client.read_gatt_char(char.uuid)
                        
                        # Pure SIG parsing (connection-agnostic)
                        result = translator.parse_characteristic(char_uuid_short, raw_data)
                        
                        if result.parse_success:
                            unit_str = f" {result.unit}" if result.unit else ""
                            print(f"     ✅ {result.name}: {result.value}{unit_str}")
                            results[char_uuid_short] = result
                        else:
                            print(f"     ⚠️  Parse failed: {result.error_message}")
                            # Still store the result for debugging
                            results[char_uuid_short] = result
                            
                    except Exception as e:
                        print(f"     ❌ Error reading {char.description}: {e}")
                        # Continue with other characteristics
                        continue
            
            print(f"\n✅ Successfully processed {len(results)} characteristics")
            
    except Exception as e:
        print(f"❌ Robust connection failed after retries: {e}")
    
    return results


async def continuous_monitoring(address: str, interval: float = 5.0, duration: float = 60.0):
    """Demonstrate continuous monitoring with automatic reconnection.
    
    Args:
        address: BLE device address  
        interval: Reading interval in seconds
        duration: Total monitoring duration in seconds
    """
    if not BLEAK_RETRY_AVAILABLE:
        print("❌ Bleak-retry-connector not available")
        return
    
    translator = BluetoothSIGTranslator()
    
    # Characteristics to monitor (common sensor data)
    monitor_uuids = {
        "2A19": "Battery Level",
        "2A6E": "Temperature", 
        "2A6F": "Humidity",
        "2A6D": "Pressure",
    }
    
    print(f"📊 Starting continuous monitoring of {address}")
    print(f"⏱️  Interval: {interval}s, Duration: {duration}s")
    print("🔄 Using robust connection with automatic retry...")
    
    start_time = asyncio.get_event_loop().time()
    reading_count = 0
    
    try:
        # Establish connection once and reuse with caching
        async with establish_connection(
            BleakClientWithServiceCache,
            address,
            timeout=15.0,
            max_attempts=5
        ) as client:
            print(f"✅ Connected to {address} for monitoring\n")
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                reading_count += 1
                timestamp = asyncio.get_event_loop().time() - start_time
                
                print(f"📈 Reading #{reading_count} (t={timestamp:.1f}s)")
                
                # Read all monitored characteristics
                for uuid, name in monitor_uuids.items():
                    try:
                        # Robust read (with built-in retry)
                        raw_data = await client.read_gatt_char(f"0000{uuid}-0000-1000-8000-00805F9B34FB")
                        
                        # Parse with SIG standards
                        result = translator.parse_characteristic(uuid, raw_data)
                        
                        if result.parse_success:
                            unit_str = f" {result.unit}" if result.unit else ""
                            print(f"  {name}: {result.value}{unit_str}")
                        else:
                            print(f"  {name}: Parse error")
                            
                    except Exception as e:
                        print(f"  {name}: Read error - {e}")
                
                print()  # Empty line between readings
                
                # Wait for next reading
                await asyncio.sleep(interval)
                
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
    
    print(f"✅ Monitoring completed after {reading_count} readings")


async def notification_monitoring(address: str, duration: float = 30.0):
    """Demonstrate notification handling with robust connections.
    
    Args:
        address: BLE device address
        duration: Monitoring duration in seconds
    """
    if not BLEAK_RETRY_AVAILABLE:
        print("❌ Bleak-retry-connector not available")
        return
    
    translator = BluetoothSIGTranslator()
    notification_count = 0
    
    def notification_handler(sender, data: bytearray):
        nonlocal notification_count
        notification_count += 1
        
        # Extract UUID for SIG parsing
        char_uuid = sender.uuid[4:8].upper() if len(sender.uuid) > 8 else sender.uuid.upper()
        
        # Parse notification data using SIG standards
        result = translator.parse_characteristic(char_uuid, bytes(data))
        
        if result.parse_success:
            unit_str = f" {result.unit}" if result.unit else ""
            print(f"📨 #{notification_count} {result.name}: {result.value}{unit_str}")
        else:
            print(f"📨 #{notification_count} Raw data: {data.hex()}")
    
    print(f"🔔 Starting notification monitoring of {address}")
    print(f"⏱️  Duration: {duration}s")
    
    try:
        async with establish_connection(
            BleakClientWithServiceCache,
            address, 
            timeout=10.0,
            max_attempts=3
        ) as client:
            print(f"✅ Connected for notifications\n")
            
            # Common notification characteristics
            notification_uuids = [
                "2A37",  # Heart Rate Measurement
                "2A18",  # Glucose Measurement
                "2A1C",  # Temperature Measurement
            ]
            
            # Start notifications on available characteristics
            active_notifications = []
            for uuid_short in notification_uuids:
                uuid_full = f"0000{uuid_short}-0000-1000-8000-00805F9B34FB"
                try:
                    await client.start_notify(uuid_full, notification_handler)
                    active_notifications.append(uuid_full)
                    print(f"🔔 Started notifications for {uuid_short}")
                except Exception as e:
                    print(f"❌ Could not start notifications for {uuid_short}: {e}")
            
            if active_notifications:
                print(f"\n📡 Listening for notifications ({duration}s)...")
                await asyncio.sleep(duration)
                
                # Stop all notifications
                for uuid_full in active_notifications:
                    try:
                        await client.stop_notify(uuid_full)
                    except Exception:
                        pass  # Ignore errors when stopping
                
                print(f"\n✅ Received {notification_count} notifications")
            else:
                print("❌ No notification characteristics available")
                
    except Exception as e:
        print(f"❌ Notification monitoring failed: {e}")


async def demonstrate_patterns():
    """Show recommended integration patterns."""
    print("\n🔧 Bleak-Retry-Connector Integration Patterns")
    print("=" * 55)
    
    print("""
# Pattern 1: Robust single-shot reading
async def read_device_info(address: str) -> dict:
    translator = BluetoothSIGTranslator()
    
    async with establish_connection(BleakClient, address, max_attempts=3) as client:
        # Read device information characteristics
        device_info = {}
        for uuid in ["2A29", "2A24", "2A25"]:  # Manufacturer, Model, Serial
            try:
                raw_data = await client.read_gatt_char(uuid)
                result = translator.parse_characteristic(uuid, raw_data)
                device_info[result.name] = result.value
            except Exception:
                pass
        
        return device_info

# Pattern 2: Service-based processing with caching
async def process_environmental_service(address: str) -> dict:
    translator = BluetoothSIGTranslator()
    
    # Use caching client for better performance
    async with establish_connection(BleakClientWithServiceCache, address) as client:
        results = {}
        
        # Find Environmental Sensing Service
        env_service = client.services.get_service("181A")
        if env_service:
            for char in env_service.characteristics:
                if "read" in char.properties:
                    raw_data = await client.read_gatt_char(char.uuid)
                    result = translator.parse_characteristic(char.uuid, raw_data)
                    results[result.name] = result.value
        
        return results

# Pattern 3: Production monitoring with error recovery
async def production_monitoring(address: str):
    translator = BluetoothSIGTranslator()
    
    while True:  # Continuous operation
        try:
            async with establish_connection(
                BleakClientWithServiceCache, 
                address,
                timeout=10.0,
                max_attempts=5
            ) as client:
                # Monitor until disconnection
                while client.is_connected:
                    # Read critical sensor data
                    raw_data = await client.read_gatt_char("2A6E")  # Temperature
                    result = translator.parse_characteristic("2A6E", raw_data)
                    
                    # Process result...
                    await asyncio.sleep(1.0)
                    
        except Exception as e:
            print(f"Connection lost: {e}")
            await asyncio.sleep(5.0)  # Wait before retry
    """)


async def main():
    """Main function demonstrating bleak-retry-connector + bluetooth_sig."""
    parser = argparse.ArgumentParser(description="Bleak-retry-connector + bluetooth_sig example")
    parser.add_argument("--address", "-a", help="BLE device address")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices")
    parser.add_argument("--monitor", "-m", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--notifications", "-n", action="store_true", help="Notification monitoring mode")
    parser.add_argument("--duration", "-d", type=float, default=60.0, help="Monitoring duration (seconds)")
    parser.add_argument("--interval", "-i", type=float, default=5.0, help="Reading interval (seconds)")
    
    args = parser.parse_args()
    
    print("🚀 Bleak-Retry-Connector + Bluetooth SIG Integration Demo")
    print("=" * 65)
    
    if not BLEAK_RETRY_AVAILABLE:
        print("\n❌ This example requires bleak-retry-connector. Install with:")
        print("    pip install bleak-retry-connector bleak")
        return
    
    try:
        if args.scan or not args.address:
            # Scan for devices using basic Bleak
            print("🔍 Scanning for BLE devices...")
            devices = await BleakScanner.discover(timeout=10.0)
            
            print(f"\n📡 Found {len(devices)} devices:")
            for i, device in enumerate(devices, 1):
                name = device.name or "Unknown"
                print(f"  {i}. {name} ({device.address}) - RSSI: {device.rssi}dBm")
            
            if not args.address:
                print("\n💡 Use --address with one of the discovered addresses")
                return
        
        if args.address:
            if args.monitor:
                await continuous_monitoring(args.address, args.interval, args.duration)
            elif args.notifications:
                await notification_monitoring(args.address, args.duration)
            else:
                await robust_device_reading(args.address)
        
        await demonstrate_patterns()
        
        print("\n✅ Demo completed!")
        print("This example shows robust BLE connections with pure SIG parsing.")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
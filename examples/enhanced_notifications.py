#!/usr/bin/env python3
"""Enhanced Notifications - SIG library integration with notification parsing.

Based on Bleak's enable_notifications.py with comprehensive Bluetooth SIG library
integration for parsing notification data. This example demonstrates:

1. Automatic SIG parsing in notification callbacks
2. Rich data extraction that manual parsing would miss
3. Standards-compliant notification handling
4. Real-time parsing with proper error handling

Requirements:
    pip install bleak

Usage:
    python enhanced_notifications.py --address 12:34:56:78:9A:BC
    python enhanced_notifications.py --address 12:34:56:78:9A:BC --characteristic 2A37  # Heart Rate
    python enhanced_notifications.py --scan  # Scan first
    python enhanced_notifications.py --mock  # Simulate notifications with mock data
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator

# Import shared utilities  
from ble_utils import (
    BLEAK_AVAILABLE,
    scan_with_bleak,
)

# Try to import Bleak
if BLEAK_AVAILABLE:
    from bleak import BleakClient, BleakGATTCharacteristic

# Set up logging for notification output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SIGNotificationHandler:
    """Enhanced notification handler with Bluetooth SIG parsing."""
    
    def __init__(self, translator: BluetoothSIGTranslator):
        self.translator = translator
        self.notification_count = 0
        self.start_time = time.time()
        
    def create_handler(self, characteristic_name: str = None):
        """Create a notification handler function with SIG parsing."""
        
        def sig_notification_handler(sender: BleakGATTCharacteristic, data: bytearray) -> None:
            """Enhanced notification handler with automatic SIG parsing."""
            self.notification_count += 1
            elapsed = time.time() - self.start_time
            
            # Get characteristic name from SIG registry first
            char_info = self.translator.get_characteristic_info(sender.uuid)
            
            if char_info:
                # Parse using SIG standards
                result = self.translator.parse_characteristic(sender.uuid, data)
                
                if result.parse_success:
                    # Show rich parsed data
                    unit_str = f" {result.unit}" if result.unit else ""
                    logger.info("📊 Notification #%d (%.1fs): %s = %s%s",
                              self.notification_count, elapsed, result.name, result.value, unit_str)
                    
                    # Show additional rich data that manual parsing would miss
                    self._display_rich_data(result, data)
                    
                else:
                    logger.warning("❌ Notification #%d (%.1fs): %s - Parse failed: %s",
                                 self.notification_count, elapsed, result.name, result.error_message)
                    logger.info("   🔢 Raw data: %s", data.hex())
            else:
                # Unknown characteristic
                char_name = characteristic_name or f"Unknown-{sender.uuid}"
                logger.warning("❓ Notification #%d (%.1fs): %s - Not a known SIG characteristic",
                             self.notification_count, elapsed, char_name)
                logger.info("   📝 UUID: %s", sender.uuid)
                logger.info("   🔢 Raw data: %s", data.hex())
                
        return sig_notification_handler
    
    def _display_rich_data(self, result, raw_data: bytearray) -> None:
        """Display rich parsed data that demonstrates SIG library advantages."""
        
        # Show raw data for comparison
        logger.info("   🔢 Raw data: %s", raw_data.hex())
        
        # Show characteristic-specific rich data
        if hasattr(result.value, '__dict__'):
            # Structured data object
            logger.info("   📋 Structured data:")
            for key, value in result.value.__dict__.items():
                if not key.startswith('_'):
                    logger.info("      %s: %s", key, value)
        
        # Show SIG standard compliance features
        if result.name == "Heart Rate Measurement":
            self._display_heart_rate_details(result)
        elif result.name == "Temperature Measurement":
            self._display_temperature_details(result)
        elif result.name == "Battery Level":
            self._display_battery_details(result)
        elif "Pressure" in result.name:
            self._display_pressure_details(result)
    
    def _display_heart_rate_details(self, result) -> None:
        """Display heart rate measurement specific details."""
        if hasattr(result.value, 'heart_rate'):
            logger.info("   💓 Heart Rate: %d bpm", result.value.heart_rate)
            
        if hasattr(result.value, 'sensor_contact_detected'):
            contact_status = "✅ Good" if result.value.sensor_contact_detected else "❌ Poor"
            logger.info("   👆 Sensor Contact: %s", contact_status)
            
        if hasattr(result.value, 'energy_expended'):
            logger.info("   🔥 Energy Expended: %s kJ", result.value.energy_expended)
            
        if hasattr(result.value, 'rr_intervals'):
            logger.info("   📈 RR Intervals: %s", result.value.rr_intervals)
    
    def _display_temperature_details(self, result) -> None:
        """Display temperature measurement specific details."""
        if hasattr(result.value, 'temperature'):
            logger.info("   🌡️  Temperature: %.2f %s", result.value.temperature, result.unit)
            
        if hasattr(result.value, 'timestamp'):
            logger.info("   ⏰ Timestamp: %s", result.value.timestamp)
            
        if hasattr(result.value, 'temperature_type'):
            logger.info("   📍 Location: %s", result.value.temperature_type)
            
        if hasattr(result.value, 'status'):
            logger.info("   📊 Status: %s", result.value.status)
    
    def _display_battery_details(self, result) -> None:
        """Display battery level specific details."""
        if hasattr(result.value, 'level'):
            logger.info("   🔋 Battery Level: %d%%", result.value.level)
            
        if hasattr(result.value, 'status'):
            logger.info("   📊 Battery Status: %s", result.value.status)
    
    def _display_pressure_details(self, result) -> None:
        """Display pressure measurement specific details."""
        logger.info("   📊 Pressure: %s %s", result.value, result.unit)
        
        # Convert to different units for context
        if result.unit == "Pa":
            hpa = result.value / 100
            logger.info("   🌡️  Pressure (hPa): %.2f", hpa)


async def monitor_notifications_with_sig_parsing(
    address: str, 
    target_characteristic: str = None,
    duration: int = 30,
    timeout: float = 10.0
) -> None:
    """Monitor BLE notifications with enhanced SIG parsing."""
    
    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available. Install with: pip install bleak")
        return
    
    translator = BluetoothSIGTranslator()
    handler = SIGNotificationHandler(translator)
    
    print(f"🔗 Connecting to device: {address}")
    
    try:
        async with BleakClient(address, timeout=timeout) as client:
            print("✅ Connected successfully!")
            print(f"📱 Device: {client.address}")
            
            # Find notifiable characteristics
            notifiable_chars = await find_notifiable_characteristics(client, translator, target_characteristic)
            
            if not notifiable_chars:
                print("❌ No notifiable characteristics found")
                return
            
            # Subscribe to notifications
            subscribed_count = await subscribe_to_notifications(client, handler, notifiable_chars)
            
            if subscribed_count == 0:
                print("❌ Failed to subscribe to any notifications")
                return
            
            print(f"📡 Subscribed to {subscribed_count} characteristics")
            print(f"🔔 Monitoring notifications for {duration} seconds...")
            print("   (Press Ctrl+C to stop early)\n")
            
            # Monitor notifications
            try:
                await asyncio.sleep(duration)
            except KeyboardInterrupt:
                print("\n⚠️  Monitoring stopped by user")
            
            print(f"\n📊 Monitoring complete!")
            print(f"   Total notifications received: {handler.notification_count}")
            print(f"   Duration: {time.time() - handler.start_time:.1f} seconds")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")


async def find_notifiable_characteristics(
    client, 
    translator: BluetoothSIGTranslator,
    target_characteristic: str = None
) -> list:
    """Find characteristics that support notifications."""
    
    notifiable_chars = []
    
    print(f"\n🔍 Discovering notifiable characteristics...")
    
    for service in client.services:
        # Identify service
        service_info = translator.get_service_info(service.uuid)
        service_name = service_info.name if service_info else f"Unknown Service"
        
        print(f"\n🔧 Service: {service_name} ({service.uuid})")
        
        for char in service.characteristics:
            if "notify" in char.properties or "indicate" in char.properties:
                # Check if this is our target characteristic (if specified)
                if target_characteristic:
                    # Support both UUID and name targeting
                    char_info = translator.get_characteristic_info(char.uuid)
                    
                    uuid_match = str(char.uuid).upper() == target_characteristic.upper()
                    name_match = (char_info and 
                                char_info.name.lower() == target_characteristic.lower())
                    
                    if not (uuid_match or name_match):
                        continue
                
                # Get characteristic info
                char_info = translator.get_characteristic_info(char.uuid)
                char_name = char_info.name if char_info else f"Unknown-{char.uuid}"
                
                notifiable_chars.append({
                    'characteristic': char,
                    'info': char_info,
                    'name': char_name
                })
                
                properties = ", ".join(char.properties)
                sig_status = "✅ Known SIG" if char_info else "❓ Unknown/Custom"
                
                print(f"   📡 {char_name}")
                print(f"      📝 UUID: {char.uuid}")
                print(f"      🔑 Properties: {properties}")
                print(f"      📊 Status: {sig_status}")
    
    return notifiable_chars


async def subscribe_to_notifications(client, handler: SIGNotificationHandler, notifiable_chars: list) -> int:
    """Subscribe to notifications for discovered characteristics."""
    
    subscribed_count = 0
    
    print(f"\n📡 Subscribing to {len(notifiable_chars)} notifiable characteristics:")
    
    for char_data in notifiable_chars:
        char = char_data['characteristic']
        char_name = char_data['name']
        
        try:
            # Create handler for this specific characteristic
            notification_handler = handler.create_handler(char_name)
            
            # Subscribe to notifications
            await client.start_notify(char.uuid, notification_handler)
            
            print(f"   ✅ Subscribed to {char_name}")
            subscribed_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed to subscribe to {char_name}: {e}")
    
    return subscribed_count


async def run_mock_notifications_demo(duration: int = 10) -> None:
    """Demonstrate notification parsing with mock data."""
    
    print("🧪 MOCK NOTIFICATIONS DEMONSTRATION")
    print("=" * 50)
    print("Simulating BLE notifications with SIG parsing (no hardware needed)")
    
    translator = BluetoothSIGTranslator()
    handler = SIGNotificationHandler(translator)
    
    # Mock notification data for different characteristics
    mock_notifications = [
        {
            "name": "Heart Rate Measurement",
            "uuid": "2A37",
            "data_sequence": [
                bytes([0x00, 0x48]),  # 72 bpm, no sensor contact
                bytes([0x01, 0x4A]),  # 74 bpm, with sensor contact
                bytes([0x01, 0x4C]),  # 76 bpm, with sensor contact
                bytes([0x01, 0x4E]),  # 78 bpm, with sensor contact
            ]
        },
        {
            "name": "Battery Level", 
            "uuid": "2A19",
            "data_sequence": [
                bytes([100]),  # 100%
                bytes([95]),   # 95%
                bytes([90]),   # 90%
                bytes([85]),   # 85%
            ]
        },
        {
            "name": "Temperature",
            "uuid": "2A6E", 
            "data_sequence": [
                bytes([0x64, 0x09]),  # 24.04°C
                bytes([0x65, 0x09]),  # 24.05°C
                bytes([0x66, 0x09]),  # 24.06°C
                bytes([0x67, 0x09]),  # 24.07°C
            ]
        }
    ]
    
    print(f"\n🔔 Simulating {duration} seconds of notifications...")
    
    start_time = time.time()
    notification_interval = duration / 12  # Send 12 total notifications
    
    # Create mock characteristic objects
    class MockCharacteristic:
        def __init__(self, uuid: str, name: str):
            self.uuid = uuid
            self.description = name
    
    # Simulate notifications
    for i in range(4):  # 4 rounds of notifications
        for mock_char in mock_notifications:
            char = MockCharacteristic(mock_char["uuid"], mock_char["name"])
            data = bytearray(mock_char["data_sequence"][i])
            
            # Create and call handler
            notification_handler = handler.create_handler(mock_char["name"])
            notification_handler(char, data)
            
            # Wait between notifications
            await asyncio.sleep(notification_interval)
            
            # Check if we've exceeded our duration
            if time.time() - start_time >= duration:
                break
        
        if time.time() - start_time >= duration:
            break
    
    print(f"\n📊 Mock demonstration complete!")
    print(f"   Total mock notifications: {handler.notification_count}")
    print(f"   Duration: {time.time() - handler.start_time:.1f} seconds")


async def main():
    """Main entry point for enhanced notifications example."""
    
    parser = argparse.ArgumentParser(
        description="Enhanced BLE Notifications with Bluetooth SIG parsing"
    )
    parser.add_argument(
        "--address",
        help="BLE device address to connect to"
    )
    parser.add_argument(
        "--characteristic",
        help="Specific characteristic UUID or name to monitor (optional)"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan for nearby BLE devices"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run mock notifications demo (no hardware required)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Duration to monitor notifications in seconds (default: 30)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Connection timeout in seconds (default: 10.0)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Enhanced BLE Notifications with Bluetooth SIG Integration")
    print("Showcasing automatic parsing of notification data with SIG standards")
    print()
    
    if args.mock:
        await run_mock_notifications_demo(args.duration)
        return
    
    if args.scan:
        print("🔍 Scanning for BLE devices...")
        devices = await scan_with_bleak(timeout=10.0)
        if devices:
            print(f"\n📱 Found {len(devices)} devices. Use --address with one of these:")
            for device in devices[:5]:
                print(f"   {device.address} - {device.name or 'Unknown'}")
        else:
            print("❌ No devices found")
        return
    
    if not args.address:
        print("❌ Error: Must specify --address, --scan, or --mock")
        print("Examples:")
        print("  python enhanced_notifications.py --scan")
        print("  python enhanced_notifications.py --address 12:34:56:78:9A:BC")
        print("  python enhanced_notifications.py --address 12:34:56:78:9A:BC --characteristic '2A37'")
        print("  python enhanced_notifications.py --address 12:34:56:78:9A:BC --characteristic 'Heart Rate Measurement'")
        print("  python enhanced_notifications.py --mock")
        return
    
    await monitor_notifications_with_sig_parsing(
        args.address, 
        args.characteristic,
        args.duration,
        args.timeout
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
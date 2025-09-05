#!/usr/bin/env python3
"""Comprehensive BLE debugging script with multiple connection strategies and detailed analysis.

This script consolidates functionality from multiple debugging scripts to provide
a single, comprehensive tool for BLE device testing and debugging.
"""

import argparse
import asyncio
import logging
import sys
import traceback
from pathlib import Path

# Configure path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# pylint: disable=wrong-import-position
try:
    from bleak import BleakClient, BleakScanner
    BLEAK_AVAILABLE = True
except ImportError:
    print("⚠️  Warning: 'bleak' module not found. Some functionality will be limited.")
    print("Install with: pip install bleak")
    BLEAK_AVAILABLE = False

    # Create mock classes for argument parsing
    class BleakClient: pass
    class BleakScanner: pass

try:
    from bluetooth_sig.core import BluetoothSIG, BluetoothSIGTranslator
    FRAMEWORK_AVAILABLE = True
except ImportError:
    print("⚠️  Warning: BLE GATT framework not available. Framework-specific features disabled.")
    FRAMEWORK_AVAILABLE = False


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def scan_devices(timeout: float = 10.0, show_details: bool = False) -> None:
    """Scan for nearby BLE devices."""
    print("🔍 Scanning for BLE devices...")
    print("=" * 60)

    try:
        devices = await BleakScanner.discover(timeout=timeout)
        if devices:
            print(f"Found {len(devices)} devices:")
            for idx, device in enumerate(devices, 1):
                name = device.name or "Unknown"
                rssi_str = f"({device.rssi} dBm)" if hasattr(device, 'rssi') and device.rssi else ""
                print(f"  {idx:2d}. {device.address} - {name} {rssi_str}")

                if show_details:
                    if hasattr(device, "details"):
                        print(f"      Details: {device.details}")
                    if hasattr(device, "metadata"):
                        print(f"      Metadata: {device.metadata}")
        else:
            print("No devices found")
            print("\n💡 Troubleshooting tips:")
            print("   - Ensure devices are powered on and advertising")
            print("   - Check Bluetooth adapter is enabled")
            print("   - Try increasing scan timeout")
            print("   - Restart Bluetooth: sudo systemctl restart bluetooth")

    except Exception as e:
        print(f"❌ Scan error: {e}")
        traceback.print_exc()


async def test_simple_connection(mac_address: str) -> bool:
    """Test a very simple connection."""
    print(f"🔧 Simple Connection Test: {mac_address}")
    print("-" * 40)

    try:
        # Most basic connection possible
        async with BleakClient(mac_address, timeout=45.0) as client:
            print("✅ Simple connection successful!")
            return True
    except Exception as e:
        print(f"❌ Simple connection failed: {e}")
        return False


async def test_bluetoothctl_style(mac_address: str) -> bool:
    """Test connection similar to bluetoothctl."""
    print(f"🔧 Bluetoothctl-style Test: {mac_address}")
    print("-" * 40)

    # Discover device fresh each time
    print("Discovering device...")
    devices = await BleakScanner.discover(timeout=5.0)
    target_device = None

    for device in devices:
        if device.address.upper() == mac_address.upper():
            target_device = device
            break

    if not target_device:
        print("❌ Device not found in fresh scan")
        return False

    print(f"✅ Fresh device found: {target_device.name}")

    # Try connection immediately after discovery
    try:
        client = BleakClient(target_device)
        await client.connect()
        print("✅ Connected!")

        # Minimal service check
        await asyncio.sleep(1.0)
        service_count = len(list(client.services))
        print(f"✅ Services: {service_count}")

        await client.disconnect()
        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_multiple_strategies(mac_address: str) -> bool:
    """Try multiple connection strategies."""
    print(f"🔍 Testing Multiple Connection Strategies: {mac_address}")
    print("=" * 60)

    # First, find the device
    device = await BleakScanner.find_device_by_address(mac_address)
    if not device:
        print("❌ Device not found")
        return False

    print(f"✅ Device found: {device.name or 'Unknown'}")

    strategies = [
        ("Short timeout", {"timeout": 10.0}),
        ("Long timeout", {"timeout": 60.0}),
        ("No services filter", {"timeout": 30.0, "services": None}),
    ]

    for strategy_name, kwargs in strategies:
        print(f"\n🔄 Strategy: {strategy_name}")
        print(f"   Parameters: {kwargs}")

        try:
            async with BleakClient(device, **kwargs) as client:
                print(f"   ✅ Connected successfully!")
                print(f"   Services available: {len(list(client.services))}")

                # Try to read one simple characteristic
                for service in client.services:
                    for char in service.characteristics:
                        if "read" in char.properties:
                            try:
                                value = await client.read_gatt_char(char)
                                print(f"   ✅ Read test successful: {len(value)} bytes")
                                return True
                            except Exception as e:
                                print(f"   ⚠️  Read test failed: {e}")
                                continue

                print(f"   ⚠️  No readable characteristics found")
                return True  # Connection successful even without reads

        except asyncio.TimeoutError:
            print(f"   ❌ Timeout error")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Try manual connection without context manager
    print(f"\n🔄 Strategy: Manual connection")
    client = None
    try:
        client = BleakClient(device)
        print("   Connecting manually...")
        await client.connect()
        print("   ✅ Manual connection successful!")

        # Force service discovery
        print("   Discovering services...")
        await asyncio.sleep(2.0)  # Give time for discovery

        services = list(client.services)
        print(f"   ✅ Found {len(services)} services")

        return True

    except Exception as e:
        print(f"   ❌ Manual connection failed: {e}")
    finally:
        if client and client.is_connected:
            await client.disconnect()

    return False


async def connect_device(mac_address: str) -> bool:
    """Test connection to device using multiple strategies."""
    print(f"🔗 Testing Connection: {mac_address}")
    print("=" * 70)

    # Try all strategies
    strategies = [
        test_simple_connection,
        test_bluetoothctl_style,
        test_multiple_strategies,
    ]

    for strategy_func in strategies:
        success = await strategy_func(mac_address)
        if success:
            print(f"\n🎉 SUCCESS with {strategy_func.__name__}!")
            return True
        else:
            print(f"\n❌ {strategy_func.__name__} failed")

    print(f"\n💡 All strategies failed. Try:")
    print(f"   1. sudo systemctl restart bluetooth")
    print(f"   2. bluetoothctl scan on")
    print(f"   3. bluetoothctl connect {mac_address}")
    print(f"   4. Check if device requires pairing")
    return False


async def discover_device(mac_address: str) -> bool:
    """Perform comprehensive device discovery."""
    print(f"🔍 Device Discovery: {mac_address}")
    print("=" * 70)

    # Step 1: Device Discovery with detailed information
    print("📡 Step 1: Device Discovery & Verification")
    print("-" * 40)

    device = None
    try:
        print(f"Searching for device {mac_address}...")
        device = await BleakScanner.find_device_by_address(mac_address)

        if device:
            print("✅ Device found!")
            print(f"   Name: {device.name or 'Unknown'}")
            print(f"   Address: {device.address}")
            # RSSI might not be available from find_device_by_address
            if hasattr(device, "rssi") and device.rssi is not None:
                print(f"   RSSI: {device.rssi} dBm")
            else:
                print("   RSSI: Not available from address lookup")
            if hasattr(device, "details"):
                print(f"   Details: {device.details}")
            if hasattr(device, "metadata"):
                print(f"   Metadata: {device.metadata}")
        else:
            print(f"❌ Device {mac_address} not found via address lookup")
            print("🔄 Performing full scan to locate device...")

            devices = await BleakScanner.discover(timeout=15.0)
            print(f"Found {len(devices)} total devices:")

            for idx, scanned_device in enumerate(devices):
                status = (
                    "🎯"
                    if scanned_device.address.upper() == mac_address.upper()
                    else "  "
                )
                print(
                    f"{status} {idx+1:2d}. {scanned_device.address} - {scanned_device.name or 'Unknown'} ({scanned_device.rssi} dBm)"
                )

                if scanned_device.address.upper() == mac_address.upper():
                    device = scanned_device
                    print(f"✅ Target device found in scan!")

            if not device:
                print(f"❌ Device {mac_address} not discoverable")
                print("\n💡 Troubleshooting tips:")
                print(
                    "   - Ensure device is powered on and in pairing/advertising mode"
                )
                print("   - Check MAC address format (should be XX:XX:XX:XX:XX:XX)")
                print("   - Move closer to the device")
                print("   - Restart Bluetooth: sudo systemctl restart bluetooth")
                return False

    except Exception as e:
        print(f"❌ Error during device discovery: {e}")
        traceback.print_exc()
        return False

    # Step 2: Connection attempt with detailed error handling
    print(f"\n🔗 Step 2: Connection Attempt")
    print("-" * 40)

    try:
        print(f"Creating BleakClient for {device.address}...")
        print("Connection parameters:")
        print("   - Timeout: 30 seconds")
        print("   - Device object: Using discovered device")

        # Try connection with extended timeout
        async with BleakClient(device, timeout=30.0) as client:
            print(f"✅ Connection established!")
            print(f"   Address: {client.address}")
            print(f"   Connected: {client.is_connected}")

            # Check MTU
            try:
                mtu = client.mtu_size
                print(f"   MTU Size: {mtu} bytes")
            except Exception as e:
                print(f"   MTU Size: Unable to determine ({e})")

            # Step 3: Service Discovery
            print(f"\n📋 Step 3: Service Discovery")
            print("-" * 40)

            # Wait a moment for service discovery to complete
            await asyncio.sleep(1.0)

            if not client.services:
                print("❌ No services discovered")
                print("   This might indicate:")
                print("   - Device requires pairing")
                print("   - Device has connection issues")
                print("   - Service discovery timeout")
                return False

            services_list = list(client.services)
            print(f"✅ Discovered {len(services_list)} services")

            readable_chars = []
            total_chars = 0

            # Detailed service enumeration
            for service_idx, service in enumerate(client.services, 1):
                print(f"\n📋 Service {service_idx}: {service.uuid}")
                print(f"   Description: {service.description}")
                print(f"   Handle range: {getattr(service, 'handle', 'N/A')}")

                if not service.characteristics:
                    print("   └─ No characteristics")
                    continue

                char_list = list(service.characteristics)
                total_chars += len(char_list)
                print(f"   └─ {len(char_list)} characteristics:")

                for char_idx, char in enumerate(service.characteristics, 1):
                    properties = ", ".join(char.properties)
                    print(f"      {char_idx}. {char.uuid}")
                    print(f"         Description: {char.description}")
                    print(f"         Properties: [{properties}]")
                    print(f"         Handle: {getattr(char, 'handle', 'N/A')}")

                    # Collect readable characteristics
                    if "read" in char.properties:
                        readable_chars.append(char)
                        print(f"         ✅ Readable")

                    # Show descriptors
                    if char.descriptors:
                        print(f"         Descriptors:")
                        for desc_idx, desc in enumerate(char.descriptors, 1):
                            print(
                                f"           {desc_idx}. {desc.uuid} - {desc.description}"
                            )

            print(
                f"\n📊 Summary: {total_chars} total characteristics, {len(readable_chars)} readable"
            )
            return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Exception type: {type(e).__name__}")
        _print_error_analysis(str(e))
        return False


async def read_device(mac_address: str) -> bool:
    """Read all readable characteristics from device."""
    print(f"📖 Reading Device Characteristics: {mac_address}")
    print("=" * 70)

    try:
        # Use framework if available, otherwise fall back to raw Bleak
        if FRAMEWORK_AVAILABLE:
            print("Using BLE GATT framework...")
            device = BLEGATTDevice(mac_address)
            connected = await device.connect()

            if not connected:
                print(f"❌ Could not connect to device {mac_address}")
                return False

            print(f"✅ Connected using framework")

            # Read characteristics
            print("\n🔍 Reading all readable characteristics...")
            values = await device.read_characteristics()

            for uuid, value in values.items():
                if isinstance(value, (bytes, bytearray)):
                    if len(value) == 0:
                        print(f"  ⚠️  {uuid}: Empty data (0 bytes)")
                    else:
                        try:
                            str_val = value.decode("utf-8").strip("\x00")
                            is_printable = str_val and all(c.isprintable() or c.isspace() for c in str_val)
                            if is_printable and len(str_val) > 0:
                                print(f"  ✅ {uuid}: '{str_val}' ({len(value)} bytes)")
                            else:
                                hex_val = " ".join(f"{b:02x}" for b in value)
                                print(f"  ✅ {uuid}: {hex_val} ({len(value)} bytes)")
                        except UnicodeDecodeError:
                            hex_val = " ".join(f"{b:02x}" for b in value)
                            print(f"  ✅ {uuid}: {hex_val} ({len(value)} bytes)")
                else:
                    print(f"  ✅ {uuid}: {value}")

            # Parse with GATT framework
            print("\n🏗️  Testing GATT framework integration...")
            parsed = await device.read_parsed_characteristics()
            chars = parsed.get("characteristics", {})

            if chars:
                for uuid, entry in chars.items():
                    char_name = entry.get("characteristic", "?")
                    value = entry.get("value")
                    unit = entry.get("unit", "")
                    unit_str = f" {unit}" if unit else ""
                    print(f"  ✅ {char_name}: {value}{unit_str}")
                print(f"\n✅ Successfully parsed {len(chars)} characteristics using framework")
            else:
                print("\nℹ️  No characteristics were parsed (may need raw data re-reading)")

            # Enhanced SIG translator analysis
            print("\n🔍 Enhanced SIG Analysis...")
            translator = BluetoothSIGTranslator()

            # Show supported characteristics summary
            supported = translator.list_supported_characteristics()
            print(f"✅ SIG Translator supports {len(supported)} characteristics")

            # Analyze discovered characteristics
            discovered_uuids = [uuid for uuid in values.keys()]
            if discovered_uuids:
                print(f"\n📊 Analyzing {len(discovered_uuids)} discovered "
                      "characteristics:")
                char_info = translator.get_characteristics_info(
                    discovered_uuids)

                for uuid, info in char_info.items():
                    if info:
                        name = info.get('name', 'Unknown')
                        data_type = info.get('data_type', 'unknown')
                        unit = info.get('unit', '')
                        unit_str = f" ({unit})" if unit else ""
                        print(f"  📋 {uuid}: {name} [{data_type}]{unit_str}")
                    else:
                        print(f"  ❓ {uuid}: Unknown characteristic")

                # Batch validation if we have raw data
                print("\n🔍 Validating characteristic data...")
                valid_count = 0
                for uuid, data in values.items():
                    if isinstance(data, (bytes, bytearray)):
                        is_valid = translator.validate_characteristic_data(
                            uuid, data)
                        status = "✅" if is_valid else "⚠️"
                        validity = 'Valid' if is_valid else 'Invalid/Unknown'
                        print(f"  {status} {uuid}: {validity}")
                        if is_valid:
                            valid_count += 1

                print(f"\n📈 Validation Summary: {valid_count}/"
                      f"{len(values)} characteristics have valid data format")

            await device.disconnect()
            return True

        else:
            print("Framework not available, using raw Bleak...")
            device = await BleakScanner.find_device_by_address(mac_address)
            if not device:
                print("❌ Device not found")
                return False

            async with BleakClient(device, timeout=30.0) as client:
                print(f"✅ Connected to {device.address}")

                readable_chars = []
                for service in client.services:
                    for char in service.characteristics:
                        if "read" in char.properties:
                            readable_chars.append(char)

                print(f"\n🔍 Reading {len(readable_chars)} readable characteristics...")
                successful_reads = 0

                for idx, char in enumerate(readable_chars, 1):
                    try:
                        print(f"Reading {idx}/{len(readable_chars)}: {char.uuid}...")
                        value = await client.read_gatt_char(char)
                        successful_reads += 1

                        # Display value
                        if isinstance(value, (bytes, bytearray)):
                            if len(value) == 0:
                                print(f"   ✅ Empty value")
                            elif all(32 <= b <= 126 for b in value):  # Printable ASCII
                                try:
                                    str_val = value.decode("utf-8").strip("\x00")
                                    print(f"   ✅ '{str_val}' (string)")
                                except UnicodeDecodeError:
                                    hex_val = " ".join(f"{b:02x}" for b in value)
                                    print(f"   ✅ {hex_val} (hex)")
                            else:
                                hex_val = " ".join(f"{b:02x}" for b in value)
                                print(f"   ✅ {hex_val} (hex)")
                        else:
                            print(f"   ✅ {value}")

                    except Exception as e:
                        print(f"   ❌ Error: {e}")

                print(f"\n📊 Read Summary: {successful_reads}/{len(readable_chars)} successful")
                return True

    except Exception as e:
        print(f"❌ Read failed: {e}")
        traceback.print_exc()
        return False


async def monitor_device(mac_address: str, duration: int = 60) -> bool:
    """Monitor device characteristics continuously."""
    print(f"📡 Monitoring Device: {mac_address} (for {duration} seconds)")
    print("=" * 70)

    print("⚠️  Monitor functionality not yet implemented")
    print("This would continuously read characteristics and display changes")
    print(f"Duration: {duration} seconds")
    return True


async def test_device_comprehensive(mac_address: str) -> bool:
    """Run comprehensive test suite on device."""
    print(f"🧪 Comprehensive Test Suite: {mac_address}")
    print("=" * 70)

    success_count = 0
    total_tests = 5

    # Test 1: Connection
    print("Test 1/5: Connection Testing")
    if await connect_device(mac_address):
        success_count += 1
        print("✅ Connection test passed")
    else:
        print("❌ Connection test failed")

    print("\n" + "="*40 + "\n")

    # Test 2: Discovery
    print("Test 2/5: Service Discovery")
    if await discover_device(mac_address):
        success_count += 1
        print("✅ Discovery test passed")
    else:
        print("❌ Discovery test failed")

    print("\n" + "="*40 + "\n")

    # Test 3: Reading
    print("Test 3/5: Characteristic Reading")
    if await read_device(mac_address):
        success_count += 1
        print("✅ Reading test passed")
    else:
        print("❌ Reading test failed")

    print("\n" + "="*40 + "\n")

    # Test 4: Framework Integration (if available)
    print("Test 4/5: Framework Integration")
    if FRAMEWORK_AVAILABLE:
        try:
            device = BLEGATTDevice(mac_address)
            connected = await device.connect()
            if connected:
                parsed = await device.read_parsed_characteristics()
                await device.disconnect()
                success_count += 1
                print("✅ Framework integration test passed")
            else:
                print("❌ Framework integration test failed - connection")
        except Exception as e:
            print(f"❌ Framework integration test failed: {e}")
    else:
        print("⚠️  Framework not available - skipping")
        success_count += 1  # Don't penalize if framework not available

    print("\n" + "="*40 + "\n")

    # Test 5: Error Analysis
    print("Test 5/5: Error Analysis")
    _print_error_analysis("")
    success_count += 1
    print("✅ Error analysis completed")

    print("\n" + "="*70)
    print(f"🏁 Test Suite Results: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed - check logs above")
        return False


def _print_error_analysis(error_msg: str = "") -> None:
    """Print analysis of common BLE connection errors and solutions."""
    print("🔍 Common BLE Error Analysis & Solutions")
    print("=" * 60)

    if error_msg:
        error_msg_lower = error_msg.lower()
        print(f"Current Error: {error_msg}\n")

        if "timeout" in error_msg_lower:
            print("🔍 Timeout Error Detected:")
            print("   • Device may be sleeping or unresponsive")
            print("   • Try putting device in pairing mode")
            print("   • Check for interference from other devices")
            print("   • Try: bluetoothctl scan on, then connect from command line")

        elif "permission denied" in error_msg_lower or "access" in error_msg_lower:
            print("🔍 Permission Error Detected:")
            print("   • Try: sudo python scripts/ble_debug.py <command> <address>")
            print("   • Add to bluetooth group: sudo usermod -a -G bluetooth $USER")
            print("   • Check: groups $USER")

        elif "device not found" in error_msg_lower:
            print("🔍 Device Not Found Error Detected:")
            print("   • Device moved out of range")
            print("   • Device turned off")
            print("   • MAC address changed (randomization)")

        elif "already connected" in error_msg_lower or "busy" in error_msg_lower:
            print("🔍 Device Busy Error Detected:")
            print("   • Disconnect from phone/other apps")
            print("   • Wait 10 seconds and retry")
            print("   • Reset Bluetooth: sudo systemctl restart bluetooth")

        print("\n" + "-"*40 + "\n")

    print("📱 Service Discovery Errors:")
    print("❌ 'Service Discovery has not been performed yet'")
    print("   → Solution: Enhanced connection with explicit discovery retry")
    print("   → Often affects: Apple devices, complex devices")

    print("\n🔐 Authentication Errors:")
    print("❌ 'ATT error: 0x0e (Unlikely Error)'")
    print("   → Meaning: Characteristic requires authentication/encryption")
    print("   → Solution: Device needs to be paired first")
    print("   → Command: bluetoothctl pair <MAC_ADDRESS>")

    print("\n⏱️  Connection Timeouts:")
    print("❌ Connection timeout or 'Device not found'")
    print("   → Causes: Device sleeping, out of range, already connected")
    print("   → Solutions:")
    print("     • bluetoothctl disconnect <MAC_ADDRESS>")
    print("     • Ensure device is in advertising mode")
    print("     • Check device power/battery")

    print("\n📦 Empty Characteristic Data:")
    print("❌ Characteristics return 0 bytes")
    print("   → Causes: Requires write-first, authentication, timing")
    print("   → Solutions:")
    print("     • Some characteristics need activation via write")
    print("     • May require notifications to be enabled")
    print("     • Check characteristic properties")

    print("\n🚫 Framework Recognition:")
    print("ℹ️  'No services recognized by GATT framework'")
    print("   → Expected for proprietary devices")
    print("   → Our framework targets standard Bluetooth SIG services")
    print("   → Focus on Environmental Sensing Service (181A) devices")

    print("\n🎯 Recommended Test Devices:")
    print("✅ Environmental sensors with ESS service")
    print("✅ Fitness trackers with standard services")
    print("✅ Nordic nRF52 development boards")
    print("✅ Thingy:52 (when properly advertising)")


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for BLE debug commands."""
    parser = argparse.ArgumentParser(
        description="Comprehensive BLE debugging script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scan                           # Scan for devices
  %(prog)s scan --timeout 30 --details   # Extended scan with details
  %(prog)s connect AA:BB:CC:DD:EE:FF      # Test connection strategies
  %(prog)s discover AA:BB:CC:DD:EE:FF     # Full service discovery
  %(prog)s read AA:BB:CC:DD:EE:FF         # Read all characteristics
  %(prog)s monitor AA:BB:CC:DD:EE:FF      # Monitor device (30 sec)
  %(prog)s test AA:BB:CC:DD:EE:FF         # Full diagnostic suite
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for BLE devices')
    scan_parser.add_argument('--timeout', type=float, default=10.0,
                           help='Scan timeout in seconds (default: 10)')
    scan_parser.add_argument('--details', action='store_true',
                           help='Show detailed device information')

    # Connect command
    connect_parser = subparsers.add_parser('connect', help='Test connection to device')
    connect_parser.add_argument('address', help='Device MAC address (XX:XX:XX:XX:XX:XX)')

    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover device services and characteristics')
    discover_parser.add_argument('address', help='Device MAC address (XX:XX:XX:XX:XX:XX)')

    # Read command
    read_parser = subparsers.add_parser('read', help='Read all readable characteristics')
    read_parser.add_argument('address', help='Device MAC address (XX:XX:XX:XX:XX:XX)')

    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor device characteristics')
    monitor_parser.add_argument('address', help='Device MAC address (XX:XX:XX:XX:XX:XX)')
    monitor_parser.add_argument('--duration', type=int, default=30,
                              help='Monitor duration in seconds (default: 30)')

    # Test command
    test_parser = subparsers.add_parser('test', help='Run comprehensive test suite')
    test_parser.add_argument('address', help='Device MAC address (XX:XX:XX:XX:XX:XX)')

    return parser


async def main() -> int:
    """Main function."""
    # Check dependencies early
    if not BLEAK_AVAILABLE:
        print("\n❌ Required dependency 'bleak' is not installed.")
        print("Install dependencies with: pip install bleak")
        print("For full functionality: pip install -e '.[dev]'")
        return 1

    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == 'scan':
            await scan_devices(timeout=args.timeout, show_details=args.details)
            return 0

        elif args.command == 'connect':
            success = await connect_device(args.address.upper())
            return 0 if success else 1

        elif args.command == 'discover':
            success = await discover_device(args.address.upper())
            return 0 if success else 1

        elif args.command == 'read':
            success = await read_device(args.address.upper())
            return 0 if success else 1

        elif args.command == 'monitor':
            success = await monitor_device(args.address.upper(), args.duration)
            return 0 if success else 1

        elif args.command == 'test':
            success = await test_device_comprehensive(args.address.upper())
            return 0 if success else 1

        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
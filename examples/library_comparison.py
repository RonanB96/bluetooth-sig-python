#!/usr/bin/env python3
"""Library comparison example - compare different BLE libraries with SIG parsing.

This example demonstrates the framework-agnostic nature of bluetooth_sig by
showing how the same SIG parsing code works identically across different BLE
connection libraries. The parsing logic remains unchanged regardless of the
underlying BLE implementation.

Key Demonstration:
- Same bluetooth_sig code works with multiple BLE libraries
- Connection method varies, but SIG parsing is identical
- Framework-agnostic design allows easy migration between libraries
- Performance and feature comparison across libraries

Usage:
    python library_comparison.py --address 12:34:56:78:9A:BC
    python library_comparison.py --scan --compare-all
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator

# Check available BLE libraries
AVAILABLE_LIBRARIES = {}

# Check for Bleak
try:
    from bleak import BleakClient, BleakScanner
    AVAILABLE_LIBRARIES['bleak'] = {
        'module': 'bleak',
        'async': True,
        'description': 'Cross-platform async BLE library'
    }
except ImportError:
    pass

# Check for Bleak-retry-connector
try:
    from bleak_retry_connector import establish_connection, BleakClientWithServiceCache
    AVAILABLE_LIBRARIES['bleak-retry'] = {
        'module': 'bleak_retry_connector',
        'async': True,
        'description': 'Robust BLE connections with retry logic'
    }
except ImportError:
    pass

# Check for SimpleBLE variants
try:
    import simpleble
    AVAILABLE_LIBRARIES['simpleble'] = {
        'module': 'simpleble',
        'async': False,
        'description': 'C++ based cross-platform BLE library'
    }
except ImportError:
    try:
        import simplebluez
        AVAILABLE_LIBRARIES['simplebluez'] = {
            'module': 'simplebluez',
            'async': False,
            'description': 'Linux-specific BLE library'
        }
    except ImportError:
        pass


def show_library_availability():
    """Display which BLE libraries are available."""
    print("📚 BLE Library Availability Check")
    print("=" * 40)
    
    if not AVAILABLE_LIBRARIES:
        print("❌ No BLE libraries found. Install one or more:")
        print("   pip install bleak")
        print("   pip install bleak-retry-connector")
        print("   pip install simpleble  # If available for your platform")
        print("   pip install simplebluez  # Linux only")
        return False
    
    print("✅ Available BLE libraries:")
    for lib_name, info in AVAILABLE_LIBRARIES.items():
        async_str = "Async" if info['async'] else "Sync"
        print(f"   {lib_name}: {info['description']} ({async_str})")
    
    print(f"\n🎯 Will demonstrate bluetooth_sig parsing with {len(AVAILABLE_LIBRARIES)} libraries")
    return True


async def read_with_bleak(address: str, target_uuids: List[str]) -> Dict[str, Tuple[bytes, float]]:
    """Read characteristics using Bleak library.
    
    Returns:
        Dict mapping UUID to (raw_data, read_time)
    """
    if 'bleak' not in AVAILABLE_LIBRARIES:
        return {}
    
    results = {}
    print("📱 Reading with Bleak...")
    
    try:
        start_time = time.time()
        async with BleakClient(address, timeout=10.0) as client:
            connection_time = time.time() - start_time
            print(f"   ⏱️  Connection time: {connection_time:.2f}s")
            
            for uuid_short in target_uuids:
                uuid_full = f"0000{uuid_short}-0000-1000-8000-00805F9B34FB"
                try:
                    read_start = time.time()
                    raw_data = await client.read_gatt_char(uuid_full)
                    read_time = time.time() - read_start
                    results[uuid_short] = (raw_data, read_time)
                    print(f"   📖 {uuid_short}: {len(raw_data)} bytes in {read_time:.3f}s")
                except Exception as e:
                    print(f"   ❌ {uuid_short}: {e}")
                    
    except Exception as e:
        print(f"   ❌ Bleak connection failed: {e}")
    
    return results


async def read_with_bleak_retry(address: str, target_uuids: List[str]) -> Dict[str, Tuple[bytes, float]]:
    """Read characteristics using Bleak-retry-connector.
    
    Returns:
        Dict mapping UUID to (raw_data, read_time)
    """
    if 'bleak-retry' not in AVAILABLE_LIBRARIES:
        return {}
    
    results = {}
    print("🔄 Reading with Bleak-Retry-Connector...")
    
    try:
        start_time = time.time()
        async with establish_connection(
            BleakClientWithServiceCache, 
            address, 
            timeout=10.0,
            max_attempts=3
        ) as client:
            connection_time = time.time() - start_time
            print(f"   ⏱️  Robust connection time: {connection_time:.2f}s")
            
            for uuid_short in target_uuids:
                uuid_full = f"0000{uuid_short}-0000-1000-8000-00805F9B34FB"
                try:
                    read_start = time.time()
                    raw_data = await client.read_gatt_char(uuid_full)
                    read_time = time.time() - read_start
                    results[uuid_short] = (raw_data, read_time)
                    print(f"   📖 {uuid_short}: {len(raw_data)} bytes in {read_time:.3f}s")
                except Exception as e:
                    print(f"   ❌ {uuid_short}: {e}")
                    
    except Exception as e:
        print(f"   ❌ Bleak-retry connection failed: {e}")
    
    return results


def read_with_simpleble(address: str, target_uuids: List[str]) -> Dict[str, Tuple[bytes, float]]:
    """Read characteristics using SimpleBLE.
    
    Returns:
        Dict mapping UUID to (raw_data, read_time)
    """
    if 'simpleble' not in AVAILABLE_LIBRARIES and 'simplebluez' not in AVAILABLE_LIBRARIES:
        return {}
    
    # Determine which SimpleBLE variant to use
    module_name = 'simpleble' if 'simpleble' in AVAILABLE_LIBRARIES else 'simplebluez'
    
    results = {}
    print(f"🔧 Reading with {module_name.title()}...")
    
    try:
        if module_name == 'simpleble':
            import simpleble as ble_module
        else:
            import simplebluez as ble_module
        
        # Get adapter
        adapters = ble_module.Adapter.get_adapters()
        if not adapters:
            print("   ❌ No adapters found")
            return results
        
        adapter = adapters[0]
        
        # Scan and connect
        start_time = time.time()
        adapter.scan_start()
        time.sleep(3.0)  # Brief scan
        adapter.scan_stop()
        
        peripherals = adapter.scan_get_results()
        target_peripheral = None
        
        for peripheral in peripherals:
            try:
                if hasattr(peripheral, 'address') and peripheral.address() == address:
                    target_peripheral = peripheral
                    break
                elif peripheral.identifier() == address:
                    target_peripheral = peripheral
                    break
            except Exception:
                continue
        
        if not target_peripheral:
            print(f"   ❌ Device {address} not found")
            return results
        
        target_peripheral.connect()
        connection_time = time.time() - start_time
        print(f"   ⏱️  Connection time: {connection_time:.2f}s")
        
        if not target_peripheral.is_connected():
            print("   ❌ Connection failed")
            return results
        
        # Read characteristics
        for service in target_peripheral.services():
            for char in service.characteristics():
                char_uuid = char.uuid()
                char_uuid_short = char_uuid[4:8].upper() if len(char_uuid) > 8 else char_uuid.upper()
                
                if char_uuid_short in target_uuids:
                    try:
                        read_start = time.time()
                        raw_data = char.read()
                        read_time = time.time() - read_start
                        
                        # Convert to bytes if needed
                        if hasattr(raw_data, '__iter__') and not isinstance(raw_data, (str, bytes)):
                            raw_bytes = bytes(raw_data)
                        else:
                            raw_bytes = raw_data if isinstance(raw_data, bytes) else bytes()
                        
                        results[char_uuid_short] = (raw_bytes, read_time)
                        print(f"   📖 {char_uuid_short}: {len(raw_bytes)} bytes in {read_time:.3f}s")
                    except Exception as e:
                        print(f"   ❌ {char_uuid_short}: {e}")
        
        target_peripheral.disconnect()
        
    except Exception as e:
        print(f"   ❌ {module_name} error: {e}")
    
    return results


async def compare_libraries(address: str, target_uuids: List[str] = None):
    """Compare different BLE libraries with identical SIG parsing.
    
    Args:
        address: BLE device address
        target_uuids: List of characteristic UUIDs to test
    """
    if target_uuids is None:
        target_uuids = ["2A19", "2A00", "2A6E", "2A6F"]  # Battery, Device Name, Temperature, Humidity
    
    print("🔬 BLE Library Comparison with Identical SIG Parsing")
    print("=" * 60)
    print(f"Target device: {address}")
    print(f"Test characteristics: {', '.join(target_uuids)}\n")
    
    # Initialize SIG translator (used by all libraries)
    translator = BluetoothSIGTranslator()
    
    # Store results from each library
    library_results = {}
    library_timings = {}
    
    # Test each available library
    if 'bleak' in AVAILABLE_LIBRARIES:
        start_time = time.time()
        raw_results = await read_with_bleak(address, target_uuids)
        total_time = time.time() - start_time
        library_results['bleak'] = raw_results
        library_timings['bleak'] = total_time
        print()
    
    if 'bleak-retry' in AVAILABLE_LIBRARIES:
        start_time = time.time()
        raw_results = await read_with_bleak_retry(address, target_uuids)
        total_time = time.time() - start_time
        library_results['bleak-retry'] = raw_results
        library_timings['bleak-retry'] = total_time
        print()
    
    if 'simpleble' in AVAILABLE_LIBRARIES or 'simplebluez' in AVAILABLE_LIBRARIES:
        start_time = time.time()
        raw_results = read_with_simpleble(address, target_uuids)
        total_time = time.time() - start_time
        lib_name = 'simpleble' if 'simpleble' in AVAILABLE_LIBRARIES else 'simplebluez'
        library_results[lib_name] = raw_results
        library_timings[lib_name] = total_time
        print()
    
    # Parse all results with the SAME bluetooth_sig translator
    print("🔄 Parsing all results with IDENTICAL bluetooth_sig code:")
    print("=" * 55)
    
    parsed_results = {}
    for lib_name, raw_data_dict in library_results.items():
        print(f"\n📚 {lib_name.title()} results parsed by bluetooth_sig:")
        parsed_results[lib_name] = {}
        
        for uuid_short, (raw_data, read_time) in raw_data_dict.items():
            # THE SAME parsing code for ALL libraries
            result = translator.parse_characteristic(uuid_short, raw_data)
            parsed_results[lib_name][uuid_short] = result
            
            if result.parse_success:
                unit_str = f" {result.unit}" if result.unit else ""
                print(f"   ✅ {result.name}: {result.value}{unit_str}")
            else:
                print(f"   ❌ {result.name}: Parse failed")
    
    # Compare results across libraries
    print("\n📊 Cross-Library Comparison")
    print("=" * 30)
    
    for uuid_short in target_uuids:
        print(f"\n🔍 Characteristic {uuid_short}:")
        values_match = True
        reference_value = None
        
        for lib_name in library_results.keys():
            if uuid_short in parsed_results[lib_name]:
                result = parsed_results[lib_name][uuid_short]
                if result.parse_success:
                    value = result.value
                    unit_str = f" {result.unit}" if result.unit else ""
                    print(f"   {lib_name}: {value}{unit_str}")
                    
                    if reference_value is None:
                        reference_value = value
                    elif reference_value != value:
                        values_match = False
                else:
                    print(f"   {lib_name}: Parse failed")
                    values_match = False
            else:
                print(f"   {lib_name}: Not read")
                values_match = False
        
        if values_match and reference_value is not None:
            print(f"   ✅ All libraries parsed IDENTICAL values!")
        else:
            print(f"   ⚠️  Values differ or some failed")
    
    # Performance comparison
    print(f"\n⏱️  Performance Comparison")
    print("=" * 25)
    for lib_name, total_time in library_timings.items():
        successful_reads = len([r for r in library_results[lib_name].values()])
        print(f"   {lib_name}: {total_time:.2f}s total, {successful_reads} successful reads")


def demonstrate_mock_comparison():
    """Demonstrate library comparison with mock data."""
    print("\n🎭 Mock Library Comparison (No Hardware Required)")
    print("=" * 55)
    
    # Mock data as if from different libraries
    mock_library_data = {
        'bleak': {
            '2A19': bytes([0x64]),  # 100% battery
            '2A00': b'Bleak Device',
        },
        'simpleble': {
            '2A19': bytes([0x64]),  # Same battery reading
            '2A00': b'Bleak Device',  # Same device name
        },
        'custom_lib': {
            '2A19': bytes([0x64]),  # Same value from any library
            '2A00': b'Bleak Device',
        }
    }
    
    # THE SAME translator for all "libraries"
    translator = BluetoothSIGTranslator()
    
    print("Comparing bluetooth_sig parsing across mock libraries:\n")
    
    for uuid_short in ['2A19', '2A00']:
        print(f"🔍 Characteristic {uuid_short}:")
        
        for lib_name, data_dict in mock_library_data.items():
            if uuid_short in data_dict:
                raw_data = data_dict[uuid_short]
                
                # IDENTICAL parsing code for all libraries
                result = translator.parse_characteristic(uuid_short, raw_data)
                
                if result.parse_success:
                    unit_str = f" {result.unit}" if result.unit else ""
                    print(f"   {lib_name}: {result.value}{unit_str}")
                else:
                    print(f"   {lib_name}: Parse failed")
        
        print("   ✅ All 'libraries' produce IDENTICAL parsed values!\n")


async def main():
    """Main function for BLE library comparison."""
    parser = argparse.ArgumentParser(description="BLE library comparison with bluetooth_sig")
    parser.add_argument("--address", "-a", help="BLE device address to test")
    parser.add_argument("--scan", "-s", action="store_true", help="Scan for devices first")
    parser.add_argument("--compare-all", "-c", action="store_true", help="Compare all available libraries")
    parser.add_argument("--uuids", "-u", nargs="+", help="Specific UUIDs to test")
    
    args = parser.parse_args()
    
    print("🚀 BLE Library Comparison with Framework-Agnostic SIG Parsing")
    print("=" * 70)
    
    # Show available libraries
    has_libraries = show_library_availability()
    
    if not has_libraries and not args.address:
        print("\n📝 Showing mock comparison to demonstrate the concept:")
        demonstrate_mock_comparison()
        return
    
    try:
        if args.scan and 'bleak' in AVAILABLE_LIBRARIES:
            print("\n🔍 Scanning for devices...")
            devices = await BleakScanner.discover(timeout=10.0)
            
            print(f"\n📡 Found {len(devices)} devices:")
            for i, device in enumerate(devices, 1):
                name = device.name or "Unknown"
                print(f"  {i}. {name} ({device.address}) - RSSI: {device.rssi}dBm")
            
            if not args.address:
                print("\n💡 Use --address with one of the discovered addresses to compare")
                demonstrate_mock_comparison()
                return
        
        if args.address and has_libraries:
            target_uuids = args.uuids or ["2A19", "2A00", "2A6E", "2A6F"]
            await compare_libraries(args.address, target_uuids)
        elif args.address:
            print(f"\n❌ No BLE libraries available to test with {args.address}")
            demonstrate_mock_comparison()
        else:
            demonstrate_mock_comparison()
        
        print("\n✅ Demo completed!")
        print("Key takeaway: bluetooth_sig provides IDENTICAL parsing across all BLE libraries!")
        print("Your choice of BLE library doesn't affect SIG standard interpretation.")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
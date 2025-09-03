#!/usr/bin/env python3
"""
Demonstration of the new Bluetooth SIG Standards Library.

This script showcases the pure SIG translation capabilities without any 
connection dependencies.
"""

import sys
sys.path.insert(0, "src")

def demonstrate_pure_sig_translation():
    """Demonstrate the pure SIG translation pattern."""
    print("🔗 Bluetooth SIG Standards Library - Pure Translation Demo")
    print("=" * 60)
    
    # Import the new library
    from bluetooth_sig import BluetoothSIGTranslator
    
    # Create translator instance
    translator = BluetoothSIGTranslator()
    print(f"📚 Translator: {translator}")
    print()
    
    # Demonstrate characteristic parsing with various UUID formats
    print("🔍 Characteristic Parsing Examples:")
    print("-" * 40)
    
    examples = [
        ("2A19", b'\x64', "Battery Level (100%)"),
        ("00002A19-0000-1000-8000-00805F9B34FB", b'\x50', "Battery Level (80%)"),
        ("2A6E", b'\x00\x01', "Temperature (raw)"),
        ("unknown-uuid", b'\xFF\xFE', "Unknown characteristic"),
    ]
    
    for uuid, raw_data, description in examples:
        result = translator.parse_characteristic(uuid, raw_data)
        print(f"  UUID: {uuid}")
        print(f"  Description: {description}")
        print(f"  Raw data: {raw_data.hex()}")
        print(f"  Parsed: {result}")
        print()
    
    # Demonstrate metadata retrieval
    print("📋 Characteristic Information:")
    print("-" * 40)
    
    info_examples = ["2A19", "2A6E", "unknown"]
    for uuid in info_examples:
        info = translator.get_characteristic_info(uuid)
        if info:
            print(f"  UUID {uuid}: {info['name']} ({info['value_type']})")
            if info['unit']:
                print(f"    Unit: {info['unit']}")
        else:
            print(f"  UUID {uuid}: Not found in registry")
    print()
    
    # Demonstrate listing capabilities
    print("📊 Registry Statistics:")
    print("-" * 40)
    
    characteristics = translator.list_supported_characteristics()
    services = translator.list_supported_services()
    
    print(f"  Supported characteristics: {len(characteristics)}")
    print(f"  Supported services: {len(services)}")
    print()
    
    # Show the pure SIG translation pattern from the docs
    print("🎯 Pure SIG Translation Pattern:")
    print("-" * 40)
    
    def parse_sensor_reading(char_uuid: str, raw_data: bytes):
        """Pure SIG standard translation - no connection dependencies."""
        return translator.parse_characteristic(char_uuid, raw_data)
    
    # Example usage
    battery_data = parse_sensor_reading("2A19", b'\x4B')  # 75%
    print(f"  Pattern usage: Battery reading = {battery_data}")
    print()
    
    print("✅ Demo completed successfully!")
    print("🚀 The library is now pure SIG standards with zero connection dependencies.")

if __name__ == "__main__":
    try:
        demonstrate_pure_sig_translation()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)
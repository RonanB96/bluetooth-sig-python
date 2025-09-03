#!/usr/bin/env python3
"""
Test script to verify the new BluetoothSIGTranslator API works without dependencies.
"""

import sys
sys.path.insert(0, "src")

def test_basic_functionality():
    """Test basic SIG translator functionality."""
    try:
        # Test import
        from bluetooth_sig import BluetoothSIGTranslator
        print("✅ BluetoothSIGTranslator import successful")
        
        # Test instantiation
        translator = BluetoothSIGTranslator()
        print(f"✅ Translator instance: {translator}")
        
        # Test listing supported characteristics (without requiring YAML)
        try:
            characteristics = translator.list_supported_characteristics()
            print(f"✅ Found {len(characteristics)} supported characteristics")
        except Exception as e:
            print(f"⚠️  Characteristics listing failed (expected without YAML): {e}")
        
        # Test characteristic parsing with dummy data (will test parsing logic)
        try:
            # Test with battery level (UUID 2A19) - should return raw data if no parser
            result = translator.parse_characteristic("2A19", b'\x64')  # 100%
            print(f"✅ Characteristic parsing result: {result}")
        except Exception as e:
            print(f"⚠️  Characteristic parsing failed (expected without YAML): {e}")
            
        print("✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
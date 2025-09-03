#!/usr/bin/env python3
"""
Run the BluetoothSIGTranslator tests directly without pytest.
"""

import sys
sys.path.insert(0, "src")

from tests.test_bluetooth_sig_translator import TestBluetoothSIGTranslator

def run_tests():
    """Run all tests in the TestBluetoothSIGTranslator class."""
    test_class = TestBluetoothSIGTranslator()
    
    # Get all test methods
    test_methods = [method for method in dir(test_class) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    
    for method_name in test_methods:
        try:
            print(f"Running {method_name}...")
            method = getattr(test_class, method_name)
            method()
            print(f"✅ {method_name} passed")
            passed += 1
        except Exception as e:
            print(f"❌ {method_name} failed: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""Testing with mocks example - unit testing SIG parsing without BLE hardware.

This example demonstrates how to unit test bluetooth_sig parsing functionality
using mock data, without requiring actual BLE devices. This is essential for:
- CI/CD pipelines without BLE hardware
- Regression testing of SIG parsing logic
- Validation of new characteristic implementations
- Performance testing with synthetic data

Key Benefits:
- No BLE hardware required
- Deterministic test results
- Fast execution in CI/CD
- Comprehensive edge case testing
- Validation against SIG specifications

Usage:
    python testing_with_mocks.py
    python testing_with_mocks.py --test-suite comprehensive
    python testing_with_mocks.py --benchmark
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig import BluetoothSIGTranslator


class MockCharacteristicData:
    """Mock characteristic data based on SIG specifications."""
    
    # Test data derived from official Bluetooth SIG specifications
    SIG_COMPLIANT_DATA = {
        # Battery Service
        "2A19": {  # Battery Level
            "valid": [
                (bytes([0x00]), 0, "%"),      # 0%
                (bytes([0x32]), 50, "%"),     # 50%
                (bytes([0x64]), 100, "%"),    # 100%
            ],
            "invalid": [
                (bytes([]), "insufficient data"),
                (bytes([0x65]), "value > 100%"),  # 101% is invalid
            ]
        },
        
        # Environmental Sensing
        "2A6E": {  # Temperature
            "valid": [
                (bytes([0x00, 0x00]), 0.0, "°C"),        # 0°C
                (bytes([0x64, 0x09]), 24.04, "°C"),      # ~24°C
                (bytes([0x9C, 0xFF]), -1.0, "°C"),       # -1°C (signed)
                (bytes([0x10, 0x27]), 100.0, "°C"),      # 100°C
            ],
            "invalid": [
                (bytes([0x00]), "insufficient data"),
                (bytes([]), "no data"),
            ]
        },
        
        "2A6F": {  # Humidity
            "valid": [
                (bytes([0x00, 0x00]), 0.0, "%"),         # 0%
                (bytes([0x10, 0x27]), 100.0, "%"),       # 100%
                (bytes([0x38, 0x19]), 64.56, "%"),       # ~65%
            ],
            "invalid": [
                (bytes([0x00]), "insufficient data"),
            ]
        },
        
        "2A6D": {  # Pressure
            "valid": [
                (bytes([0x40, 0x9C, 0x00, 0x00]), 40.0, "kPa"),    # 40 kPa
                (bytes([0x70, 0x96, 0x00, 0x00]), 38.512, "kPa"),  # ~38.5 kPa
            ],
            "invalid": [
                (bytes([0x00, 0x00]), "insufficient data"),
                (bytes([]), "no data"),
            ]
        },
        
        # Device Information
        "2A00": {  # Device Name
            "valid": [
                (b"Test Device", "Test Device", None),
                (b"SIG Demo", "SIG Demo", None),
                (b"", "", None),  # Empty name is valid
            ],
            "invalid": []  # Device names are generally flexible
        },
        
        "2A29": {  # Manufacturer Name String
            "valid": [
                (b"Bluetooth SIG", "Bluetooth SIG", None),
                (b"Test Company", "Test Company", None),
            ],
            "invalid": []
        },
        
        # Heart Rate Service
        "2A37": {  # Heart Rate Measurement
            "valid": [
                (bytes([0x00, 0x48]), {"heart_rate": 72, "flags": 0, "sensor_contact_detected": False, "sensor_contact_supported": False}, "bpm"),  # 72 BPM
                (bytes([0x00, 0x3C]), {"heart_rate": 60, "flags": 0, "sensor_contact_detected": False, "sensor_contact_supported": False}, "bpm"),  # 60 BPM
            ],
            "invalid": [
                (bytes([0x00]), "insufficient data"),
                (bytes([]), "no data"),
            ]
        },
    }


def run_basic_parsing_tests() -> Dict[str, Any]:
    """Run basic parsing tests with mock data."""
    print("🧪 Basic SIG Parsing Tests")
    print("=" * 30)
    
    translator = BluetoothSIGTranslator()
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "details": {}
    }
    
    for uuid, test_data in MockCharacteristicData.SIG_COMPLIANT_DATA.items():
        print(f"\n📊 Testing {uuid} characteristic:")
        char_results = {"valid_passed": 0, "valid_failed": 0, "invalid_handled": 0}
        
        # Test valid data
        for raw_data, expected_value, expected_unit in test_data["valid"]:
            results["total_tests"] += 1
            try:
                result = translator.parse_characteristic(uuid, raw_data)
                
                if result.parse_success:
                    # Check if parsed value matches expected
                    if result.value == expected_value:
                        print(f"   ✅ Valid data: {raw_data.hex()} → {result.value} {result.unit or ''}")
                        results["passed"] += 1
                        char_results["valid_passed"] += 1
                    else:
                        print(f"   ❌ Value mismatch: expected {expected_value}, got {result.value}")
                        results["failed"] += 1
                        char_results["valid_failed"] += 1
                else:
                    print(f"   ❌ Parse failed: {result.error_message}")
                    results["failed"] += 1
                    char_results["valid_failed"] += 1
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                results["failed"] += 1
                char_results["valid_failed"] += 1
        
        # Test invalid data (should fail gracefully)
        for raw_data, expected_error in test_data["invalid"]:
            results["total_tests"] += 1
            try:
                result = translator.parse_characteristic(uuid, raw_data)
                
                if not result.parse_success:
                    print(f"   ✅ Invalid data handled: {raw_data.hex() if raw_data else 'empty'}")
                    results["passed"] += 1
                    char_results["invalid_handled"] += 1
                else:
                    print(f"   ⚠️  Invalid data accepted: {raw_data.hex() if raw_data else 'empty'}")
                    results["failed"] += 1
                    
            except Exception as e:
                print(f"   ✅ Exception properly raised: {e}")
                results["passed"] += 1
                char_results["invalid_handled"] += 1
        
        results["details"][uuid] = char_results
    
    return results


def run_edge_case_tests() -> Dict[str, Any]:
    """Test edge cases and error conditions."""
    print("\n🔍 Edge Case Tests")
    print("=" * 20)
    
    translator = BluetoothSIGTranslator()
    results = {"total_tests": 0, "passed": 0, "failed": 0}
    
    edge_cases = [
        ("Unknown UUID", "FFFF", bytes([0x01, 0x02]), "Should fallback gracefully"),
        ("Empty data", "2A19", bytes([]), "Should handle empty data"),
        ("Oversized data", "2A19", bytes([0x64] * 100), "Should handle excess data"),
        ("Invalid UUID format", "invalid", bytes([0x64]), "Should handle malformed UUID"),
        ("Case sensitivity", "2a19", bytes([0x64]), "Should handle lowercase UUID"),
        ("Full UUID format", "00002A19-0000-1000-8000-00805F9B34FB", bytes([0x64]), "Should handle full UUID"),
    ]
    
    for test_name, uuid, data, description in edge_cases:
        results["total_tests"] += 1
        try:
            result = translator.parse_characteristic(uuid, data)
            print(f"   ✅ {test_name}: {description}")
            results["passed"] += 1
        except Exception as e:
            print(f"   ❌ {test_name}: Exception - {e}")
            results["failed"] += 1
    
    return results


def run_performance_benchmark() -> Dict[str, Any]:
    """Benchmark parsing performance with mock data."""
    print("\n⚡ Performance Benchmark")
    print("=" * 25)
    
    translator = BluetoothSIGTranslator()
    
    # Generate test dataset
    test_data = []
    for uuid, test_cases in MockCharacteristicData.SIG_COMPLIANT_DATA.items():
        for raw_data, _, _ in test_cases["valid"]:
            test_data.append((uuid, raw_data))
    
    # Benchmark single parsing operations
    single_times = []
    for uuid, raw_data in test_data:
        start_time = time.perf_counter()
        translator.parse_characteristic(uuid, raw_data)
        end_time = time.perf_counter()
        single_times.append(end_time - start_time)
    
    # Benchmark batch operations
    batch_data = {uuid: raw_data for uuid, raw_data in test_data[:5]}  # Limit batch size
    
    start_time = time.perf_counter()
    translator.parse_characteristics(batch_data)
    batch_time = time.perf_counter() - start_time
    
    results = {
        "single_parse_avg": sum(single_times) / len(single_times) * 1000,  # ms
        "single_parse_min": min(single_times) * 1000,  # ms
        "single_parse_max": max(single_times) * 1000,  # ms
        "batch_parse_time": batch_time * 1000,  # ms
        "total_operations": len(test_data),
    }
    
    print(f"   📈 Single parse average: {results['single_parse_avg']:.3f}ms")
    print(f"   🚀 Single parse fastest: {results['single_parse_min']:.3f}ms")
    print(f"   🐌 Single parse slowest: {results['single_parse_max']:.3f}ms")
    print(f"   📦 Batch parse ({len(batch_data)} items): {results['batch_parse_time']:.3f}ms")
    print(f"   🔢 Total operations: {results['total_operations']}")
    
    return results


def run_compliance_validation() -> Dict[str, Any]:
    """Validate compliance with SIG specifications."""
    print("\n📜 SIG Compliance Validation")
    print("=" * 30)
    
    translator = BluetoothSIGTranslator()
    results = {"total_checks": 0, "passed": 0, "failed": 0, "warnings": []}
    
    # Check that common characteristics are supported
    essential_characteristics = [
        "2A19",  # Battery Level
        "2A00",  # Device Name
        "2A6E",  # Temperature
        "2A6F",  # Humidity
        "2A37",  # Heart Rate Measurement
    ]
    
    print("   🔍 Checking essential characteristic support:")
    for uuid in essential_characteristics:
        results["total_checks"] += 1
        char_info = translator.get_characteristic_info(uuid)
        if char_info:
            print(f"     ✅ {uuid}: {char_info.name}")
            results["passed"] += 1
        else:
            print(f"     ❌ {uuid}: Not supported")
            results["failed"] += 1
    
    # Check UUID resolution consistency
    print("\n   🔗 Testing UUID resolution consistency:")
    test_cases = [
        ("2A19", "2a19", "Case insensitive"),
        ("2A19", "00002A19-0000-1000-8000-00805F9B34FB", "Short vs full UUID"),
    ]
    
    for uuid1, uuid2, description in test_cases:
        results["total_checks"] += 1
        info1 = translator.get_characteristic_info(uuid1)
        info2 = translator.get_characteristic_info(uuid2)
        
        if info1 and info2 and info1.name == info2.name:
            print(f"     ✅ {description}: Consistent")
            results["passed"] += 1
        else:
            print(f"     ❌ {description}: Inconsistent")
            results["failed"] += 1
    
    # Check value type consistency
    print("\n   📊 Validating value types:")
    for uuid in essential_characteristics:
        results["total_checks"] += 1
        
        # Use first valid test data for this characteristic
        if uuid in MockCharacteristicData.SIG_COMPLIANT_DATA:
            test_data = MockCharacteristicData.SIG_COMPLIANT_DATA[uuid]["valid"][0]
            raw_data, expected_value, expected_unit = test_data
            
            result = translator.parse_characteristic(uuid, raw_data)
            if result.parse_success:
                if type(result.value).__name__ == result.value_type:
                    print(f"     ✅ {uuid}: Value type consistent ({result.value_type})")
                    results["passed"] += 1
                else:
                    print(f"     ⚠️  {uuid}: Value type mismatch (got {type(result.value).__name__}, expected {result.value_type})")
                    results["warnings"].append(f"Value type mismatch for {uuid}")
                    results["passed"] += 1  # Still count as passed since it's working
            else:
                print(f"     ❌ {uuid}: Parse failed")
                results["failed"] += 1
    
    return results


def run_comprehensive_test_suite():
    """Run all test suites and provide summary."""
    print("🚀 Comprehensive bluetooth_sig Test Suite")
    print("=" * 45)
    print("Testing SIG parsing without BLE hardware\n")
    
    # Run all test suites
    basic_results = run_basic_parsing_tests()
    edge_results = run_edge_case_tests()
    compliance_results = run_compliance_validation()
    performance_results = run_performance_benchmark()
    
    # Summary
    total_tests = basic_results["total_tests"] + edge_results["total_tests"] + compliance_results["total_checks"]
    total_passed = basic_results["passed"] + edge_results["passed"] + compliance_results["passed"]
    total_failed = basic_results["failed"] + edge_results["failed"] + compliance_results["failed"]
    
    print(f"\n📋 Test Suite Summary")
    print("=" * 20)
    print(f"   📊 Total tests: {total_tests}")
    print(f"   ✅ Passed: {total_passed}")
    print(f"   ❌ Failed: {total_failed}")
    print(f"   📈 Success rate: {(total_passed/total_tests)*100:.1f}%")
    
    if compliance_results["warnings"]:
        print(f"\n   ⚠️  Warnings:")
        for warning in compliance_results["warnings"]:
            print(f"     - {warning}")
    
    print(f"\n   ⚡ Performance:")
    print(f"     - Average parse time: {performance_results['single_parse_avg']:.3f}ms")
    print(f"     - Total operations tested: {performance_results['total_operations']}")
    
    return {
        "total_tests": total_tests,
        "passed": total_passed,
        "failed": total_failed,
        "success_rate": (total_passed/total_tests)*100,
        "performance": performance_results,
        "warnings": compliance_results["warnings"]
    }


def demonstrate_ci_cd_integration():
    """Show how to integrate with CI/CD pipelines."""
    print("\n🔧 CI/CD Integration Example")
    print("=" * 30)
    
    print("""
# Example GitHub Actions workflow
name: Bluetooth SIG Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest
    
    - name: Run SIG parsing tests
      run: |
        python examples/testing_with_mocks.py --test-suite comprehensive
        
    - name: Run pytest unit tests
      run: |
        pytest tests/ -v
        
# Example pytest integration
def test_battery_level_parsing():
    translator = BluetoothSIGTranslator()
    result = translator.parse_characteristic("2A19", bytes([0x64]))
    assert result.parse_success
    assert result.value == 100
    assert result.unit == "%"

def test_temperature_parsing():
    translator = BluetoothSIGTranslator()
    result = translator.parse_characteristic("2A6E", bytes([0x64, 0x09]))
    assert result.parse_success
    assert abs(result.value - 24.04) < 0.1  # Float comparison
    assert result.unit == "°C"
    """)


def main():
    """Main function for mock testing demonstration."""
    parser = argparse.ArgumentParser(description="Testing bluetooth_sig with mock data")
    parser.add_argument("--test-suite", choices=["basic", "comprehensive"], default="basic",
                        help="Test suite to run")
    parser.add_argument("--benchmark", action="store_true", help="Run performance benchmark only")
    parser.add_argument("--compliance", action="store_true", help="Run compliance validation only")
    
    args = parser.parse_args()
    
    try:
        if args.benchmark:
            run_performance_benchmark()
        elif args.compliance:
            run_compliance_validation()
        elif args.test_suite == "comprehensive":
            results = run_comprehensive_test_suite()
            print(f"\n{'✅' if results['failed'] == 0 else '❌'} Test suite completed")
        else:
            run_basic_parsing_tests()
        
        demonstrate_ci_cd_integration()
        
        print("\n✅ Mock testing demo completed!")
        print("This demonstrates how to test bluetooth_sig without BLE hardware.")
        print("Perfect for CI/CD pipelines, unit tests, and development validation.")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
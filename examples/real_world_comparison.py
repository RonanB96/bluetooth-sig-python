#!/usr/bin/env python3
"""Real-World Integration Comparison: Manual vs Bluetooth SIG Library.

This example provides direct side-by-side comparison of manual BLE parsing
versus using the Bluetooth SIG library, demonstrating:

1. Code complexity differences
2. Standards compliance gaps in manual parsing
3. Missing features when parsing manually
4. Error handling and validation differences
5. Maintainability and future-proofing advantages

Usage:
    python real_world_comparison.py --address 12:34:56:78:9A:BC
    python real_world_comparison.py --mock  # Use mock data (no hardware)
    python real_world_comparison.py --benchmark  # Performance comparison
"""

# pylint: disable=import-error,broad-exception-caught,too-few-public-methods,possibly-used-before-assignment
# pylint: disable=too-many-branches,protected-access

from __future__ import annotations

import argparse
import asyncio
import struct
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import shared utilities
from ble_utils import (
    BLEAK_AVAILABLE,
    mock_ble_data,
    scan_with_bleak,
)

from bluetooth_sig import BluetoothSIGTranslator

# Try to import Bleak
if BLEAK_AVAILABLE:
    from bleak import BleakClient


@dataclass
class ParseComparison:
    """Results of parsing comparison between manual and SIG library."""

    characteristic_name: str
    raw_data: bytes
    manual_result: dict[str, Any]
    manual_error: str | None
    sig_result: Any
    sig_error: str | None
    features_comparison: dict[str, Any]


class ManualBLEParser:
    """Manual BLE parsing implementation to compare against SIG library.

    This demonstrates typical manual parsing approaches and their limitations.
    """

    def parse_battery_level(self, data: bytes) -> dict[str, Any]:
        """Manual battery level parsing - simple but incomplete."""
        try:
            if len(data) < 1:
                raise ValueError("Battery data too short")

            level = data[0]
            if level > 100:
                raise ValueError("Invalid battery level")

            return {
                "level": level,
                "unit": "%",
                "raw_bytes": len(data),
                # Missing: Status flags, timestamp, etc.
            }
        except Exception as e:
            return {"error": str(e)}

    def parse_temperature(self, data: bytes) -> dict[str, Any]:
        """Manual temperature parsing - error-prone and incomplete."""
        try:
            if len(data) < 2:
                raise ValueError("Temperature data too short")

            # Manual parsing - missing many SIG standard features
            raw_temp = struct.unpack("<h", data[:2])[0]
            celsius = raw_temp * 0.01

            return {
                "temperature": celsius,
                "unit": "°C",
                "raw_bytes": len(data),
                # Missing: timestamp, temperature type, measurement status, etc.
            }
        except Exception as e:
            return {"error": str(e)}

    def parse_heart_rate(self, data: bytes) -> dict[str, Any]:
        """Manual heart rate parsing - complex and error-prone."""
        try:
            if len(data) < 2:
                raise ValueError("Heart rate data too short")

            # Manual flag parsing - easy to get wrong
            flags = data[0]
            hr_format = flags & 0x01
            sensor_contact = (flags & 0x06) >> 1
            energy_expended = flags & 0x08
            rr_interval = flags & 0x10

            offset = 1

            # Heart rate value
            if hr_format == 0:
                # 8-bit
                heart_rate = data[offset]
                offset += 1
            else:
                # 16-bit
                if len(data) < offset + 2:
                    raise ValueError("Invalid heart rate data length")
                heart_rate = struct.unpack("<H", data[offset : offset + 2])[0]
                offset += 2

            result = {
                "heart_rate": heart_rate,
                "unit": "bpm",
                "sensor_contact": sensor_contact == 3,
                "raw_bytes": len(data),
                # Missing proper flag interpretation, energy expended parsing, etc.
            }

            # Energy expended (if present) - manual parsing is complex
            if energy_expended and len(data) >= offset + 2:
                energy = struct.unpack("<H", data[offset : offset + 2])[0]
                result["energy_expended"] = energy
                offset += 2

            # RR intervals (if present) - manual parsing is very complex
            if rr_interval and len(data) > offset:
                # This would require complex manual parsing
                result["rr_intervals_available"] = True
                # Manual parsing would likely skip this due to complexity

            return result

        except Exception as e:
            return {"error": str(e)}

    def parse_device_info_string(self, data: bytes) -> dict[str, Any]:
        """Manual device information string parsing."""
        try:
            # Simple UTF-8 decode - missing encoding detection, language, etc.
            text = data.decode("utf-8").strip("\x00")
            return {
                "value": text,
                "encoding": "utf-8",  # Assumed, not detected
                "raw_bytes": len(data),
                # Missing: proper encoding detection, language tags, etc.
            }
        except Exception as e:
            try:
                # Fallback to latin-1
                text = data.decode("latin-1").strip("\x00")
                return {
                    "value": text,
                    "encoding": "latin-1",  # Fallback
                    "raw_bytes": len(data),
                }
            except Exception as e2:
                return {"error": f"Decode failed: {e}, {e2}"}

    def parse_humidity(self, data: bytes) -> dict[str, Any]:
        """Manual humidity parsing."""
        try:
            if len(data) < 2:
                raise ValueError("Humidity data too short")

            # Manual parsing - basic implementation
            raw_humidity = struct.unpack("<H", data[:2])[0]
            humidity = raw_humidity * 0.01

            return {
                "humidity": humidity,
                "unit": "%",
                "raw_bytes": len(data),
                # Missing: status flags, measurement conditions, etc.
            }
        except Exception as e:
            return {"error": str(e)}


class ComparisonAnalyzer:
    """Analyzes differences between manual and SIG library parsing."""

    def __init__(self):
        self.manual_parser = ManualBLEParser()
        self.sig_translator = BluetoothSIGTranslator()

    def compare_parsing(self, characteristic_uuid: str, data: bytes) -> ParseComparison:
        """Compare manual vs SIG library parsing for a characteristic."""

        # Get characteristic info
        char_info = self.sig_translator.get_characteristic_info(characteristic_uuid)
        char_name = char_info.name if char_info else f"Unknown-{characteristic_uuid}"

        # Manual parsing
        manual_result = None
        manual_error = None
        try:
            manual_result = self._manual_parse_by_uuid(characteristic_uuid, data)
        except Exception as e:
            manual_error = str(e)

        # SIG library parsing
        sig_result = None
        sig_error = None
        try:
            sig_parse_result = self.sig_translator.parse_characteristic(
                characteristic_uuid, data
            )
            if sig_parse_result.parse_success:
                sig_result = sig_parse_result
            else:
                sig_error = sig_parse_result.error_message
        except Exception as e:
            sig_error = str(e)

        # Analyze feature differences
        features_comparison = self._analyze_features(manual_result, sig_result)

        return ParseComparison(
            characteristic_name=char_name,
            raw_data=data,
            manual_result=manual_result,
            manual_error=manual_error,
            sig_result=sig_result,
            sig_error=sig_error,
            features_comparison=features_comparison,
        )

    def _manual_parse_by_uuid(self, uuid: str, data: bytes) -> dict[str, Any]:
        """Route to appropriate manual parser based on UUID."""
        uuid = uuid.upper()

        # Map UUIDs to manual parsing methods
        parsers = {
            "2A19": self.manual_parser.parse_battery_level,
            "2A6E": self.manual_parser.parse_temperature,
            "2A37": self.manual_parser.parse_heart_rate,
            "2A6F": self.manual_parser.parse_humidity,
            "2A29": self.manual_parser.parse_device_info_string,  # Manufacturer
            "2A24": self.manual_parser.parse_device_info_string,  # Model
            "2A25": self.manual_parser.parse_device_info_string,  # Serial
        }

        parser = parsers.get(uuid)
        if not parser:
            raise ValueError(f"No manual parser for UUID {uuid}")

        return parser(data)

    def _analyze_features(self, manual_result: dict, sig_result: Any) -> dict[str, Any]:
        """Analyze feature differences between manual and SIG parsing."""

        features = {
            "manual_features": [],
            "sig_features": [],
            "missing_in_manual": [],
            "code_complexity": {},
            "standards_compliance": {},
        }

        # Analyze manual result
        if manual_result and not manual_result.get("error"):
            features["manual_features"] = list(manual_result.keys())
            features["code_complexity"]["manual"] = (
                "High - custom parsing logic required"
            )
            features["standards_compliance"]["manual"] = "Partial - basic parsing only"

        # Analyze SIG result
        if sig_result and sig_result.parse_success:
            # Count SIG features
            sig_features = ["value", "unit", "name", "parse_success"]
            if hasattr(sig_result.value, "__dict__"):
                sig_features.extend(sig_result.value.__dict__.keys())

            features["sig_features"] = sig_features
            features["code_complexity"]["sig"] = "Low - single method call"
            features["standards_compliance"]["sig"] = (
                "Full - official SIG specifications"
            )

            # Find missing features in manual parsing
            if manual_result and not manual_result.get("error"):
                manual_keys = set(manual_result.keys())
                sig_keys = set(sig_features)
                features["missing_in_manual"] = list(sig_keys - manual_keys)

        return features


async def run_comparison_with_device(address: str, timeout: float = 10.0) -> None:
    """Run comparison using real device data."""

    if not BLEAK_AVAILABLE:
        print("❌ Bleak not available. Install with: pip install bleak")
        return

    analyzer = ComparisonAnalyzer()

    print(f"🔗 Connecting to device: {address}")

    try:
        async with BleakClient(address, timeout=timeout) as client:
            print("✅ Connected successfully!")

            # Find readable characteristics to compare
            test_characteristics = await find_comparable_characteristics(
                client, analyzer.sig_translator
            )

            if not test_characteristics:
                print("❌ No suitable characteristics found for comparison")
                return

            print(f"\n📊 Comparing {len(test_characteristics)} characteristics:")

            comparisons = []

            for char_uuid, char_obj in test_characteristics.items():
                try:
                    # Read data from device
                    raw_data = await client.read_gatt_char(char_obj)

                    # Compare parsing approaches
                    comparison = analyzer.compare_parsing(char_uuid, raw_data)
                    comparisons.append(comparison)

                    # Display comparison
                    display_comparison(comparison)

                except Exception as e:
                    print(f"❌ Failed to read {char_uuid}: {e}")

            # Summary
            display_summary(comparisons)

    except Exception as e:
        print(f"❌ Connection failed: {e}")


async def find_comparable_characteristics(
    client, translator: BluetoothSIGTranslator
) -> dict[str, Any]:
    """Find characteristics that can be compared between manual and SIG parsing."""

    # UUIDs we have manual parsers for
    comparable_uuids = {"2A19", "2A6E", "2A37", "2A6F", "2A29", "2A24", "2A25"}

    found_characteristics = {}

    for service in client.services:
        for char in service.characteristics:
            char_uuid = str(char.uuid)[4:8].upper()  # Extract 16-bit UUID

            if char_uuid in comparable_uuids and "read" in char.properties:
                char_info = translator.get_characteristic_info(char.uuid)
                char_name = char_info.name if char_info else f"Unknown-{char_uuid}"

                print(f"📋 Found comparable: {char_name} ({char_uuid})")
                found_characteristics[char_uuid] = char

    return found_characteristics


def run_mock_comparison() -> None:
    """Run comparison using mock data."""

    print("🧪 MOCK DATA COMPARISON")
    print("=" * 50)
    print("Comparing manual vs SIG library parsing with mock data")

    analyzer = ComparisonAnalyzer()
    mock_data = mock_ble_data()

    # Test characteristics with mock data
    test_cases = [
        ("2A19", mock_data["2A19"], "Battery Level"),
        ("2A6E", mock_data["2A6E"], "Temperature"),
        ("2A6F", mock_data["2A6F"], "Humidity"),
    ]

    # Add more complex mock data for heart rate
    test_cases.append(
        (
            "2A37",
            bytes([0x01, 0x48, 0x00, 0x40, 0x01]),  # Heart rate with sensor contact
            "Heart Rate Measurement",
        )
    )

    # Add device info string
    test_cases.append(
        (
            "2A29",
            b"ExampleCorp\x00",  # Manufacturer name
            "Manufacturer Name String",
        )
    )

    comparisons = []

    print(f"\n📊 Comparing {len(test_cases)} characteristics:")

    for uuid, data, name in test_cases:
        print("\n" + "=" * 60)
        print(f"🔧 Testing: {name} ({uuid})")
        print(f"🔢 Mock Data: {data.hex()}")

        comparison = analyzer.compare_parsing(uuid, data)
        comparisons.append(comparison)

        display_comparison(comparison)

    # Summary
    display_summary(comparisons)


def display_comparison(comparison: ParseComparison) -> None:
    """Display detailed comparison results."""

    print(f"\n--- {comparison.characteristic_name} Comparison ---")

    # Manual parsing results
    print("\n🔧 Manual Parsing:")
    if comparison.manual_error:
        print(f"   ❌ Error: {comparison.manual_error}")
    elif comparison.manual_result:
        print("   📊 Results:")
        for key, value in comparison.manual_result.items():
            print(f"      {key}: {value}")
    else:
        print("   ❌ No result")

    # SIG library results
    print("\n✨ Bluetooth SIG Library:")
    if comparison.sig_error:
        print(f"   ❌ Error: {comparison.sig_error}")
    elif comparison.sig_result:
        print("   📊 Results:")
        print(f"      Name: {comparison.sig_result.name}")
        print(f"      Value: {comparison.sig_result.value}")
        print(f"      Unit: {comparison.sig_result.unit}")
        print(f"      Parse Success: {comparison.sig_result.parse_success}")

        # Show structured data if available
        if hasattr(comparison.sig_result.value, "__dict__"):
            print("      Structured Data:")
            for key, value in comparison.sig_result.value.__dict__.items():
                if not key.startswith("_"):
                    print(f"         {key}: {value}")
    else:
        print("   ❌ No result")

    # Feature comparison
    features = comparison.features_comparison
    print("\n📈 Feature Analysis:")

    if features.get("code_complexity"):
        print("   Code Complexity:")
        for approach, complexity in features["code_complexity"].items():
            print(f"      {approach.capitalize()}: {complexity}")

    if features.get("standards_compliance"):
        print("   Standards Compliance:")
        for approach, compliance in features["standards_compliance"].items():
            print(f"      {approach.capitalize()}: {compliance}")

    if features.get("missing_in_manual"):
        print("   ⚠️  Missing in Manual Parsing:")
        for feature in features["missing_in_manual"]:
            print(f"      - {feature}")


def display_summary(comparisons: list[ParseComparison]) -> None:
    """Display overall summary of comparisons."""

    print("\n" + "=" * 60)
    print("📊 COMPARISON SUMMARY")
    print("=" * 60)

    total_tests = len(comparisons)
    manual_successes = sum(
        1 for c in comparisons if c.manual_result and not c.manual_error
    )
    sig_successes = sum(1 for c in comparisons if c.sig_result and not c.sig_error)

    print("\n📈 Success Rates:")
    print(
        f"   Manual Parsing: {manual_successes}/{total_tests} ({manual_successes / total_tests * 100:.1f}%)"
    )
    print(
        f"   SIG Library: {sig_successes}/{total_tests} ({sig_successes / total_tests * 100:.1f}%)"
    )

    # Count missing features
    total_missing_features = 0
    for comparison in comparisons:
        missing = comparison.features_comparison.get("missing_in_manual", [])
        total_missing_features += len(missing)

    print("\n🎯 Key Advantages of Bluetooth SIG Library:")
    print(
        f"   ✅ Higher success rate: {sig_successes - manual_successes} more successful parses"
    )
    print("   ✅ Standards compliance: Full SIG specification implementation")
    print(
        f"   ✅ Rich data extraction: {total_missing_features} additional features extracted"
    )
    print("   ✅ Lower complexity: Single method call vs custom parsing logic")
    print("   ✅ Error handling: Comprehensive validation and error reporting")
    print("   ✅ Future-proof: Automatic updates with SIG specification changes")

    print("\n🔧 Manual Parsing Limitations:")
    print("   ❌ Custom code required for each characteristic")
    print("   ❌ Easy to introduce bugs in bit manipulation")
    print("   ❌ Missing advanced features (timestamps, status flags, etc.)")
    print("   ❌ No automatic validation")
    print("   ❌ Manual maintenance required for spec updates")


def run_benchmark_comparison() -> None:
    """Run performance benchmark between manual and SIG parsing."""

    print("⚡ PERFORMANCE BENCHMARK")
    print("=" * 50)

    analyzer = ComparisonAnalyzer()
    mock_data = mock_ble_data()

    # Test data
    test_data = [
        ("2A19", mock_data["2A19"]),
        ("2A6E", mock_data["2A6E"]),
        ("2A6F", mock_data["2A6F"]),
    ]

    iterations = 1000

    print(f"Running {iterations} iterations for each characteristic...")

    for uuid, data in test_data:
        char_info = analyzer.sig_translator.get_characteristic_info(uuid)
        char_name = char_info.name if char_info else f"UUID-{uuid}"

        # Benchmark manual parsing
        start_time = time.perf_counter()
        for _ in range(iterations):
            try:
                analyzer._manual_parse_by_uuid(uuid, data)
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        manual_time = time.perf_counter() - start_time

        # Benchmark SIG parsing
        start_time = time.perf_counter()
        for _ in range(iterations):
            analyzer.sig_translator.parse_characteristic(uuid, data)
        sig_time = time.perf_counter() - start_time

        print(f"\n📊 {char_name}:")
        print(
            f"   Manual: {manual_time * 1000:.2f}ms ({manual_time / iterations * 1000000:.1f}μs per parse)"
        )
        print(
            f"   SIG Library: {sig_time * 1000:.2f}ms ({sig_time / iterations * 1000000:.1f}μs per parse)"
        )

        if manual_time > 0:
            ratio = sig_time / manual_time
            if ratio < 1:
                print(f"   🚀 SIG Library is {1 / ratio:.1f}x faster")
            else:
                print(f"   ⚡ Manual is {ratio:.1f}x faster")


async def main():
    """Main entry point for real-world comparison."""

    parser = argparse.ArgumentParser(
        description="Real-world comparison: Manual vs Bluetooth SIG library parsing"
    )
    parser.add_argument("--address", help="BLE device address to connect to")
    parser.add_argument(
        "--scan", action="store_true", help="Scan for nearby BLE devices"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run comparison with mock data (no hardware required)",
    )
    parser.add_argument(
        "--benchmark", action="store_true", help="Run performance benchmark"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Connection timeout in seconds (default: 10.0)",
    )

    args = parser.parse_args()

    print("🚀 Real-World Integration Comparison")
    print("Manual BLE Parsing vs Bluetooth SIG Library")
    print()

    if args.benchmark:
        run_benchmark_comparison()
        return

    if args.mock:
        run_mock_comparison()
        return

    if args.scan:
        print("🔍 Scanning for BLE devices...")
        devices = await scan_with_bleak(timeout=10.0)
        if devices:
            print(
                f"\n📱 Found {len(devices)} devices. Use --address with one of these:"
            )
            for device in devices[:5]:
                print(f"   {device.address} - {device.name or 'Unknown'}")
        else:
            print("❌ No devices found")
        return

    if not args.address:
        print("❌ Error: Must specify --address, --scan, --mock, or --benchmark")
        print("Examples:")
        print("  python real_world_comparison.py --mock")
        print("  python real_world_comparison.py --benchmark")
        print("  python real_world_comparison.py --scan")
        print("  python real_world_comparison.py --address 12:34:56:78:9A:BC")
        return

    await run_comparison_with_device(args.address, args.timeout)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

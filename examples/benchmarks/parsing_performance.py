#!/usr/bin/env python3
"""Performance benchmark for Bluetooth SIG parsing.

This example demonstrates:
1. Measuring parse latency for various characteristic types
2. Comparing manual vs SIG library parsing performance
3. Batch parsing performance measurement
4. Memory and throughput characteristics

Run with optional logging:
    python parsing_performance.py --log-level=debug
    python parsing_performance.py --log-level=info
"""

import argparse
import logging
import struct
import sys
from pathlib import Path

# Set up paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.utils.profiling import (
    ProfilingSession,
    benchmark_function,
    compare_implementations,
    format_comparison,
)


def manual_battery_parse(data: bytes) -> int:
    """Manual battery parsing - minimal features."""
    return data[0]


def manual_temperature_parse(data: bytes) -> float:
    """Manual temperature parsing - minimal features."""
    temp_raw: int = struct.unpack("<h", data[:2])[0]  # type: ignore[assignment]
    return temp_raw * 0.01


def manual_heart_rate_parse(data: bytes) -> int:
    """Manual heart rate parsing - minimal features."""
    flags = data[0]
    if flags & 0x01:
        hr_value: int = struct.unpack("<H", data[1:3])[0]  # type: ignore[assignment]
        return hr_value
    return data[1]


def benchmark_single_characteristic_parsing(session: ProfilingSession) -> None:
    """Benchmark parsing of individual characteristics."""
    print("\n" + "=" * 80)
    print("Single Characteristic Parsing Benchmark")
    print("=" * 80)

    translator = BluetoothSIGTranslator()
    iterations = 10000

    # Battery Level (simple, 1 byte)
    battery_data = bytes([0x64])  # 100%

    print("\n1. Battery Level (1 byte, simple)")
    print(f"   Testing with {iterations} iterations...")

    results = compare_implementations(
        {
            "manual": lambda: manual_battery_parse(battery_data),
            "sig_library": lambda: translator.parse_characteristic("2A19", battery_data),
        },
        iterations=iterations,
    )

    print(format_comparison(results, baseline="manual"))
    session.add_result(results["sig_library"])

    # Temperature (2 bytes, simple)
    temp_data = bytes([0x64, 0x09])  # 24.20°C

    print("\n2. Temperature (2 bytes, moderate complexity)")
    print(f"   Testing with {iterations} iterations...")

    results = compare_implementations(
        {
            "manual": lambda: manual_temperature_parse(temp_data),
            "sig_library": lambda: translator.parse_characteristic("2A6E", temp_data),
        },
        iterations=iterations,
    )

    print(format_comparison(results, baseline="manual"))
    session.add_result(results["sig_library"])

    # Heart Rate (complex with flags)
    hr_data = bytes([0x0E, 0x5A, 0x01])  # 90 bpm with contact detected

    print("\n3. Heart Rate Measurement (complex with flags)")
    print(f"   Testing with {iterations} iterations...")

    results = compare_implementations(
        {
            "manual": lambda: manual_heart_rate_parse(hr_data),
            "sig_library": lambda: translator.parse_characteristic("2A37", hr_data),
        },
        iterations=iterations,
    )

    print(format_comparison(results, baseline="manual"))
    session.add_result(results["sig_library"])


def benchmark_batch_parsing(session: ProfilingSession) -> None:
    """Benchmark batch parsing of multiple characteristics."""
    print("\n" + "=" * 80)
    print("Batch Parsing Benchmark")
    print("=" * 80)

    translator = BluetoothSIGTranslator()
    iterations = 1000

    # Simulate data from multiple sensors (typical smart device)
    sensor_data = {  # pylint: disable=duplicate-code
        # NOTE: Test sensor data duplicates pure_sig_parsing example fixture.
        # Duplication justified because:
        # 1. Standard test dataset for demonstrating multi-characteristic parsing
        # 2. Each example demonstrates different aspects (pure parsing vs performance)
        # 3. Self-contained examples are more educational than shared test data
        "2A19": bytes([0x55]),  # 85% battery
        "2A6E": bytes([0x58, 0x07]),  # 18.64°C temperature
        "2A6F": bytes([0x38, 0x19]),  # 65.12% humidity
        "2A6D": bytes([0x70, 0x96, 0x00, 0x00]),  # 996.8 hPa pressure
    }

    print("\nBatching 4 characteristics together")
    print(f"Testing with {iterations} iterations...")

    # Batch parsing
    batch_result = benchmark_function(
        lambda: translator.parse_characteristics(sensor_data),
        iterations=iterations,
        operation="Batch parse (4 characteristics)",
    )

    # Individual parsing for comparison
    def parse_individually() -> None:
        for uuid, data in sensor_data.items():
            translator.parse_characteristic(uuid, data)

    individual_result = benchmark_function(
        parse_individually,
        iterations=iterations,
        operation="Individual parse (4 characteristics)",
    )

    print(format_comparison({"batch": batch_result, "individual": individual_result}, baseline="individual"))

    session.add_result(batch_result)


def benchmark_uuid_resolution(session: ProfilingSession) -> None:
    """Benchmark UUID resolution performance."""
    print("\n" + "=" * 80)
    print("UUID Resolution Benchmark")
    print("=" * 80)

    translator = BluetoothSIGTranslator()
    iterations = 10000

    print(f"\nTesting with {iterations} iterations...")

    # UUID lookup
    uuid_lookup = benchmark_function(
        lambda: translator.get_characteristic_info_by_uuid("2A19"),
        iterations=iterations,
        operation="UUID lookup",
    )

    # Name resolution
    name_resolution = benchmark_function(
        lambda: translator.get_sig_info_by_name("Battery Level"),
        iterations=iterations,
        operation="Name resolution",
    )

    print(
        format_comparison(
            {
                "uuid_lookup": uuid_lookup,
                "name_resolution": name_resolution,
            }
        )
    )

    session.add_result(uuid_lookup)


def benchmark_real_world_scenario(session: ProfilingSession) -> None:
    """Benchmark a realistic device interaction scenario."""
    print("\n" + "=" * 80)
    print("Real-World Scenario Benchmark")
    print("=" * 80)
    print("Simulating: Health thermometer device with periodic readings")

    translator = BluetoothSIGTranslator()
    iterations = 5000

    # Typical health thermometer notification payload
    # Temperature Measurement characteristic (0x2A1C)
    temp_measurement_data = bytes.fromhex("06FE06E507E4070100")

    print(f"\nSimulating {iterations} temperature notifications...")

    result = benchmark_function(
        lambda: translator.parse_characteristic("2A1C", temp_measurement_data),
        iterations=iterations,
        operation="Health thermometer notification",
    )

    print(str(result))
    print("\nFor a device sending notifications every 1 second:")
    print(f"  CPU time per notification: {result.avg_time * 1000:.4f}ms")
    print(f"  Percentage of 1s interval: {result.avg_time * 100:.4f}%")
    print(f"  Could handle {int(result.per_second)} concurrent devices")

    session.add_result(result)


def print_summary(session: ProfilingSession) -> None:
    """Print summary of all benchmark results."""
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY")
    print("=" * 80)

    print(f"\nProfile: {session.name}")
    print(f"Total operations measured: {len(session.results)}")

    if session.results:
        avg_throughput = sum(r.per_second for r in session.results) / len(session.results)
        avg_latency = sum(r.avg_time for r in session.results) / len(session.results)

        print("\nAverage performance across all tests:")
        print(f"  Latency:    {avg_latency * 1000:.4f}ms per operation")
        print(f"  Throughput: {avg_throughput:.0f} operations/sec")

    print("\n" + "=" * 80)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)
    print("""
1. For high-throughput applications:
   - Use batch parsing (parse_characteristics) when possible
   - Process notifications in batches rather than one-by-one
   - Cache characteristic info lookups if parsing same UUIDs repeatedly

2. For low-latency applications:
   - The library adds minimal overhead (<0.1ms for simple characteristics)
   - Consider using individual parsing with pre-resolved UUIDs
   - Enable logging only for debugging (adds ~10-20% overhead)

3. Memory optimization:
   - Reuse BluetoothSIGTranslator instance (don't create per parse)
   - Clear service cache periodically if tracking many devices
   - Use streaming/generator patterns for large batches

4. Code hot paths identified:
   - CharacteristicRegistry.create_characteristic (UUID lookup)
   - Characteristic.parse_value (parsing logic)
   - Context building in batch operations
    """)


def main() -> None:
    """Run the performance benchmarks."""
    parser = argparse.ArgumentParser(description="Benchmark Bluetooth SIG library parsing performance")
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="warning",
        help="Set logging level (default: warning for minimal overhead)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick benchmark with fewer iterations",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if log_level <= logging.INFO:
        print(f"\n⚠️  Logging enabled at {args.log_level.upper()} level")
        print("    Note: Logging adds overhead and will affect benchmark results")

    print("\n🚀 Bluetooth SIG Library Performance Benchmark")
    print("=" * 80)

    session = ProfilingSession(name="Parsing Performance Benchmark")

    try:
        # Run all benchmarks
        benchmark_single_characteristic_parsing(session)
        benchmark_batch_parsing(session)
        benchmark_uuid_resolution(session)
        benchmark_real_world_scenario(session)

        # Print summary
        print_summary(session)

        print("\n✅ Benchmark complete!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        print(f"\n\n❌ Benchmark failed ({type(e).__name__}): {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

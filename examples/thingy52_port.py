#!/usr/bin/env python3
"""Nordic Thingy:52 demonstration using bluetooth-sig-python library.

This example demonstrates how to use the bluetooth-sig-python library to parse
Nordic Thingy:52 sensor data, combining both SIG-standard characteristics
(like Battery Level) and vendor-specific Nordic characteristics (environmental,
motion, and UI sensors).

This is a port of the original BluePy Thingy:52 example, showcasing the improved
architecture with:
- Type-safe msgspec.Struct-based data models
- Clean separation of decoding logic
- No hardcoded UUID strings in parsing logic
- Consistent API patterns for SIG and vendor characteristics
- Comprehensive error handling

Requirements:
    - bluetooth-sig library (this library)
    - BLE connection library (bleak, simplepyble, or bluepy)

Usage:
    # With mock data (no device required)
    python thingy52_port.py --mock

    # With real device (requires BLE library and device address)
    python thingy52_port.py --address AA:BB:CC:DD:EE:FF

References:
    - Nordic Thingy:52 Documentation:
      https://nordicsemiconductor.github.io/Nordic-Thingy52-FW/documentation
    - Original BluePy Implementation:
      https://github.com/IanHarvey/bluepy/blob/master/bluepy/thingy52.py
    - Bluetooth SIG Assigned Numbers:
      https://www.bluetooth.com/specifications/assigned-numbers/
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path
from typing import Any

# Add project root to path for imports
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

# Import SIG characteristic parsing from bluetooth-sig library
from bluetooth_sig import BluetoothSIGTranslator

# Import vendor characteristic decoders
from examples.vendor_characteristics import (
    BUTTON_CHAR_UUID,
    COLOR_CHAR_UUID,
    EULER_CHAR_UUID,
    GAS_CHAR_UUID,
    GRAVITY_VECTOR_CHAR_UUID,
    HEADING_CHAR_UUID,
    HUMIDITY_CHAR_UUID,
    ORIENTATION_CHAR_UUID,
    PRESSURE_CHAR_UUID,
    QUATERNION_CHAR_UUID,
    RAW_DATA_CHAR_UUID,
    ROTATION_MATRIX_CHAR_UUID,
    STEP_COUNTER_CHAR_UUID,
    TAP_CHAR_UUID,
    TEMPERATURE_CHAR_UUID,
    decode_thingy_button,
    decode_thingy_color,
    decode_thingy_euler,
    decode_thingy_gas,
    decode_thingy_gravity_vector,
    decode_thingy_heading,
    decode_thingy_humidity,
    decode_thingy_orientation,
    decode_thingy_pressure,
    decode_thingy_quaternion,
    decode_thingy_raw_motion,
    decode_thingy_rotation_matrix,
    decode_thingy_step_counter,
    decode_thingy_tap,
    decode_thingy_temperature,
)


def generate_mock_thingy_data() -> dict[str, bytes]:
    """Generate mock Thingy:52 sensor data for demonstration.

    Returns:
        Dictionary mapping characteristic UUIDs to mock sensor data bytes.
    """
    return {
        # SIG Battery Level characteristic (0x2A19)
        "2A19": bytes([85]),  # 85% battery
        # Nordic vendor characteristics
        TEMPERATURE_CHAR_UUID: bytes([0x17, 0x32]),  # 23.50°C
        PRESSURE_CHAR_UUID: bytes([0xE0, 0x8A, 0x01, 0x00, 0x32]),  # 101088.50 Pa
        HUMIDITY_CHAR_UUID: bytes([0x41]),  # 65%
        GAS_CHAR_UUID: bytes([0x90, 0x01, 0x32, 0x00]),  # eCO2: 400ppm, TVOC: 50ppb
        COLOR_CHAR_UUID: bytes([0xFF, 0x00, 0x80, 0x00, 0x40, 0x00, 0x00, 0x01]),  # R:255, G:128, B:64, C:256
        BUTTON_CHAR_UUID: bytes([0x00]),  # Button released
        TAP_CHAR_UUID: bytes([0x02, 0x03]),  # y+ direction, 3 taps
        ORIENTATION_CHAR_UUID: bytes([0x01]),  # Landscape
        QUATERNION_CHAR_UUID: struct.pack("<iiii", 1073741824, 0, 0, 0),  # w=1.0 (fixed-point)
        STEP_COUNTER_CHAR_UUID: bytes([0x64, 0x00, 0x00, 0x00, 0x10, 0x27, 0x00, 0x00]),  # 100 steps, 10000ms
        RAW_DATA_CHAR_UUID: struct.pack("<hhhhhhhhh", 100, 200, 300, 10, 20, 30, 5, 10, 15),
        EULER_CHAR_UUID: struct.pack("<iii", 0, 0, 0),  # Roll, pitch, yaw = 0
        ROTATION_MATRIX_CHAR_UUID: struct.pack("<hhhhhhhhh", 32767, 0, 0, 0, 32767, 0, 0, 0, 32767),  # Identity-ish
        HEADING_CHAR_UUID: struct.pack("<i", 5898240),  # ~90 degrees (90 * 65536)
        GRAVITY_VECTOR_CHAR_UUID: struct.pack("<fff", 0.0, 0.0, 9.81),  # Standard gravity
    }


def parse_and_display_thingy_data(mock_data: dict[str, bytes]) -> dict[str, Any]:
    """Parse and display Thingy:52 sensor data using bluetooth-sig-python.

    This function demonstrates the consistent API between SIG and vendor
    characteristics - users don't need to know if a characteristic is
    SIG-standard or vendor-specific.

    Args:
        mock_data: Dictionary mapping UUIDs to raw characteristic bytes.

    Returns:
        Dictionary of parsed sensor values.
    """
    translator = BluetoothSIGTranslator()
    results: dict[str, Any] = {}

    print("\n" + "=" * 70)
    print("Nordic Thingy:52 Sensor Data - Parsed with bluetooth-sig-python")
    print("=" * 70)

    # ========================================================================
    # SIG Standard Characteristics - Use translator.parse_characteristic()
    # ========================================================================

    print("\n📊 SIG Standard Characteristics:")
    print("-" * 70)

    if "2A19" in mock_data:
        try:
            battery_result = translator.parse_characteristic("2A19", mock_data["2A19"], None)
            print(f"  Battery Level: {battery_result.value}%")
            results["battery_level"] = battery_result.value
        except Exception as e:
            print(f"  Battery Level: Error - {e}")

    # ========================================================================
    # Vendor Environment Characteristics - Use decode functions
    # ========================================================================

    print("\n🌡️  Environment Sensors:")
    print("-" * 70)

    if TEMPERATURE_CHAR_UUID in mock_data:
        try:
            temp_data = decode_thingy_temperature(mock_data[TEMPERATURE_CHAR_UUID])
            temp_celsius = temp_data.temperature_celsius + (temp_data.temperature_decimal / 100.0)
            print(f"  Temperature: {temp_celsius:.2f}°C")
            results["temperature"] = temp_celsius
        except Exception as e:
            print(f"  Temperature: Error - {e}")

    if PRESSURE_CHAR_UUID in mock_data:
        try:
            pressure_data = decode_thingy_pressure(mock_data[PRESSURE_CHAR_UUID])
            pressure_pa = pressure_data.pressure_integer + (pressure_data.pressure_decimal / 100.0)
            pressure_hpa = pressure_pa / 100.0  # Convert Pa to hPa
            print(f"  Pressure: {pressure_hpa:.2f} hPa ({pressure_pa:.2f} Pa)")
            results["pressure_hpa"] = pressure_hpa
        except Exception as e:
            print(f"  Pressure: Error - {e}")

    if HUMIDITY_CHAR_UUID in mock_data:
        try:
            humidity_data = decode_thingy_humidity(mock_data[HUMIDITY_CHAR_UUID])
            print(f"  Humidity: {humidity_data.humidity_percent}%")
            results["humidity"] = humidity_data.humidity_percent
        except Exception as e:
            print(f"  Humidity: Error - {e}")

    if GAS_CHAR_UUID in mock_data:
        try:
            gas_data = decode_thingy_gas(mock_data[GAS_CHAR_UUID])
            print("  Air Quality:")
            print(f"    eCO2: {gas_data.eco2_ppm} ppm")
            print(f"    TVOC: {gas_data.tvoc_ppb} ppb")
            results["eco2"] = gas_data.eco2_ppm
            results["tvoc"] = gas_data.tvoc_ppb
        except Exception as e:
            print(f"  Air Quality: Error - {e}")

    if COLOR_CHAR_UUID in mock_data:
        try:
            color_data = decode_thingy_color(mock_data[COLOR_CHAR_UUID])
            print("  Color Sensor:")
            print(f"    Red: {color_data.red}")
            print(f"    Green: {color_data.green}")
            print(f"    Blue: {color_data.blue}")
            print(f"    Clear: {color_data.clear}")
            results["color"] = {
                "r": color_data.red,
                "g": color_data.green,
                "b": color_data.blue,
                "c": color_data.clear,
            }
        except Exception as e:
            print(f"  Color Sensor: Error - {e}")

    # ========================================================================
    # Vendor User Interface Characteristics
    # ========================================================================

    print("\n🔘 User Interface:")
    print("-" * 70)

    if BUTTON_CHAR_UUID in mock_data:
        try:
            button_data = decode_thingy_button(mock_data[BUTTON_CHAR_UUID])
            button_state = "Pressed" if button_data.pressed else "Released"
            print(f"  Button: {button_state}")
            results["button_pressed"] = button_data.pressed
        except Exception as e:
            print(f"  Button: Error - {e}")

    # ========================================================================
    # Vendor Motion Characteristics
    # ========================================================================

    print("\n🏃 Motion Sensors:")
    print("-" * 70)

    if TAP_CHAR_UUID in mock_data:
        try:
            tap_data = decode_thingy_tap(mock_data[TAP_CHAR_UUID])
            directions = ["x+", "x-", "y+", "y-", "z+", "z-"]
            direction_name = directions[tap_data.direction] if tap_data.direction < 6 else "unknown"
            print(f"  Tap Detection: {tap_data.count} taps in {direction_name} direction")
            results["tap"] = {"direction": direction_name, "count": tap_data.count}
        except Exception as e:
            print(f"  Tap Detection: Error - {e}")

    if ORIENTATION_CHAR_UUID in mock_data:
        try:
            orientation_data = decode_thingy_orientation(mock_data[ORIENTATION_CHAR_UUID])
            orientations = ["Portrait", "Landscape", "Reverse Portrait"]
            orientation_name = (
                orientations[orientation_data.orientation] if orientation_data.orientation < 3 else "Unknown"
            )
            print(f"  Orientation: {orientation_name}")
            results["orientation"] = orientation_name
        except Exception as e:
            print(f"  Orientation: Error - {e}")

    if QUATERNION_CHAR_UUID in mock_data:
        try:
            quat_data = decode_thingy_quaternion(mock_data[QUATERNION_CHAR_UUID])
            # Convert fixed-point to float (divide by 2^30)
            scale = 2**30
            print("  Quaternion:")
            print(f"    w: {quat_data.w / scale:.4f}")
            print(f"    x: {quat_data.x / scale:.4f}")
            print(f"    y: {quat_data.y / scale:.4f}")
            print(f"    z: {quat_data.z / scale:.4f}")
            results["quaternion"] = {
                "w": quat_data.w / scale,
                "x": quat_data.x / scale,
                "y": quat_data.y / scale,
                "z": quat_data.z / scale,
            }
        except Exception as e:
            print(f"  Quaternion: Error - {e}")

    if STEP_COUNTER_CHAR_UUID in mock_data:
        try:
            step_data = decode_thingy_step_counter(mock_data[STEP_COUNTER_CHAR_UUID])
            print(f"  Step Counter: {step_data.steps} steps ({step_data.time_ms}ms)")
            results["steps"] = step_data.steps
        except Exception as e:
            print(f"  Step Counter: Error - {e}")

    if RAW_DATA_CHAR_UUID in mock_data:
        try:
            raw_data = decode_thingy_raw_motion(mock_data[RAW_DATA_CHAR_UUID])
            print("  Raw Motion Data:")
            print(f"    Accelerometer: ({raw_data.accel_x}, {raw_data.accel_y}, {raw_data.accel_z})")
            print(f"    Gyroscope: ({raw_data.gyro_x}, {raw_data.gyro_y}, {raw_data.gyro_z})")
            print(f"    Compass: ({raw_data.compass_x}, {raw_data.compass_y}, {raw_data.compass_z})")
            results["raw_motion"] = {
                "accel": (raw_data.accel_x, raw_data.accel_y, raw_data.accel_z),
                "gyro": (raw_data.gyro_x, raw_data.gyro_y, raw_data.gyro_z),
                "compass": (raw_data.compass_x, raw_data.compass_y, raw_data.compass_z),
            }
        except Exception as e:
            print(f"  Raw Motion Data: Error - {e}")

    if EULER_CHAR_UUID in mock_data:
        try:
            euler_data = decode_thingy_euler(mock_data[EULER_CHAR_UUID])
            # Convert fixed-point to degrees (divide by 65536)
            scale = 65536
            print("  Euler Angles:")
            print(f"    Roll: {euler_data.roll / scale:.2f}°")
            print(f"    Pitch: {euler_data.pitch / scale:.2f}°")
            print(f"    Yaw: {euler_data.yaw / scale:.2f}°")
            results["euler"] = {
                "roll": euler_data.roll / scale,
                "pitch": euler_data.pitch / scale,
                "yaw": euler_data.yaw / scale,
            }
        except Exception as e:
            print(f"  Euler Angles: Error - {e}")

    if ROTATION_MATRIX_CHAR_UUID in mock_data:
        try:
            rot_data = decode_thingy_rotation_matrix(mock_data[ROTATION_MATRIX_CHAR_UUID])
            # Convert fixed-point to float (divide by 32768)
            scale = 32768
            print("  Rotation Matrix:")
            print(f"    [{rot_data.m11 / scale:.3f}, {rot_data.m12 / scale:.3f}, {rot_data.m13 / scale:.3f}]")
            print(f"    [{rot_data.m21 / scale:.3f}, {rot_data.m22 / scale:.3f}, {rot_data.m23 / scale:.3f}]")
            print(f"    [{rot_data.m31 / scale:.3f}, {rot_data.m32 / scale:.3f}, {rot_data.m33 / scale:.3f}]")
            results["rotation_matrix"] = [
                [rot_data.m11 / scale, rot_data.m12 / scale, rot_data.m13 / scale],
                [rot_data.m21 / scale, rot_data.m22 / scale, rot_data.m23 / scale],
                [rot_data.m31 / scale, rot_data.m32 / scale, rot_data.m33 / scale],
            ]
        except Exception as e:
            print(f"  Rotation Matrix: Error - {e}")

    if HEADING_CHAR_UUID in mock_data:
        try:
            heading_data = decode_thingy_heading(mock_data[HEADING_CHAR_UUID])
            # Convert fixed-point to degrees (divide by 65536)
            heading_degrees = heading_data.heading / 65536
            print(f"  Compass Heading: {heading_degrees:.2f}°")
            results["heading"] = heading_degrees
        except Exception as e:
            print(f"  Compass Heading: Error - {e}")

    if GRAVITY_VECTOR_CHAR_UUID in mock_data:
        try:
            gravity_data = decode_thingy_gravity_vector(mock_data[GRAVITY_VECTOR_CHAR_UUID])
            print(f"  Gravity Vector: ({gravity_data.x:.2f}, {gravity_data.y:.2f}, {gravity_data.z:.2f}) m/s²")
            results["gravity"] = (gravity_data.x, gravity_data.y, gravity_data.z)
        except Exception as e:
            print(f"  Gravity Vector: Error - {e}")

    print("\n" + "=" * 70)
    print(f"✅ Successfully parsed {len(results)} sensor values")
    print("=" * 70 + "\n")

    return results


def main() -> int:
    """Main entry point for Thingy:52 demonstration.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="Nordic Thingy:52 sensor parsing demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with mock data (no device required)
  python thingy52_port.py --mock

  # Run with real device (requires BLE library)
  python thingy52_port.py --address AA:BB:CC:DD:EE:FF

This example demonstrates the architectural improvements of using
bluetooth-sig-python library over raw byte parsing:

1. Type Safety: msgspec.Struct-based data models with validation
2. Clean Separation: Decoding logic separated from data structures
3. No Hardcoded UUIDs: All UUIDs defined as constants, not scattered in code
4. Consistent API: SIG and vendor characteristics use same patterns
5. Comprehensive Error Handling: Clear error messages for invalid data

Note: Real device connection requires a BLE library (bleak, simplepyble, etc.)
and is not implemented in this demonstration script.
        """,
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock data instead of real device (default)",
    )
    parser.add_argument(
        "--address",
        type=str,
        help="BLE device address (requires BLE library, not yet implemented)",
    )

    args = parser.parse_args()

    if args.address:
        print("❌ Real device connection not yet implemented in this demo.")
        print("   Use --mock flag to see parsing demonstration with mock data.")
        return 1

    # Generate and parse mock data
    print("📝 Using mock Thingy:52 data for demonstration")
    mock_data = generate_mock_thingy_data()
    parse_and_display_thingy_data(mock_data)

    print("\n💡 Key Takeaways:")
    print("   • SIG characteristics use translator.parse_characteristic()")
    print("   • Vendor characteristics use dedicated decode_thingy_*() functions")
    print("   • Both return type-safe msgspec.Struct objects")
    print("   • No hardcoded UUID strings in parsing logic")
    print("   • Clean error handling with ValueError for invalid data")
    print("\n✨ This demonstrates the power of bluetooth-sig-python library!")

    return 0


if __name__ == "__main__":
    sys.exit(main())

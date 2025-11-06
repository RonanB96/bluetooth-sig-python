#!/usr/bin/env python3
"""Nordic Thingy:52 BluePy connection manager and example.

This module provides a BluePy-based connection manager for Nordic Thingy:52 devices,
demonstrating how to use bluetooth-sig-python library for parsing sensor data from
a real BLE device.

Usage:
    # Read all sensors once
    python thingy52_bluepy.py AA:BB:CC:DD:EE:FF

    # Read specific sensors with notifications
    python thingy52_bluepy.py AA:BB:CC:DD:EE:FF --temperature --humidity --battery

    # Continuous reading
    python thingy52_bluepy.py AA:BB:CC:DD:EE:FF --all --count 10 --interval 2.0

Requirements:
    pip install bluepy bluetooth-sig

References:
    - Nordic Thingy:52 Documentation:
      https://nordicsemiconductor.github.io/Nordic-Thingy52-FW/documentation
    - BluePy Library: https://github.com/IanHarvey/bluepy
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from bluepy.btle import ADDR_TYPE_RANDOM, UUID, DefaultDelegate, Peripheral  # type: ignore[import-not-found]
except ImportError:
    print("ERROR: bluepy library not installed. Install with: pip install bluepy")
    sys.exit(1)

from bluetooth_sig import BluetoothSIGTranslator  # noqa: E402
from examples.vendor_characteristics import (  # noqa: E402
    BUTTON_CHAR_UUID,
    COLOR_CHAR_UUID,
    ENVIRONMENT_SERVICE_UUID,
    EULER_CHAR_UUID,
    GAS_CHAR_UUID,
    GRAVITY_VECTOR_CHAR_UUID,
    HEADING_CHAR_UUID,
    HUMIDITY_CHAR_UUID,
    MOTION_SERVICE_UUID,
    ORIENTATION_CHAR_UUID,
    PRESSURE_CHAR_UUID,
    QUATERNION_CHAR_UUID,
    STEP_COUNTER_CHAR_UUID,
    TAP_CHAR_UUID,
    TEMPERATURE_CHAR_UUID,
    USER_INTERFACE_SERVICE_UUID,
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
    decode_thingy_step_counter,
    decode_thingy_tap,
    decode_thingy_temperature,
)

# CCCD UUID for enabling notifications
CCCD_UUID = UUID("00002902-0000-1000-8000-00805f9b34fb")


class Thingy52Delegate(DefaultDelegate):  # type: ignore[misc,no-any-unimported]
    """Notification delegate for Thingy:52 sensor data.

    Handles notifications from Thingy:52 sensors and parses them using
    bluetooth-sig-python library decoders.
    """

    def __init__(self) -> None:
        """Initialize the delegate."""
        DefaultDelegate.__init__(self)
        self.translator = BluetoothSIGTranslator()

    def handleNotification(self, handle: int, data: bytes) -> None:
        """Handle incoming notifications from Thingy:52 sensors.

        Args:
            handle: Characteristic handle
            data: Raw notification data
        """
        print(f"\n📨 Notification from handle {handle}:")
        print(f"   Raw data: {data.hex()}")
        # Note: In production, you'd map handle to characteristic UUID
        # and parse accordingly


class Thingy52:
    """Nordic Thingy:52 connection manager.

    Provides high-level interface for connecting to and reading from
    Nordic Thingy:52 BLE device using BluePy for connection and
    bluetooth-sig-python for parsing.

    Example:
        >>> thingy = Thingy52("AA:BB:CC:DD:EE:FF")
        >>> thingy.connect()
        >>> battery = thingy.read_battery()
        >>> temp = thingy.read_temperature()
        >>> thingy.disconnect()
    """

    def __init__(self, address: str) -> None:
        """Initialize Thingy:52 connection manager.

        Args:
            address: BLE MAC address of Thingy:52 device (format: AA:BB:CC:DD:EE:FF)
        """
        self.address = address
        self.periph: Peripheral | None = None  # type: ignore[no-any-unimported]
        self.translator = BluetoothSIGTranslator()
        self._services_discovered = False

        # Service UUIDs
        self.battery_service_uuid = UUID("0000180f-0000-1000-8000-00805f9b34fb")
        self.environment_service_uuid = UUID(ENVIRONMENT_SERVICE_UUID)
        self.ui_service_uuid = UUID(USER_INTERFACE_SERVICE_UUID)
        self.motion_service_uuid = UUID(MOTION_SERVICE_UUID)

    def connect(self) -> None:
        """Connect to Thingy:52 device.

        Raises:
            RuntimeError: If connection fails
        """
        try:
            print(f"Connecting to {self.address}...")
            self.periph = Peripheral(self.address, addrType=ADDR_TYPE_RANDOM)
            print("✅ Connected successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to {self.address}: {e}") from e

    def disconnect(self) -> None:
        """Disconnect from Thingy:52 device."""
        if self.periph:
            self.periph.disconnect()
            self.periph = None
            print("Disconnected from Thingy:52")

    def _ensure_connected(self) -> None:
        """Ensure device is connected.

        Raises:
            RuntimeError: If not connected
        """
        if not self.periph:
            raise RuntimeError("Not connected. Call connect() first.")

    def _read_characteristic(self, service_uuid: UUID, char_uuid: str) -> bytes:  # type: ignore[no-any-unimported]
        """Read a characteristic value.

        Args:
            service_uuid: Service UUID
            char_uuid: Characteristic UUID (full or short form)

        Returns:
            Raw characteristic bytes

        Raises:
            RuntimeError: If read fails
        """
        self._ensure_connected()
        try:
            # Get service
            service = self.periph.getServiceByUUID(service_uuid)  # type: ignore[union-attr]

            # Get characteristic
            char = service.getCharacteristics(UUID(char_uuid))[0]

            # Read value
            return char.read()  # type: ignore[no-any-return]
        except Exception as e:
            raise RuntimeError(f"Failed to read characteristic {char_uuid}: {e}") from e

    # Battery Service (SIG Standard)
    def read_battery(self) -> int:
        """Read battery level using SIG-standard characteristic.

        Returns:
            Battery level percentage (0-100)
        """
        data = self._read_characteristic(self.battery_service_uuid, "2A19")
        result = self.translator.parse_characteristic("2A19", data, None)
        return int(result.value)  # type: ignore

    # Environment Service (Nordic Vendor)
    def read_temperature(self) -> float:
        """Read temperature from Nordic vendor characteristic.

        Returns:
            Temperature in degrees Celsius
        """
        data = self._read_characteristic(self.environment_service_uuid, TEMPERATURE_CHAR_UUID)
        temp_data = decode_thingy_temperature(data)
        return temp_data.temperature_celsius + (temp_data.temperature_decimal / 100.0)

    def read_pressure(self) -> float:
        """Read pressure from Nordic vendor characteristic.

        Returns:
            Pressure in hPa (hectopascals)
        """
        data = self._read_characteristic(self.environment_service_uuid, PRESSURE_CHAR_UUID)
        pressure_data = decode_thingy_pressure(data)
        pressure_pa = pressure_data.pressure_integer + (pressure_data.pressure_decimal / 100.0)
        return pressure_pa / 100.0  # Convert Pa to hPa

    def read_humidity(self) -> int:
        """Read humidity from Nordic vendor characteristic.

        Returns:
            Relative humidity percentage (0-100)
        """
        data = self._read_characteristic(self.environment_service_uuid, HUMIDITY_CHAR_UUID)
        humidity_data = decode_thingy_humidity(data)
        return humidity_data.humidity_percent

    def read_gas(self) -> dict[str, int]:
        """Read air quality from Nordic vendor characteristic.

        Returns:
            Dictionary with 'eco2_ppm' and 'tvoc_ppb' keys
        """
        data = self._read_characteristic(self.environment_service_uuid, GAS_CHAR_UUID)
        gas_data = decode_thingy_gas(data)
        return {"eco2_ppm": gas_data.eco2_ppm, "tvoc_ppb": gas_data.tvoc_ppb}

    def read_color(self) -> dict[str, int]:
        """Read color sensor from Nordic vendor characteristic.

        Returns:
            Dictionary with 'red', 'green', 'blue', 'clear' keys
        """
        data = self._read_characteristic(self.environment_service_uuid, COLOR_CHAR_UUID)
        color_data = decode_thingy_color(data)
        return {
            "red": color_data.red,
            "green": color_data.green,
            "blue": color_data.blue,
            "clear": color_data.clear,
        }

    # User Interface Service
    def read_button(self) -> bool:
        """Read button state from Nordic vendor characteristic.

        Returns:
            True if button is pressed, False if released
        """
        data = self._read_characteristic(self.ui_service_uuid, BUTTON_CHAR_UUID)
        button_data = decode_thingy_button(data)
        return button_data.pressed

    # Motion Service
    def read_tap(self) -> dict[str, Any]:
        """Read tap detection from Nordic vendor characteristic.

        Returns:
            Dictionary with 'direction' and 'count' keys
        """
        data = self._read_characteristic(self.motion_service_uuid, TAP_CHAR_UUID)
        tap_data = decode_thingy_tap(data)
        directions = ["x+", "x-", "y+", "y-", "z+", "z-"]
        direction_name = directions[tap_data.direction] if tap_data.direction < 6 else "unknown"
        return {"direction": direction_name, "count": tap_data.count}

    def read_orientation(self) -> str:
        """Read device orientation from Nordic vendor characteristic.

        Returns:
            Orientation string: "Portrait", "Landscape", or "Reverse Portrait"
        """
        data = self._read_characteristic(self.motion_service_uuid, ORIENTATION_CHAR_UUID)
        orientation_data = decode_thingy_orientation(data)
        orientations = ["Portrait", "Landscape", "Reverse Portrait"]
        return orientations[orientation_data.orientation] if orientation_data.orientation < 3 else "Unknown"

    def read_quaternion(self) -> dict[str, float]:
        """Read quaternion from Nordic vendor characteristic.

        Returns:
            Dictionary with 'w', 'x', 'y', 'z' keys (normalized float values)
        """
        data = self._read_characteristic(self.motion_service_uuid, QUATERNION_CHAR_UUID)
        quat_data = decode_thingy_quaternion(data)
        scale = 2**30
        return {
            "w": quat_data.w / scale,
            "x": quat_data.x / scale,
            "y": quat_data.y / scale,
            "z": quat_data.z / scale,
        }

    def read_step_counter(self) -> dict[str, int]:
        """Read step counter from Nordic vendor characteristic.

        Returns:
            Dictionary with 'steps' and 'time_ms' keys
        """
        data = self._read_characteristic(self.motion_service_uuid, STEP_COUNTER_CHAR_UUID)
        step_data = decode_thingy_step_counter(data)
        return {"steps": step_data.steps, "time_ms": step_data.time_ms}

    def read_euler(self) -> dict[str, float]:
        """Read Euler angles from Nordic vendor characteristic.

        Returns:
            Dictionary with 'roll', 'pitch', 'yaw' keys (degrees)
        """
        data = self._read_characteristic(self.motion_service_uuid, EULER_CHAR_UUID)
        euler_data = decode_thingy_euler(data)
        scale = 65536
        return {
            "roll": euler_data.roll / scale,
            "pitch": euler_data.pitch / scale,
            "yaw": euler_data.yaw / scale,
        }

    def read_heading(self) -> float:
        """Read compass heading from Nordic vendor characteristic.

        Returns:
            Heading in degrees (0-360)
        """
        data = self._read_characteristic(self.motion_service_uuid, HEADING_CHAR_UUID)
        heading_data = decode_thingy_heading(data)
        return heading_data.heading / 65536

    def read_gravity(self) -> dict[str, float]:
        """Read gravity vector from Nordic vendor characteristic.

        Returns:
            Dictionary with 'x', 'y', 'z' keys (m/s²)
        """
        data = self._read_characteristic(self.motion_service_uuid, GRAVITY_VECTOR_CHAR_UUID)
        gravity_data = decode_thingy_gravity_vector(data)
        return {"x": gravity_data.x, "y": gravity_data.y, "z": gravity_data.z}

    def read_all_sensors(self) -> dict[str, Any]:
        """Read all available sensors.

        Returns:
            Dictionary with all sensor readings
        """
        results: dict[str, Any] = {}

        # Battery (SIG standard)
        try:
            results["battery"] = self.read_battery()
        except Exception as e:
            results["battery"] = f"Error: {e}"

        # Environment sensors
        try:
            results["temperature"] = self.read_temperature()
        except Exception as e:
            results["temperature"] = f"Error: {e}"

        try:
            results["pressure"] = self.read_pressure()
        except Exception as e:
            results["pressure"] = f"Error: {e}"

        try:
            results["humidity"] = self.read_humidity()
        except Exception as e:
            results["humidity"] = f"Error: {e}"

        try:
            results["gas"] = self.read_gas()
        except Exception as e:
            results["gas"] = f"Error: {e}"

        try:
            results["color"] = self.read_color()
        except Exception as e:
            results["color"] = f"Error: {e}"

        # Motion sensors
        try:
            results["orientation"] = self.read_orientation()
        except Exception as e:
            results["orientation"] = f"Error: {e}"

        try:
            results["heading"] = self.read_heading()
        except Exception as e:
            results["heading"] = f"Error: {e}"

        try:
            results["gravity"] = self.read_gravity()
        except Exception as e:
            results["gravity"] = f"Error: {e}"

        return results


def main() -> int:
    """Main entry point for Thingy:52 example.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Nordic Thingy:52 BLE sensor reader using BluePy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("address", help="BLE MAC address of Thingy:52 (format: AA:BB:CC:DD:EE:FF)")
    parser.add_argument("--battery", action="store_true", help="Read battery level")
    parser.add_argument("--temperature", action="store_true", help="Read temperature")
    parser.add_argument("--pressure", action="store_true", help="Read pressure")
    parser.add_argument("--humidity", action="store_true", help="Read humidity")
    parser.add_argument("--gas", action="store_true", help="Read gas sensor (eCO2, TVOC)")
    parser.add_argument("--color", action="store_true", help="Read color sensor")
    parser.add_argument("--orientation", action="store_true", help="Read orientation")
    parser.add_argument("--heading", action="store_true", help="Read compass heading")
    parser.add_argument("--gravity", action="store_true", help="Read gravity vector")
    parser.add_argument("--all", action="store_true", help="Read all sensors")
    parser.add_argument("--count", "-n", type=int, default=1, help="Number of times to read (default: 1, 0=continuous)")
    parser.add_argument(
        "--interval", "-t", type=float, default=2.0, help="Time between reads in seconds (default: 2.0)"
    )

    args = parser.parse_args()

    # If no specific sensors selected, read all
    if not any(
        [
            args.battery,
            args.temperature,
            args.pressure,
            args.humidity,
            args.gas,
            args.color,
            args.orientation,
            args.heading,
            args.gravity,
            args.all,
        ]
    ):
        args.all = True

    try:
        # Connect to device
        thingy = Thingy52(args.address)
        thingy.connect()

        # Read loop
        iteration = 0
        while args.count == 0 or iteration < args.count:
            print(f"\n{'=' * 70}")
            print(f"Reading #{iteration + 1} from Thingy:52")
            print("=" * 70)

            if args.all:
                results = thingy.read_all_sensors()
                for key, value in results.items():
                    print(f"{key:15s}: {value}")
            else:
                if args.battery:
                    print(f"Battery:      {thingy.read_battery()}%")
                if args.temperature:
                    print(f"Temperature:  {thingy.read_temperature():.2f}°C")
                if args.pressure:
                    print(f"Pressure:     {thingy.read_pressure():.2f} hPa")
                if args.humidity:
                    print(f"Humidity:     {thingy.read_humidity()}%")
                if args.gas:
                    gas = thingy.read_gas()
                    print(f"eCO2:         {gas['eco2_ppm']} ppm")
                    print(f"TVOC:         {gas['tvoc_ppb']} ppb")
                if args.color:
                    color = thingy.read_color()
                    print(f"Color (RGBC): R:{color['red']}, G:{color['green']}, B:{color['blue']}, C:{color['clear']}")
                if args.orientation:
                    print(f"Orientation:  {thingy.read_orientation()}")
                if args.heading:
                    print(f"Heading:      {thingy.read_heading():.2f}°")
                if args.gravity:
                    grav = thingy.read_gravity()
                    print(f"Gravity:      ({grav['x']:.2f}, {grav['y']:.2f}, {grav['z']:.2f}) m/s²")

            iteration += 1

            # Wait before next read (unless last iteration)
            if args.count == 0 or iteration < args.count:
                time.sleep(args.interval)

        # Disconnect
        thingy.disconnect()
        print("\n✅ Successfully completed")
        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        if thingy.periph:
            thingy.disconnect()
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

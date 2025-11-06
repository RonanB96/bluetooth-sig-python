#!/usr/bin/env python3
"""Nordic Thingy:52 example using bluetooth-sig-python library with real device.

This example demonstrates how to extend the bluetooth-sig-python library
for vendor-specific characteristics while maintaining the unified API.

Key Concepts Demonstrated:
1. Creating custom characteristic classes extending CustomBaseCharacteristic
2. Registering custom characteristics with CharacteristicRegistry
3. Using Device class for unified access to SIG and vendor characteristics
4. Implementing ConnectionManagerProtocol for BluePy integration

Requirements:
    pip install bluepy bluetooth-sig

Usage:
    # Read all sensors
    python thingy52_example.py AA:BB:CC:DD:EE:FF

    # Read specific sensors
    python thingy52_example.py AA:BB:CC:DD:EE:FF --temperature --humidity --battery

References:
    - Nordic Thingy:52 Documentation:
      https://nordicsemiconductor.github.io/Nordic-Thingy52-FW/documentation
    - BluePy Library: https://github.com/IanHarvey/bluepy
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any, Callable

# Add project root to path
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

try:
    from bluepy.btle import ADDR_TYPE_RANDOM, UUID, Peripheral  # type: ignore[import-not-found]
except ImportError:
    print("ERROR: bluepy library not installed. Install with: pip install bluepy")
    sys.exit(1)

from bluetooth_sig import BluetoothSIGTranslator  # noqa: E402
from bluetooth_sig.device import Device  # noqa: E402
from bluetooth_sig.device.connection import ConnectionManagerProtocol  # noqa: E402
from bluetooth_sig.types import CharacteristicRegistration  # noqa: E402
from bluetooth_sig.types.gatt_enums import ValueType  # noqa: E402
from bluetooth_sig.types.uuid import BluetoothUUID  # noqa: E402

# Import our custom characteristics
from examples.thingy52_characteristics import (  # noqa: E402
    NORDIC_UUID_BASE,
    ThingyButtonCharacteristic,
    ThingyColorCharacteristic,
    ThingyGasCharacteristic,
    ThingyHeadingCharacteristic,
    ThingyHumidityCharacteristic,
    ThingyOrientationCharacteristic,
    ThingyPressureCharacteristic,
    ThingyTemperatureCharacteristic,
)


class BluePyConnectionManager(ConnectionManagerProtocol):
    """BluePy connection manager for Nordic Thingy:52.

    Implements ConnectionManagerProtocol to integrate BluePy with
    the bluetooth-sig-python Device class.
    """

    def __init__(self, address: str) -> None:
        """Initialize connection manager.

        Args:
            address: BLE MAC address
        """
        self.address = address
        self.periph: Peripheral | None = None  # type: ignore[no-any-unimported]

    async def connect(self) -> None:
        """Connect to device."""
        print(f"Connecting to {self.address}...")
        self.periph = Peripheral(self.address, addrType=ADDR_TYPE_RANDOM)
        print("✅ Connected successfully")

    async def disconnect(self) -> None:
        """Disconnect from device."""
        if self.periph:
            self.periph.disconnect()
            self.periph = None
            print("Disconnected")

    async def read_characteristic(self, uuid: str) -> bytes:
        """Read characteristic value.

        Args:
            uuid: Characteristic UUID

        Returns:
            Raw characteristic bytes

        Raises:
            RuntimeError: If not connected or read fails
        """
        if not self.periph:
            raise RuntimeError("Not connected")

        try:
            # Find characteristic by UUID
            characteristics = self.periph.getCharacteristics(uuid=UUID(uuid))  # type: ignore[union-attr]
            if not characteristics:
                raise RuntimeError(f"Characteristic {uuid} not found")

            char = characteristics[0]
            return char.read()  # type: ignore[no-any-return]
        except Exception as e:
            raise RuntimeError(f"Failed to read characteristic {uuid}: {e}") from e

    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        """Read GATT characteristic (ConnectionManagerProtocol method).

        Args:
            char_uuid: Characteristic UUID

        Returns:
            Raw characteristic bytes
        """
        return await self.read_characteristic(str(char_uuid))

    async def write_characteristic(self, uuid: str, data: bytes) -> None:
        """Write characteristic value.

        Args:
            uuid: Characteristic UUID
            data: Data to write

        Raises:
            RuntimeError: If not connected or write fails
        """
        if not self.periph:
            raise RuntimeError("Not connected")

        try:
            characteristics = self.periph.getCharacteristics(uuid=UUID(uuid))  # type: ignore[union-attr]
            if not characteristics:
                raise RuntimeError(f"Characteristic {uuid} not found")

            char = characteristics[0]
            char.write(data)  # type: ignore[attr-defined]
        except Exception as e:
            raise RuntimeError(f"Failed to write characteristic {uuid}: {e}") from e

    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes) -> None:
        """Write GATT characteristic (ConnectionManagerProtocol method).

        Args:
            char_uuid: Characteristic UUID
            data: Data to write
        """
        await self.write_characteristic(str(char_uuid), data)

    async def get_services(self) -> Any:  # noqa: ANN401
        """Get services from device (ConnectionManagerProtocol method).

        Returns:
            Services structure from BluePy
        """
        if not self.periph:
            raise RuntimeError("Not connected")
        return self.periph.getServices()  # type: ignore[no-any-return,union-attr]

    async def start_notify(
        self, char_uuid: BluetoothUUID, callback: Callable[[str, bytes], None]
    ) -> None:
        """Start notifications (not implemented for this example).

        Args:
            char_uuid: Characteristic UUID
            callback: Notification callback
        """
        raise NotImplementedError("Notifications not implemented in this example")

    async def stop_notify(self, char_uuid: BluetoothUUID) -> None:
        """Stop notifications (not implemented for this example).

        Args:
            char_uuid: Characteristic UUID
        """
        raise NotImplementedError("Notifications not implemented in this example")

    @property
    def is_connected(self) -> bool:
        """Check if connected.

        Returns:
            True if connected
        """
        return self.periph is not None


def register_thingy52_characteristics(translator: BluetoothSIGTranslator) -> None:
    """Register all Nordic Thingy:52 custom characteristics.

    This function registers the vendor-specific characteristics with the
    bluetooth-sig-python library's registry system, enabling unified access
    through the Device class.

    Args:
        translator: BluetoothSIGTranslator instance
    """
    # Environment Service characteristics
    translator.register_custom_characteristic_class(
        NORDIC_UUID_BASE % 0x0201,
        ThingyTemperatureCharacteristic,
        metadata=CharacteristicRegistration(
            uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0201),
            name="Thingy Temperature",
            unit="°C",
            value_type=ValueType.FLOAT,
        ),
    )

    translator.register_custom_characteristic_class(
        NORDIC_UUID_BASE % 0x0202,
        ThingyPressureCharacteristic,
        metadata=CharacteristicRegistration(
            uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0202),
            name="Thingy Pressure",
            unit="hPa",
            value_type=ValueType.FLOAT,
        ),
    )

    translator.register_custom_characteristic_class(
        NORDIC_UUID_BASE % 0x0203,
        ThingyHumidityCharacteristic,
        metadata=CharacteristicRegistration(
            uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0203),
            name="Thingy Humidity",
            unit="%",
            value_type=ValueType.INT,
        ),
    )

    translator.register_custom_characteristic_class(
        NORDIC_UUID_BASE % 0x0204,
        ThingyGasCharacteristic,
        metadata=CharacteristicRegistration(
            uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0204),
            name="Thingy Gas",
            unit="ppm/ppb",
            value_type=ValueType.DICT,
        ),
    )

    translator.register_custom_characteristic_class(
        NORDIC_UUID_BASE % 0x0205,
        ThingyColorCharacteristic,
        metadata=CharacteristicRegistration(
            uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0205),
            name="Thingy Color",
            unit="",
            value_type=ValueType.DICT,
        ),
    )

    # User Interface Service characteristics
    translator.register_custom_characteristic_class(
        NORDIC_UUID_BASE % 0x0302,
        ThingyButtonCharacteristic,
        metadata=CharacteristicRegistration(
            uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0302),
            name="Thingy Button",
            unit="",
            value_type=ValueType.BOOL,
        ),
    )

    # Motion Service characteristics
    translator.register_custom_characteristic_class(
        NORDIC_UUID_BASE % 0x0403,
        ThingyOrientationCharacteristic,
        metadata=CharacteristicRegistration(
            uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0403),
            name="Thingy Orientation",
            unit="",
            value_type=ValueType.STRING,
        ),
    )

    translator.register_custom_characteristic_class(
        NORDIC_UUID_BASE % 0x0409,
        ThingyHeadingCharacteristic,
        metadata=CharacteristicRegistration(
            uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0409),
            name="Thingy Heading",
            unit="°",
            value_type=ValueType.FLOAT,
        ),
    )

    print("✅ Registered 8 Nordic Thingy:52 custom characteristics")


async def read_thingy52_sensors(
    device: Device,
    connection_manager: BluePyConnectionManager,
    sensor_uuids: dict[str, str],
) -> dict[str, Any]:
    """Read sensors from Thingy:52 using unified Device API.

    This demonstrates the key benefit: both SIG and vendor characteristics
    are read through the same Device interface.

    Args:
        device: Device instance
        connection_manager: Connection manager
        sensor_uuids: Dictionary mapping sensor names to UUIDs

    Returns:
        Dictionary of sensor readings
    """
    results: dict[str, Any] = {}

    for sensor_name, uuid in sensor_uuids.items():
        try:
            # Read raw data from device
            raw_data = await connection_manager.read_characteristic(uuid)

            # Parse using registered characteristic (SIG or vendor)
            parsed = device.translator.parse_characteristic(uuid, raw_data)

            results[sensor_name] = parsed.value
            print(f"  {sensor_name:20s}: {parsed.value}")

        except Exception as e:
            results[sensor_name] = f"Error: {e}"
            print(f"  {sensor_name:20s}: Error - {e}")

    return results


async def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Nordic Thingy:52 example using bluetooth-sig-python library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("address", help="BLE MAC address of Thingy:52 (format: AA:BB:CC:DD:EE:FF)")
    parser.add_argument("--battery", action="store_true", help="Read battery level (SIG)")
    parser.add_argument("--temperature", action="store_true", help="Read temperature (Nordic vendor)")
    parser.add_argument("--pressure", action="store_true", help="Read pressure (Nordic vendor)")
    parser.add_argument("--humidity", action="store_true", help="Read humidity (Nordic vendor)")
    parser.add_argument("--gas", action="store_true", help="Read gas sensor (Nordic vendor)")
    parser.add_argument("--color", action="store_true", help="Read color sensor (Nordic vendor)")
    parser.add_argument("--button", action="store_true", help="Read button state (Nordic vendor)")
    parser.add_argument("--orientation", action="store_true", help="Read orientation (Nordic vendor)")
    parser.add_argument("--heading", action="store_true", help="Read heading (Nordic vendor)")
    parser.add_argument("--all", action="store_true", help="Read all sensors")

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
            args.button,
            args.orientation,
            args.heading,
            args.all,
        ]
    ):
        args.all = True

    # Initialize translator and device
    translator = BluetoothSIGTranslator()
    device = Device(args.address, translator)

    # Register Nordic Thingy:52 custom characteristics
    register_thingy52_characteristics(translator)

    # Create connection manager
    connection_manager = BluePyConnectionManager(args.address)
    device.connection_manager = connection_manager

    try:
        # Connect to device
        await connection_manager.connect()

        # Build sensor list
        sensor_uuids: dict[str, str] = {}

        if args.all or args.battery:
            sensor_uuids["Battery Level (SIG)"] = "2A19"

        if args.all or args.temperature:
            sensor_uuids["Temperature"] = NORDIC_UUID_BASE % 0x0201

        if args.all or args.pressure:
            sensor_uuids["Pressure"] = NORDIC_UUID_BASE % 0x0202

        if args.all or args.humidity:
            sensor_uuids["Humidity"] = NORDIC_UUID_BASE % 0x0203

        if args.all or args.gas:
            sensor_uuids["Gas (eCO2/TVOC)"] = NORDIC_UUID_BASE % 0x0204

        if args.all or args.color:
            sensor_uuids["Color (RGBC)"] = NORDIC_UUID_BASE % 0x0205

        if args.all or args.button:
            sensor_uuids["Button"] = NORDIC_UUID_BASE % 0x0302

        if args.all or args.orientation:
            sensor_uuids["Orientation"] = NORDIC_UUID_BASE % 0x0403

        if args.all or args.heading:
            sensor_uuids["Heading"] = NORDIC_UUID_BASE % 0x0409

        # Read sensors
        print(f"\n{'=' * 70}")
        print("Nordic Thingy:52 Sensor Readings")
        print(f"{'=' * 70}\n")

        results = await read_thingy52_sensors(device, connection_manager, sensor_uuids)

        print(f"\n{'=' * 70}")
        print(f"✅ Successfully read {len([v for v in results.values() if not isinstance(v, str)])} sensors")
        print(f"{'=' * 70}\n")

        # Disconnect
        await connection_manager.disconnect()

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        await connection_manager.disconnect()
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if connection_manager.periph:
            await connection_manager.disconnect()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

"""Nordic Thingy:52 custom characteristic classes.

This module provides custom characteristic implementations for Nordic Thingy:52
vendor-specific characteristics. These extend the bluetooth-sig-python library's
BaseCharacteristic class and integrate with the characteristic registry.

All Nordic Thingy:52 vendor characteristics use the UUID base:
EF68XXXX-9B35-4933-9B10-52FFA9740042

References:
    - Nordic Thingy:52 Firmware Documentation:
      https://nordicsemiconductor.github.io/Nordic-Thingy52-FW/documentation
"""

from __future__ import annotations

import struct

from bluetooth_sig.gatt.characteristics.base import CustomBaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.gatt_enums import ValueType
from bluetooth_sig.types.uuid import BluetoothUUID

# Nordic UUID base
NORDIC_UUID_BASE = "EF68%04X-9B35-4933-9B10-52FFA9740042"


# ============================================================================
# Environment Service Characteristics
# ============================================================================


class ThingyTemperatureCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Temperature characteristic (EF680201).

    Temperature is encoded as signed 8-bit integer (whole degrees) followed
    by unsigned 8-bit fractional part (0.01°C resolution).
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0201),
        name="Thingy Temperature",
        unit="°C",
        value_type=ValueType.FLOAT,
        properties=[],
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        """Decode temperature from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (2 bytes: int8 + uint8)
            ctx: Optional context

        Returns:
            Temperature in degrees Celsius

        Raises:
            ValueError: If data length is invalid
        """
        if len(data) != 2:
            raise ValueError(f"Temperature data must be 2 bytes, got {len(data)}")

        temp_int = struct.unpack("<b", data[0:1])[0]  # signed int8
        temp_dec = data[1]  # unsigned int8

        if temp_dec > 99:
            raise ValueError(f"Temperature decimal must be 0-99, got {temp_dec}")

        return float(temp_int + (temp_dec / 100.0))

    def encode_value(self, data: float) -> bytearray:
        """Encode temperature to Nordic Thingy:52 format.

        Args:
            data: Temperature in degrees Celsius

        Returns:
            Encoded bytes (2 bytes)
        """
        temp_int = int(data)
        temp_dec = int((data - temp_int) * 100)
        return bytearray([temp_int & 0xFF, temp_dec & 0xFF])


class ThingyPressureCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Pressure characteristic (EF680202).

    Pressure is encoded as unsigned 32-bit little-endian integer (Pascals)
    followed by unsigned 8-bit decimal part (0.01 Pa resolution).
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0202),
        name="Thingy Pressure",
        unit="hPa",
        value_type=ValueType.FLOAT,
        properties=[],
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        """Decode pressure from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (5 bytes: uint32 + uint8)
            ctx: Optional context

        Returns:
            Pressure in hectopascals (hPa)

        Raises:
            ValueError: If data length is invalid
        """
        if len(data) != 5:
            raise ValueError(f"Pressure data must be 5 bytes, got {len(data)}")

        pressure_int = struct.unpack("<I", data[0:4])[0]  # uint32 little-endian
        pressure_dec = data[4]  # uint8

        if pressure_dec > 99:
            raise ValueError(f"Pressure decimal must be 0-99, got {pressure_dec}")

        # Convert Pa to hPa
        pressure_pa = pressure_int + (pressure_dec / 100.0)
        return float(pressure_pa / 100.0)

    def encode_value(self, data: float) -> bytearray:
        """Encode pressure to Nordic Thingy:52 format.

        Args:
            data: Pressure in hectopascals (hPa)

        Returns:
            Encoded bytes (5 bytes)
        """
        pressure_pa = data * 100.0  # Convert hPa to Pa
        pressure_int = int(pressure_pa)
        pressure_dec = int((pressure_pa - pressure_int) * 100)
        return bytearray(struct.pack("<I", pressure_int)) + bytearray([pressure_dec & 0xFF])


class ThingyHumidityCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Humidity characteristic (EF680203).

    Humidity is encoded as unsigned 8-bit integer (0-100%).
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0203),
        name="Thingy Humidity",
        unit="%",
        value_type=ValueType.INT,
        properties=[],
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
        """Decode humidity from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (1 byte)
            ctx: Optional context

        Returns:
            Relative humidity percentage (0-100)

        Raises:
            ValueError: If data length is invalid or value out of range
        """
        if len(data) != 1:
            raise ValueError(f"Humidity data must be 1 byte, got {len(data)}")

        humidity = data[0]

        if humidity > 100:
            raise ValueError(f"Humidity must be 0-100%, got {humidity}")

        return humidity

    def encode_value(self, data: int) -> bytearray:
        """Encode humidity to Nordic Thingy:52 format.

        Args:
            data: Humidity percentage (0-100)

        Returns:
            Encoded bytes (1 byte)
        """
        if not 0 <= data <= 100:
            raise ValueError(f"Humidity must be 0-100%, got {data}")
        return bytearray([data & 0xFF])


class ThingyGasCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Gas sensor characteristic (EF680204).

    Gas data contains eCO2 (ppm) and TVOC (ppb) as two uint16 values.
    Returns dict with 'eco2_ppm' and 'tvoc_ppb' keys.
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0204),
        name="Thingy Gas",
        unit="ppm/ppb",
        value_type=ValueType.DICT,
        properties=[],
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> dict[str, int]:
        """Decode gas sensor data from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (4 bytes: 2x uint16)
            ctx: Optional context

        Returns:
            Dictionary with 'eco2_ppm' and 'tvoc_ppb' keys

        Raises:
            ValueError: If data length is invalid
        """
        if len(data) != 4:
            raise ValueError(f"Gas data must be 4 bytes, got {len(data)}")

        eco2 = struct.unpack("<H", data[0:2])[0]  # uint16 little-endian
        tvoc = struct.unpack("<H", data[2:4])[0]  # uint16 little-endian

        return {"eco2_ppm": eco2, "tvoc_ppb": tvoc}

    def encode_value(self, data: dict[str, int]) -> bytearray:
        """Encode gas sensor data to Nordic Thingy:52 format.

        Args:
            data: Dictionary with 'eco2_ppm' and 'tvoc_ppb' keys

        Returns:
            Encoded bytes (4 bytes)
        """
        eco2 = data.get("eco2_ppm", 0)
        tvoc = data.get("tvoc_ppb", 0)
        return bytearray(struct.pack("<HH", eco2, tvoc))


class ThingyColorCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Color sensor characteristic (EF680205).

    Color data contains Red, Green, Blue, Clear as four uint16 values.
    Returns dict with 'red', 'green', 'blue', 'clear' keys.
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0205),
        name="Thingy Color",
        unit="",
        value_type=ValueType.DICT,
        properties=[],
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> dict[str, int]:
        """Decode color sensor data from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (8 bytes: 4x uint16)
            ctx: Optional context

        Returns:
            Dictionary with 'red', 'green', 'blue', 'clear' keys

        Raises:
            ValueError: If data length is invalid
        """
        if len(data) != 8:
            raise ValueError(f"Color data must be 8 bytes, got {len(data)}")

        red = struct.unpack("<H", data[0:2])[0]
        green = struct.unpack("<H", data[2:4])[0]
        blue = struct.unpack("<H", data[4:6])[0]
        clear = struct.unpack("<H", data[6:8])[0]

        return {"red": red, "green": green, "blue": blue, "clear": clear}

    def encode_value(self, data: dict[str, int]) -> bytearray:
        """Encode color sensor data to Nordic Thingy:52 format.

        Args:
            data: Dictionary with 'red', 'green', 'blue', 'clear' keys

        Returns:
            Encoded bytes (8 bytes)
        """
        red = data.get("red", 0)
        green = data.get("green", 0)
        blue = data.get("blue", 0)
        clear = data.get("clear", 0)
        return bytearray(struct.pack("<HHHH", red, green, blue, clear))


# ============================================================================
# User Interface Service Characteristics
# ============================================================================


class ThingyButtonCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Button characteristic (EF680302).

    Button state is encoded as unsigned 8-bit integer (0=released, 1=pressed).
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0302),
        name="Thingy Button",
        unit="",
        value_type=ValueType.BOOL,
        properties=[],
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> bool:
        """Decode button state from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (1 byte)
            ctx: Optional context

        Returns:
            True if button is pressed, False if released

        Raises:
            ValueError: If data length is invalid or value is invalid
        """
        if len(data) != 1:
            raise ValueError(f"Button data must be 1 byte, got {len(data)}")

        state = data[0]

        if state > 1:
            raise ValueError(f"Button state must be 0 or 1, got {state}")

        return bool(state)

    def encode_value(self, data: bool) -> bytearray:
        """Encode button state to Nordic Thingy:52 format.

        Args:
            data: True for pressed, False for released

        Returns:
            Encoded bytes (1 byte)
        """
        return bytearray([1 if data else 0])


# ============================================================================
# Motion Service Characteristics
# ============================================================================


class ThingyOrientationCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Orientation characteristic (EF680403).

    Orientation is encoded as unsigned 8-bit integer:
    - 0: Portrait
    - 1: Landscape
    - 2: Reverse portrait
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0403),
        name="Thingy Orientation",
        unit="",
        value_type=ValueType.STRING,
        properties=[],
    )

    ORIENTATIONS = ["Portrait", "Landscape", "Reverse Portrait"]

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> str:
        """Decode orientation from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (1 byte)
            ctx: Optional context

        Returns:
            Orientation string

        Raises:
            ValueError: If data length is invalid or value invalid
        """
        if len(data) != 1:
            raise ValueError(f"Orientation data must be 1 byte, got {len(data)}")

        orientation = data[0]

        if orientation > 2:
            raise ValueError(f"Orientation must be 0-2, got {orientation}")

        return self.ORIENTATIONS[orientation]

    def encode_value(self, data: str) -> bytearray:
        """Encode orientation to Nordic Thingy:52 format.

        Args:
            data: Orientation string

        Returns:
            Encoded bytes (1 byte)
        """
        try:
            index = self.ORIENTATIONS.index(data)
            return bytearray([index])
        except ValueError as e:
            raise ValueError(f"Invalid orientation: {data}") from e


class ThingyHeadingCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Heading characteristic (EF680409).

    Heading is encoded as signed 32-bit integer in fixed-point format
    (divide by 65536 to get degrees).
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0409),
        name="Thingy Heading",
        unit="°",
        value_type=ValueType.FLOAT,
        properties=[],
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        """Decode heading from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (4 bytes: int32)
            ctx: Optional context

        Returns:
            Heading in degrees (0-360)

        Raises:
            ValueError: If data length is invalid
        """
        if len(data) != 4:
            raise ValueError(f"Heading data must be 4 bytes, got {len(data)}")

        heading_raw = struct.unpack("<i", data[0:4])[0]
        return float(heading_raw / 65536.0)

    def encode_value(self, data: float) -> bytearray:
        """Encode heading to Nordic Thingy:52 format.

        Args:
            data: Heading in degrees

        Returns:
            Encoded bytes (4 bytes)
        """
        heading_raw = int(data * 65536)
        return bytearray(struct.pack("<i", heading_raw))

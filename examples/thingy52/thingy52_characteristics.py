"""Nordic Thingy:52 vendor characteristic implementations.

This module provides custom characteristic classes for Nordic Thingy:52
environmental sensors, UI elements, and motion sensors. These use vendor-specific
UUIDs and data formats that differ from Bluetooth SIG standards.
"""

from __future__ import annotations

import msgspec

from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.characteristics.utils.data_parser import DataParser
from bluetooth_sig.gatt.exceptions import InsufficientDataError, ValueRangeError
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.context import CharacteristicContext
from bluetooth_sig.types.gatt_enums import ValueType
from bluetooth_sig.types.uuid import BluetoothUUID

# Nordic Thingy:52 UUID base
NORDIC_UUID_BASE = "EF680000-9B35-4933-9B10-52FFA9740042"


# Data structures for characteristic values
class ThingyTemperatureData(msgspec.Struct, frozen=True, kw_only=True):
    """Temperature sensor data from Nordic Thingy:52.

    Attributes:
        temperature_celsius: Temperature in degrees Celsius (integer.decimal format)
    """

    temperature_celsius: float


class ThingyPressureData(msgspec.Struct, frozen=True, kw_only=True):
    """Pressure sensor data from Nordic Thingy:52.

    Attributes:
        pressure_hpa: Pressure in hectopascals (integer.decimal format)
    """

    pressure_hpa: float


class ThingyHumidityData(msgspec.Struct, frozen=True, kw_only=True):
    """Humidity sensor data from Nordic Thingy:52.

    Attributes:
        humidity_percent: Humidity percentage (0-100)
    """

    humidity_percent: int


class ThingyGasData(msgspec.Struct, frozen=True, kw_only=True):
    """Gas sensor data from Nordic Thingy:52.

    Attributes:
        eco2_ppm: Equivalent CO2 concentration in ppm
        tvoc_ppb: Total Volatile Organic Compounds in ppb
    """

    eco2_ppm: int
    tvoc_ppb: int


class ThingyColorData(msgspec.Struct, frozen=True, kw_only=True):
    """Color sensor data from Nordic Thingy:52.

    Attributes:
        red: Red channel value (0-255)
        green: Green channel value (0-255)
        blue: Blue channel value (0-255)
        clear: Clear channel value (0-255)
    """

    red: int
    green: int
    blue: int
    clear: int


class ThingyButtonData(msgspec.Struct, frozen=True, kw_only=True):
    """Button state data from Nordic Thingy:52.

    Attributes:
        pressed: True if button is pressed, False if released
    """

    pressed: bool


class ThingyOrientationData(msgspec.Struct, frozen=True, kw_only=True):
    """Orientation sensor data from Nordic Thingy:52.

    Attributes:
        orientation: Orientation value (0-2, meaning depends on device)
    """

    orientation: int


class ThingyHeadingData(msgspec.Struct, frozen=True, kw_only=True):
    """Heading sensor data from Nordic Thingy:52.

    Attributes:
        heading_degrees: Compass heading in degrees (0-360)
    """

    heading_degrees: float


# Characteristic implementations
class ThingyTemperatureCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Temperature characteristic."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE.replace("0000", "0201")),
        name="Thingy Temperature",
        value_type=ValueType.DICT,
        unit="°C",
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ThingyTemperatureData:
        """Decode temperature data.

        Format: 2 bytes - signed int8 (integer part) + uint8 (decimal part / 256)

        Args:
            data: Raw characteristic data
            ctx: Optional context providing surrounding characteristic metadata when available.

        Returns:
            Parsed temperature data

        Raises:
            InsufficientDataError: If data length is invalid
        """
        if len(data) != 2:
            raise InsufficientDataError("Thingy Temperature", data, 2)

        # Signed int8 for integer part
        integer_part = DataParser.parse_int8(data, offset=0, signed=True)
        # Uint8 for decimal part (0-255, divide by 256 for 0.0-0.996)
        decimal_part = data[1] / 256.0

        temperature = integer_part + decimal_part

        return ThingyTemperatureData(temperature_celsius=temperature)


class ThingyPressureCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Pressure characteristic."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE.replace("0000", "0202")),
        name="Thingy Pressure",
        value_type=ValueType.DICT,
        unit="hPa",
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ThingyPressureData:
        """Decode pressure data.

        Format: 5 bytes - int32 LE (integer part) + uint8 (decimal part / 256)

        Args:
            data: Raw characteristic data
            ctx: Optional context providing surrounding characteristic metadata when available.

        Returns:
            Parsed pressure data

        Raises:
            InsufficientDataError: If data length is invalid
        """
        if len(data) != 5:
            raise InsufficientDataError("Thingy Pressure", data, 5)

        # Signed int32 for integer part
        integer_part = DataParser.parse_int32(data, offset=0, signed=True)
        # Uint8 for decimal part
        decimal_part = data[4] / 256.0

        pressure = integer_part + decimal_part

        return ThingyPressureData(pressure_hpa=pressure)


class ThingyHumidityCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Humidity characteristic."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE.replace("0000", "0203")),
        name="Thingy Humidity",
        value_type=ValueType.DICT,
        unit="%",
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ThingyHumidityData:
        """Decode humidity data.

        Format: 1 byte - signed int8 percentage

        Args:
            data: Raw characteristic data
            ctx: Optional context providing surrounding characteristic metadata when available.

        Returns:
            Parsed humidity data

        Raises:
            InsufficientDataError: If data length is invalid
            ValueRangeError: If humidity value is out of range
        """
        if len(data) != 1:
            raise InsufficientDataError("Thingy Humidity", data, 1)

        humidity = DataParser.parse_int8(data, offset=0, signed=True)

        if not 0 <= humidity <= 100:
            raise ValueRangeError("humidity", humidity, 0, 100)

        return ThingyHumidityData(humidity_percent=humidity)


class ThingyGasCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Gas characteristic."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE.replace("0000", "0204")),
        name="Thingy Gas",
        value_type=ValueType.DICT,
        unit="ppm/ppb",
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ThingyGasData:
        """Decode gas sensor data.

        Format: 4 bytes - 2x uint16 LE (eCO2 ppm, TVOC ppb)

        Args:
            data: Raw characteristic data
            ctx: Optional context providing surrounding characteristic metadata when available.

        Returns:
            Parsed gas data

        Raises:
            InsufficientDataError: If data length is invalid
        """
        if len(data) != 4:
            raise InsufficientDataError("Thingy Gas", data, 4)

        eco2 = DataParser.parse_int16(data, offset=0, signed=False)
        tvoc = DataParser.parse_int16(data, offset=2, signed=False)

        return ThingyGasData(eco2_ppm=eco2, tvoc_ppb=tvoc)


class ThingyColorCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Color characteristic."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE.replace("0000", "0205")),
        name="Thingy Color",
        value_type=ValueType.DICT,
        unit="",
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ThingyColorData:
        """Decode color sensor data.

        Format: 8 bytes - 4x uint16 LE (red, green, blue, clear)

        Args:
            data: Raw characteristic data
            ctx: Optional context providing surrounding characteristic metadata when available.

        Returns:
            Parsed color data

        Raises:
            InsufficientDataError: If data length is invalid
        """
        if len(data) != 8:
            raise InsufficientDataError("Thingy Color", data, 8)

        red = DataParser.parse_int16(data, offset=0, signed=False)
        green = DataParser.parse_int16(data, offset=2, signed=False)
        blue = DataParser.parse_int16(data, offset=4, signed=False)
        clear = DataParser.parse_int16(data, offset=6, signed=False)

        return ThingyColorData(red=red, green=green, blue=blue, clear=clear)


class ThingyButtonCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Button characteristic."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE.replace("0000", "0302")),
        name="Thingy Button",
        value_type=ValueType.DICT,
        unit="",
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ThingyButtonData:
        """Decode button state data.

        Format: 1 byte - uint8 (1 = released, 0 = pressed)

        Args:
            data: Raw characteristic data
            ctx: Optional context providing surrounding characteristic metadata when available.

        Returns:
            Parsed button data

        Raises:
            InsufficientDataError: If data length is invalid
            ValueRangeError: If button state is invalid
        """
        if len(data) != 1:
            raise InsufficientDataError("Thingy Button", data, 1)

        state = DataParser.parse_int8(data, offset=0, signed=False)
        if state not in (0, 1):
            raise ValueRangeError("button_state", state, 0, 1)

        pressed = state == 0  # 0 = pressed, 1 = released

        return ThingyButtonData(pressed=pressed)


class ThingyOrientationCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Orientation characteristic."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE.replace("0000", "0403")),
        name="Thingy Orientation",
        value_type=ValueType.DICT,
        unit="",
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ThingyOrientationData:
        """Decode orientation data.

        Format: 1 byte - uint8 orientation value

        Args:
            data: Raw characteristic data
            ctx: Optional context providing surrounding characteristic metadata when available.

        Returns:
            Parsed orientation data

        Raises:
            InsufficientDataError: If data length is invalid
            ValueRangeError: If orientation value is out of range
        """
        if len(data) != 1:
            raise InsufficientDataError("Thingy Orientation", data, 1)

        orientation = DataParser.parse_int8(data, offset=0, signed=False)
        if not 0 <= orientation <= 2:
            raise ValueRangeError("orientation", orientation, 0, 2)

        return ThingyOrientationData(orientation=orientation)


class ThingyHeadingCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Heading characteristic."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE.replace("0000", "0409")),
        name="Thingy Heading",
        value_type=ValueType.DICT,
        unit="°",
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ThingyHeadingData:
        """Decode heading data.

        Format: 4 bytes - float32 LE compass heading in degrees

        Args:
            data: Raw characteristic data
            ctx: Optional context providing surrounding characteristic metadata when available.

        Returns:
            Parsed heading data

        Raises:
            InsufficientDataError: If data length is invalid
        """
        if len(data) != 4:
            raise InsufficientDataError("Thingy Heading", data, 4)

        # Convert 4 bytes to float32 (little-endian)
        heading = DataParser.parse_float32(data, offset=0)

        return ThingyHeadingData(heading_degrees=heading)

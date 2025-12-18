"""Nordic Thingy:52 custom characteristic classes.

This module provides custom characteristic implementations for Nordic Thingy:52
vendor-specific characteristics. These extend the bluetooth-sig-python library's
CustomBaseCharacteristic class and integrate with the characteristic registry.

All Nordic Thingy:52 vendor characteristics use the UUID base:
EF68XXXX-9B35-4933-9B10-52FFA9740042

References:
    - Nordic Thingy:52 Firmware Documentation:
      https://nordicsemiconductor.github.io/Nordic-Thingy52-FW/documentation
"""

from __future__ import annotations

import msgspec

from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.characteristics.templates import Sint8Template, Uint8Template, Uint16Template, Uint32Template
from bluetooth_sig.gatt.characteristics.utils import DataParser
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.gatt.exceptions import InsufficientDataError, ValueRangeError
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.gatt_enums import ValueType
from bluetooth_sig.types.uuid import BluetoothUUID

# Nordic UUID base for Thingy:52 vendor-specific characteristics.
# Format: EF68XXXX-9B35-4933-9B10-52FFA9740042 where XXXX is the characteristic ID.
# This is the standard Nordic Semiconductor UUID base with vendor-assigned identifiers.
NORDIC_UUID_BASE = "EF68%04X-9B35-4933-9B10-52FFA9740042"


# ============================================================================
# Data Structures (msgspec.Struct for structured returns)
# ============================================================================


class ThingyGasData(msgspec.Struct, frozen=True, kw_only=True):
    """Gas sensor data from Nordic Thingy:52.

    Attributes:
        eco2_ppm: eCO2 concentration in parts per million
        tvoc_ppb: TVOC concentration in parts per billion
    """

    eco2_ppm: int
    tvoc_ppb: int


class ThingyColorData(msgspec.Struct, frozen=True, kw_only=True):
    """Color sensor data from Nordic Thingy:52.

    Attributes:
        red: Red channel value (0-65535)
        green: Green channel value (0-65535)
        blue: Blue channel value (0-65535)
        clear: Clear channel value (0-65535)
    """

    red: int
    green: int
    blue: int
    clear: int


# ============================================================================
# Environment Service Characteristics
# ============================================================================


class ThingyTemperatureCharacteristic(CustomBaseCharacteristic):
    r"""Nordic Thingy:52 Temperature characteristic (EF680201).

    Temperature is encoded as signed 8-bit integer (whole degrees) followed
    by unsigned 8-bit fractional part (0.01°C resolution).

    Examples:
        >>> char = ThingyTemperatureCharacteristic()
        >>> data = bytearray([0x18, 0x32])  # 24.50°C
        >>> char.decode_value(data)
        24.5
        >>> char.encode_value(24.5)
        bytearray(b'\x182')
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0201),
        name="Thingy Temperature",
        unit="°C",
        value_type=ValueType.FLOAT,
    )

    _int_template: Sint8Template = Sint8Template()
    _dec_template: Uint8Template = Uint8Template()

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        """Decode temperature from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (2 bytes: int8 + uint8)
            ctx: Optional context

        Returns:
            Temperature in degrees Celsius

        Raises:
            InsufficientDataError: If data length is not exactly 2 bytes
            ValueRangeError: If decimal value is not in range 0-99
        """
        if len(data) != 2:
            raise InsufficientDataError("Thingy Temperature", data, 2)

        temp_int = self._int_template.decode_value(data, offset=0)
        temp_dec = self._dec_template.decode_value(data, offset=1)

        if temp_dec > 99:
            raise ValueRangeError("temperature_decimal", temp_dec, 0, 99)

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
        return self._int_template.encode_value(temp_int) + self._dec_template.encode_value(temp_dec)


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
    )

    _int_template: Uint32Template = Uint32Template()
    _dec_template: Uint8Template = Uint8Template()

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        """Decode pressure from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (5 bytes: uint32 + uint8)
            ctx: Optional context

        Returns:
            Pressure in hectopascals (hPa)

        Raises:
            InsufficientDataError: If data length is not exactly 5 bytes
            ValueRangeError: If decimal value is not in range 0-99
        """
        if len(data) != 5:
            raise InsufficientDataError("Thingy Pressure", data, 5)

        pressure_int = self._int_template.decode_value(data, offset=0)
        pressure_dec = self._dec_template.decode_value(data, offset=4)

        if pressure_dec > 99:
            raise ValueRangeError("pressure_decimal", pressure_dec, 0, 99)

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
        return self._int_template.encode_value(pressure_int) + self._dec_template.encode_value(pressure_dec)


class ThingyHumidityCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Humidity characteristic (EF680203).

    Humidity is encoded as unsigned 8-bit integer (0-100%).

    Examples:
        >>> char = ThingyHumidityCharacteristic()
        >>> data = bytearray([65])  # 65%
        >>> char.decode_value(data)
        65
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0203),
        name="Thingy Humidity",
        unit="%",
        value_type=ValueType.INT,
    )

    _template = Uint8Template()

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
        """Decode humidity from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (1 byte)
            ctx: Optional context

        Returns:
            Relative humidity percentage (0-100)

        Raises:
            InsufficientDataError: If data length is not exactly 1 byte
            ValueRangeError: If humidity value is not in range 0-100
        """
        if len(data) != 1:
            raise InsufficientDataError("Thingy Humidity", data, 1)

        humidity = self._template.decode_value(data)

        if humidity > 100:
            raise ValueRangeError("humidity", humidity, 0, 100)

        return humidity

    def encode_value(self, data: int) -> bytearray:
        """Encode humidity to Nordic Thingy:52 format.

        Args:
            data: Humidity percentage (0-100)

        Returns:
            Encoded bytes (1 byte)
        """
        if not 0 <= data <= 100:
            raise ValueRangeError("humidity", data, 0, 100)
        return self._template.encode_value(data)


class ThingyGasCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Gas sensor characteristic (EF680204).

    Gas data contains eCO2 (ppm) and TVOC (ppb) as two uint16 values.
    Returns ThingyGasData msgspec.Struct.

    Examples:
        >>> char = ThingyGasCharacteristic()
        >>> data = bytearray([0xD0, 0x07, 0x2C, 0x01])  # 2000 ppm eCO2, 300 ppb TVOC
        >>> result = char.decode_value(data)
        >>> result.eco2_ppm
        2000
        >>> result.tvoc_ppb
        300
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0204),
        name="Thingy Gas",
        unit="ppm/ppb",
        value_type=ValueType.DICT,
    )

    _template = Uint16Template()

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ThingyGasData:
        """Decode gas sensor data from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (4 bytes: 2x uint16)
            ctx: Optional context

        Returns:
            ThingyGasData with eco2_ppm and tvoc_ppb fields

        Raises:
            InsufficientDataError: If data length is not exactly 4 bytes
        """
        if len(data) != 4:
            raise InsufficientDataError("Thingy Gas", data, 4)

        eco2 = self._template.decode_value(data, offset=0)
        tvoc = self._template.decode_value(data, offset=2)

        return ThingyGasData(eco2_ppm=eco2, tvoc_ppb=tvoc)

    def encode_value(self, data: ThingyGasData) -> bytearray:
        """Encode gas sensor data to Nordic Thingy:52 format.

        Args:
            data: ThingyGasData with eco2_ppm and tvoc_ppb fields

        Returns:
            Encoded bytes (4 bytes)
        """
        return self._template.encode_value(data.eco2_ppm) + self._template.encode_value(data.tvoc_ppb)


class ThingyColorCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Color sensor characteristic (EF680205).

    Color data contains Red, Green, Blue, Clear as four uint16 values.
    Returns ThingyColorData msgspec.Struct.

    Examples:
        >>> char = ThingyColorCharacteristic()
        >>> # Red=1000, Green=2000, Blue=3000, Clear=4000
        >>> data = bytearray([0xE8, 0x03, 0xD0, 0x07, 0xB8, 0x0B, 0xA0, 0x0F])
        >>> result = char.decode_value(data)
        >>> result.red
        1000
        >>> result.green
        2000
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0205),
        name="Thingy Color",
        unit="",
        value_type=ValueType.DICT,
    )

    _template = Uint16Template()

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ThingyColorData:
        """Decode color sensor data from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (8 bytes: 4x uint16)
            ctx: Optional context

        Returns:
            ThingyColorData with red, green, blue, clear fields

        Raises:
            InsufficientDataError: If data length is not exactly 8 bytes
        """
        if len(data) != 8:
            raise InsufficientDataError("Thingy Color", data, 8)

        red = self._template.decode_value(data, offset=0)
        green = self._template.decode_value(data, offset=2)
        blue = self._template.decode_value(data, offset=4)
        clear = self._template.decode_value(data, offset=6)

        return ThingyColorData(red=red, green=green, blue=blue, clear=clear)

    def encode_value(self, data: ThingyColorData) -> bytearray:
        """Encode color sensor data to Nordic Thingy:52 format.

        Args:
            data: ThingyColorData with red, green, blue, clear fields

        Returns:
            Encoded bytes (8 bytes)
        """
        result = bytearray()
        result.extend(self._template.encode_value(data.red))
        result.extend(self._template.encode_value(data.green))
        result.extend(self._template.encode_value(data.blue))
        result.extend(self._template.encode_value(data.clear))
        return result


# ============================================================================
# User Interface Service Characteristics
# ============================================================================


class ThingyButtonCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Button characteristic (EF680302).

    Button state is encoded as unsigned 8-bit integer (0=released, 1=pressed).

    Examples:
        >>> char = ThingyButtonCharacteristic()
        >>> data = bytearray([1])  # Pressed
        >>> char.decode_value(data)
        True
        >>> data = bytearray([0])  # Released
        >>> char.decode_value(data)
        False
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0302),
        name="Thingy Button",
        unit="",
        value_type=ValueType.BOOL,
    )

    _template = Uint8Template()

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> bool:
        """Decode button state from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (1 byte)
            ctx: Optional context

        Returns:
            True if button is pressed, False if released

        Raises:
            InsufficientDataError: If data length is not exactly 1 byte
            ValueRangeError: If button state is not 0 or 1
        """
        if len(data) != 1:
            raise InsufficientDataError("Thingy Button", data, 1)

        state = self._template.decode_value(data)

        if state > 1:
            raise ValueRangeError("button_state", state, 0, 1)

        return bool(state)

    def encode_value(self, data: bool) -> bytearray:
        """Encode button state to Nordic Thingy:52 format.

        Args:
            data: True for pressed, False for released

        Returns:
            Encoded bytes (1 byte)
        """
        return self._template.encode_value(1 if data else 0)


# ============================================================================
# Motion Service Characteristics
# ============================================================================


class ThingyOrientationCharacteristic(CustomBaseCharacteristic):
    """Nordic Thingy:52 Orientation characteristic (EF680403).

    Orientation is encoded as unsigned 8-bit integer:
    - 0: Portrait
    - 1: Landscape
    - 2: Reverse portrait

    Examples:
        >>> char = ThingyOrientationCharacteristic()
        >>> data = bytearray([1])  # Landscape
        >>> char.decode_value(data)
        'Landscape'
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0x0403),
        name="Thingy Orientation",
        unit="",
        value_type=ValueType.STRING,
    )

    ORIENTATIONS: list[str] = ["Portrait", "Landscape", "Reverse Portrait"]

    _template = Uint8Template()

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> str:
        """Decode orientation from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (1 byte)
            ctx: Optional context

        Returns:
            Orientation string

        Raises:
            InsufficientDataError: If data length is not exactly 1 byte
            ValueRangeError: If orientation value is not in range 0-2
        """
        if len(data) != 1:
            raise InsufficientDataError("Thingy Orientation", data, 1)

        orientation = self._template.decode_value(data)

        if orientation > 2:
            raise ValueRangeError("orientation", orientation, 0, 2)

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
            return self._template.encode_value(index)
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
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        """Decode heading from Nordic Thingy:52 format.

        Args:
            data: Raw bytes (4 bytes: int32)
            ctx: Optional context

        Returns:
            Heading in degrees (0-360)

        Raises:
            InsufficientDataError: If data length is not exactly 4 bytes
        """
        if len(data) != 4:
            raise InsufficientDataError("Thingy Heading", data, 4)

        heading_raw = DataParser.parse_int32(data, offset=0, signed=True)
        return float(heading_raw / 65536.0)

    def encode_value(self, data: float) -> bytearray:
        """Encode heading to Nordic Thingy:52 format.

        Args:
            data: Heading in degrees

        Returns:
            Encoded bytes (4 bytes)
        """
        heading_raw = int(data * 65536)
        return DataParser.encode_int32(heading_raw, signed=True)

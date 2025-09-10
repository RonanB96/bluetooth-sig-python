"""Template characteristic classes for common patterns.

This module provides reusable template characteristic classes that eliminate
code duplication across the 138+ characteristic implementations. Each template
follows the declarative validation pattern and uses DataParser utilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..constants import (
    ABSOLUTE_ZERO_CELSIUS,
    PERCENTAGE_MAX,
    SINT8_MAX,
    SINT8_MIN,
    SINT16_MAX,
    TEMPERATURE_RESOLUTION,
    UINT8_MAX,
    UINT16_MAX,
)
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser


@dataclass
class VectorData:
    """3D vector measurement data."""

    x_axis: float
    y_axis: float
    z_axis: float


@dataclass
class Vector2DData:
    """2D vector measurement data."""

    x_axis: float
    y_axis: float


@dataclass
class SimpleUint8Characteristic(BaseCharacteristic):
    """Template for simple 1-byte unsigned integer characteristics.

    This template handles characteristics that store a simple unsigned 8-bit
    integer value (0-255). Subclasses can override validation ranges as needed.

    Example usage:
        @dataclass
        class AlertLevelCharacteristic(SimpleUint8Characteristic):
            '''Alert level (0=none, 1=mild, 2=high).'''

            max_value: int = 2  # Override to restrict range
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 1  # type: ignore[assignment]
    min_value: int = 0  # type: ignore[assignment]
    max_value: int = UINT8_MAX  # type: ignore[assignment]
    expected_type: type = int  # type: ignore[assignment]

    def decode_value(self, data: bytearray) -> int:
        """Parse single byte as uint8."""
        return DataParser.parse_int8(data, 0, signed=False)

    def encode_value(self, data: int) -> bytearray:
        """Encode uint8 value to bytes."""
        return DataParser.encode_int8(data, signed=False)


@dataclass
class SimpleSint8Characteristic(BaseCharacteristic):
    """Template for simple 1-byte signed integer characteristics.

    This template handles characteristics that store a simple signed 8-bit
    integer value (-128 to 127).

    Example usage:
        @dataclass
        class TxPowerLevelCharacteristic(SimpleSint8Characteristic):
            '''TX power level in dBm.'''

            measurement_unit: str = "dBm"
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 1  # type: ignore[assignment]
    min_value: int = SINT8_MIN  # -128 # type: ignore[assignment]
    max_value: int = SINT8_MAX  # 127 # type: ignore[assignment]
    expected_type: type = int  # type: ignore[assignment]

    # Subclasses can override this
    measurement_unit: str = "units"

    def decode_value(self, data: bytearray) -> int:
        """Parse single byte as sint8."""
        return DataParser.parse_int8(data, 0, signed=True)

    def encode_value(self, data: int) -> bytearray:
        """Encode sint8 value to bytes."""
        return DataParser.encode_int8(data, signed=True)

    @property
    def unit(self) -> str:
        """Return the measurement unit."""
        return self.measurement_unit


@dataclass
class SimpleUint16Characteristic(BaseCharacteristic):
    """Template for simple 2-byte unsigned integer characteristics.

    This template handles characteristics that store a simple unsigned 16-bit
    integer value (0-65535) in little-endian format.

    Example usage:
        @dataclass
        class SensorValueCharacteristic(SimpleUint16Characteristic):
            '''Raw sensor value (0-65535).'''
            pass  # Uses default uint16 range
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 2  # type: ignore[assignment]
    min_value: int = 0  # type: ignore[assignment]
    max_value: int = UINT16_MAX  # type: ignore[assignment]
    expected_type: type = int  # type: ignore[assignment]

    def decode_value(self, data: bytearray) -> int:
        """Parse 2 bytes as uint16."""
        return DataParser.parse_int16(data, 0, signed=False)

    def encode_value(self, data: int) -> bytearray:
        """Encode uint16 value to bytes."""
        return DataParser.encode_int16(data, signed=False)


@dataclass
class ConcentrationCharacteristic(BaseCharacteristic):
    """Template for concentration measurements (uint16 with resolution).

    This template handles environmental sensor characteristics that measure
    concentrations (like air quality, chemical levels) with configurable
    resolution and units.

    Example usage:
        @dataclass
        class CO2ConcentrationCharacteristic(ConcentrationCharacteristic):
            '''CO2 concentration in ppm.'''

            resolution: float = 1.0
            concentration_unit: str = "ppm"
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 2  # type: ignore[assignment]
    min_value: float = 0.0  # type: ignore[assignment]
    max_value: float = float(UINT16_MAX)  # type: ignore[assignment]
    expected_type: type = float  # type: ignore[assignment]
    # Subclasses should override these
    resolution: float = 1.0  # Default resolution
    concentration_unit: str = "ppm"  # Default unit

    def decode_value(self, data: bytearray) -> float:
        """Parse concentration with resolution."""
        raw_value = DataParser.parse_int16(data, 0, signed=False)
        return raw_value * self.resolution

    def encode_value(self, data: float) -> bytearray:
        """Encode concentration value to bytes."""
        raw_value = int(data / self.resolution)
        return DataParser.encode_int16(raw_value, signed=False)

    @property
    def unit(self) -> str:
        """Return the concentration unit."""
        return self.concentration_unit


@dataclass
class TemperatureCharacteristic(BaseCharacteristic):
    """Template for temperature measurements (sint16, 0.01°C resolution).

    This template handles temperature characteristics following the Bluetooth SIG
    standard format: signed 16-bit integer with 0.01°C resolution.

    Example usage:
        @dataclass
        class AmbientTemperatureCharacteristic(TemperatureCharacteristic):
            '''Ambient temperature measurement.'''
            pass  # Uses standard temperature format
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 2  # type: ignore[assignment]
    min_value: float = (  # type: ignore[assignment]
        ABSOLUTE_ZERO_CELSIUS  # Absolute zero in Celsius
    )
    max_value: float = (  # type: ignore[assignment]
        SINT16_MAX * TEMPERATURE_RESOLUTION
    )  # Max sint16 * resolution
    expected_type: type = float  # type: ignore[assignment]

    def decode_value(self, data: bytearray) -> float:
        """Parse temperature in 0.01°C resolution."""
        raw_value = DataParser.parse_int16(data, 0, signed=True)
        return raw_value * TEMPERATURE_RESOLUTION

    def encode_value(self, data: float) -> bytearray:
        """Encode temperature to bytes."""
        raw_value = int(data / TEMPERATURE_RESOLUTION)
        return DataParser.encode_int16(raw_value, signed=True)

    @property
    def unit(self) -> str:
        """Return temperature unit."""
        # Check for manual unit override first
        manual_unit = getattr(self, "_manual_unit", None)
        if manual_unit:
            return manual_unit
        return "°C"


@dataclass
class IEEE11073FloatCharacteristic(BaseCharacteristic):
    """Template for IEEE 11073 SFLOAT format characteristics.

    This template handles medical device characteristics that use the IEEE 11073
    SFLOAT format (16-bit floating point with special values for NaN, infinity).

    Example usage:
        @dataclass
        class BloodPressureCharacteristic(IEEE11073FloatCharacteristic):
            '''Blood pressure measurement in mmHg.'''

            @property
            def unit(self) -> str:
                return "mmHg"
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 2  # type: ignore[assignment]
    expected_type: type = float  # type: ignore[assignment]
    allow_variable_length: bool = True  # Some have additional data

    def decode_value(self, data: bytearray) -> float:
        """Parse IEEE 11073 SFLOAT format."""
        # IEEE11073Parser.parse_sfloat expects raw bytes/bytearray
        return IEEE11073Parser.parse_sfloat(data, 0)

    def encode_value(self, data: float) -> bytearray:
        """Encode float to IEEE 11073 format."""
        return IEEE11073Parser.encode_sfloat(data)


@dataclass
class PercentageCharacteristic(BaseCharacteristic):
    """Template for percentage values (0-100%).

    This template handles characteristics that represent percentage values
    using a single unsigned byte (0-100).

    Example usage:
        @dataclass
        class BatteryLevelCharacteristic(PercentageCharacteristic):
            '''Battery level percentage (0-100%).'''
            pass  # Everything handled by template!
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 1  # type: ignore[assignment]
    min_value: int = 0  # type: ignore[assignment]
    max_value: int = PERCENTAGE_MAX  # type: ignore[assignment]
    expected_type: type = int  # type: ignore[assignment]

    def decode_value(self, data: bytearray) -> int:
        """Parse percentage value."""
        return DataParser.parse_int8(data, 0, signed=False)

    def encode_value(self, data: int) -> bytearray:
        """Encode percentage to bytes."""
        return DataParser.encode_int8(data, signed=False)

    @property
    def unit(self) -> str:
        """Return percentage unit."""
        return "%"


@dataclass
class PressureCharacteristic(BaseCharacteristic):
    """Template for pressure measurements (uint32, 0.1 Pa resolution).

    This template handles pressure characteristics following the Bluetooth SIG
    standard format: unsigned 32-bit integer with 0.1 Pa resolution, typically
    converted to hPa for display.

    Example usage:
        @dataclass
        class BarometricPressureCharacteristic(PressureCharacteristic):  # type: ignore[assignment]
            '''Barometric pressure measurement.'''  # type: ignore[assignment]
            pass  # Uses standard pressure format
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 4  # type: ignore[assignment]
    min_value: float = 0.0  # type: ignore[assignment]
    max_value: float = 429496729.5  # Max uint32 * 0.1 Pa  # type: ignore[assignment]
    expected_type: type = float  # type: ignore[assignment]

    def decode_value(self, data: bytearray) -> float:
        """Parse pressure in 0.1 Pa resolution."""
        raw_value = DataParser.parse_int32(data, 0, signed=False)
        return raw_value * 0.1  # Convert to Pa

    def encode_value(self, data: float) -> bytearray:
        """Encode pressure to bytes."""
        raw_value = int(data / 0.1)
        return DataParser.encode_int32(raw_value, signed=False)

    @property
    def unit(self) -> str:
        """Return pressure unit (Pa)."""
        return "Pa"


@dataclass
class VectorCharacteristic(BaseCharacteristic):  # pylint: disable=too-many-instance-attributes
    """Template for multi-dimensional vector measurements.

    This template handles characteristics that measure 3D vectors like
    magnetic flux density, acceleration, etc.

    Example usage:
        @dataclass
        class MagneticFluxDensity3DCharacteristic(VectorCharacteristic):
            '''3D magnetic flux density measurement.'''

            vector_components: list[str] = field(default_factory=lambda: ["x", "y", "z"])
            component_unit: str = "µT"
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 6  # 3 components * 2 bytes each  # type: ignore[assignment]
    min_length: int = 6  # type: ignore[assignment]
    allow_variable_length: bool = False
    expected_type: type = VectorData  # type: ignore[assignment]

    # Subclasses should override these
    vector_components: list[str] = field(default_factory=lambda: ["x", "y", "z"])
    component_unit: str = "units"
    resolution: float = 0.01  # Default resolution

    def decode_value(self, data: bytearray) -> VectorData:
        """Parse vector components."""
        if len(data) < self.expected_length:
            raise ValueError(
                f"Vector data must be at least {self.expected_length} bytes"
            )

        # Parse x, y, z components
        x_raw = DataParser.parse_int16(data, 0, signed=True)
        y_raw = DataParser.parse_int16(data, 2, signed=True)
        z_raw = DataParser.parse_int16(data, 4, signed=True)

        return VectorData(
            x_axis=x_raw * self.resolution,
            y_axis=y_raw * self.resolution,
            z_axis=z_raw * self.resolution,
        )

    def encode_value(self, data: VectorData) -> bytearray:
        """Encode vector components to bytes."""
        result = bytearray()

        x_raw = int(data.x_axis / self.resolution)
        y_raw = int(data.y_axis / self.resolution)
        z_raw = int(data.z_axis / self.resolution)

        result.extend(DataParser.encode_int16(x_raw, signed=True))
        result.extend(DataParser.encode_int16(y_raw, signed=True))
        result.extend(DataParser.encode_int16(z_raw, signed=True))

        return result

    @property
    def unit(self) -> str:
        """Return component unit."""
        return self.component_unit


@dataclass
class ScaledUint16Characteristic(BaseCharacteristic):
    """Template for uint16 characteristics with configurable resolution.

    This template handles characteristics that store uint16 values with a
    specific resolution multiplier (e.g., voltage with 1/64 V resolution).

    Example usage:
        @dataclass
        class VoltageCharacteristic(ScaledUint16Characteristic):
            '''Voltage measurement with 1/64 V resolution.'''

            resolution: float = 1/64
            measurement_unit: str = "V"
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 2  # type: ignore[assignment]
    min_value: float = 0.0  # type: ignore[assignment]
    max_value: float = (  # type: ignore[assignment]
        65535.0  # Will be scaled by resolution
    )
    expected_type: type = float  # type: ignore[assignment]

    # Subclasses should override these
    resolution: float = 1.0  # Default resolution
    measurement_unit: str = "units"  # Default unit

    def decode_value(self, data: bytearray) -> float:
        """Parse uint16 value with resolution scaling."""
        raw_value = DataParser.parse_int16(data, 0, signed=False)
        return raw_value * self.resolution

    def encode_value(self, data: float) -> bytearray:
        """Encode scaled value to uint16 bytes."""
        raw_value = int(data / self.resolution)
        return DataParser.encode_int16(raw_value, signed=False)

    @property
    def unit(self) -> str:
        """Return the measurement unit."""
        return self.measurement_unit


@dataclass
class TemperatureLikeSint8Characteristic(BaseCharacteristic):
    """Template for temperature-like measurements using sint8 (1°C resolution).

    This template handles characteristics that measure temperature-like values
    (dew point, wind chill, etc.) using signed 8-bit integers with 1°C resolution.

    Example usage:
        @dataclass
        class DewPointCharacteristic(TemperatureLikeSint8Characteristic):
            '''Dew point measurement in °C.'''
            pass  # Uses standard sint8 temperature format
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 1  # type: ignore[assignment]
    min_value: int = SINT8_MIN  # -128°C  # type: ignore[assignment]
    max_value: int = SINT8_MAX  # 127°C  # type: ignore[assignment]
    expected_type: type = float  # type: ignore[assignment]

    def decode_value(self, data: bytearray) -> float:
        """Parse temperature-like value (sint8, 1°C resolution)."""
        raw_value = DataParser.parse_int8(data, 0, signed=True)
        return float(raw_value)

    def encode_value(self, data: float) -> bytearray:
        """Encode temperature-like value to bytes."""
        temp_value = int(round(data))
        return DataParser.encode_int8(temp_value, signed=True)

    @property
    def unit(self) -> str:
        """Return temperature unit."""
        return "°C"


@dataclass
class TemperatureLikeUint8Characteristic(BaseCharacteristic):
    """Template for temperature-like measurements using uint8 (1°C resolution).

    This template handles characteristics that measure temperature-like values
    (heat index, etc.) using unsigned 8-bit integers with 1°C resolution.

    Example usage:
        @dataclass
        class HeatIndexCharacteristic(TemperatureLikeUint8Characteristic):
            '''Heat index measurement in °C.'''
            pass  # Uses standard uint8 temperature format
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 1  # type: ignore[assignment]
    min_value: int = 0  # 0°C  # type: ignore[assignment]
    max_value: int = UINT8_MAX  # 255°C  # type: ignore[assignment]
    expected_type: type = float  # type: ignore[assignment]

    def decode_value(self, data: bytearray) -> float:
        """Parse temperature-like value (uint8, 1°C resolution)."""
        raw_value = DataParser.parse_int8(data, 0, signed=False)
        return float(raw_value)

    def encode_value(self, data: float) -> bytearray:
        """Encode temperature-like value to bytes."""
        temp_value = int(round(data))
        return DataParser.encode_int8(temp_value, signed=False)

    @property
    def unit(self) -> str:
        """Return temperature unit."""
        return "°C"


@dataclass
class Uint24ScaledCharacteristic(BaseCharacteristic):
    """Template for uint24 characteristics with configurable resolution.

    This template handles characteristics that store 24-bit unsigned values
    with a specific resolution multiplier (e.g., illuminance with 0.01 lx resolution).

    Example usage:
        @dataclass
        class IlluminanceCharacteristic(Uint24ScaledCharacteristic):
            '''Illuminance measurement with 0.01 lx resolution.'''

            resolution: float = 0.01
            measurement_unit: str = "lx"
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 3  # type: ignore[assignment]
    min_value: float = 0.0  # type: ignore[assignment]
    max_value: float = 16777215.0  # Max uint24, will be scaled by resolution  # type: ignore[assignment]
    expected_type: type = float  # type: ignore[assignment]

    # Subclasses should override these
    resolution: float = 1.0  # Default resolution
    measurement_unit: str = "units"  # Default unit

    def decode_value(self, data: bytearray) -> float:
        """Parse uint24 value with resolution scaling."""
        if len(data) < 3:
            raise ValueError(f"{self.__class__.__name__} data must be at least 3 bytes")

        raw_value = int.from_bytes(data[:3], byteorder="little", signed=False)
        return raw_value * self.resolution

    def encode_value(self, data: float) -> bytearray:
        """Encode scaled value to uint24 bytes."""
        raw_value = int(data / self.resolution)
        raw_value = min(raw_value, 0xFFFFFF)  # Clamp to uint24 max
        return bytearray(raw_value.to_bytes(3, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Return the measurement unit."""
        return self.measurement_unit


@dataclass
class Sint24ScaledCharacteristic(BaseCharacteristic):
    """Template for sint24 characteristics with configurable resolution.

    This template handles characteristics that store 24-bit signed values
    with a specific resolution multiplier (e.g., elevation with 0.01 m resolution).

    Example usage:
        @dataclass
        class ElevationCharacteristic(Sint24ScaledCharacteristic):
            '''Elevation measurement with 0.01 m resolution.'''

            resolution: float = 0.01
            measurement_unit: str = "m"
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 3  # type: ignore[assignment]
    min_value: float = -83886.08  # Min sint24 * 0.01  # type: ignore[assignment]
    max_value: float = 83886.07  # Max sint24 * 0.01  # type: ignore[assignment]
    expected_type: type = float  # type: ignore[assignment]

    # Subclasses should override these
    resolution: float = 1.0  # Default resolution
    measurement_unit: str = "units"  # Default unit

    def decode_value(self, data: bytearray) -> float:
        """Parse sint24 value with resolution scaling."""
        if len(data) < 3:
            raise ValueError(f"{self.__class__.__name__} data must be at least 3 bytes")

        # Parse sint24 (little endian) - handle 24-bit signed integer
        raw_bytes = data[:3] + b"\x00"  # Pad to 4 bytes
        raw_value = int.from_bytes(raw_bytes, byteorder="little", signed=False)

        # Handle sign extension for 24-bit signed value
        if raw_value & 0x800000:  # Check if negative (bit 23 set)
            raw_value = raw_value - 0x1000000  # Convert to negative

        return raw_value * self.resolution

    def encode_value(self, data: float) -> bytearray:
        """Encode scaled value to sint24 bytes."""
        raw_value = int(data / self.resolution)

        # Ensure it fits in sint24 range
        if not -8388608 <= raw_value <= 8388607:
            raise ValueError(f"Value {raw_value} exceeds sint24 range")

        # Convert to unsigned representation for encoding
        if raw_value < 0:
            raw_unsigned = raw_value + 0x1000000  # Convert negative to 24-bit unsigned
        else:
            raw_unsigned = raw_value

        return bytearray(raw_unsigned.to_bytes(3, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Return the measurement unit."""
        return self.measurement_unit


@dataclass
class SoundPressureCharacteristic(BaseCharacteristic):
    """Template for sound pressure level measurements (uint16, 0.1 dB resolution).

    This template handles sound pressure level characteristics following the
    Bluetooth SIG standard format: unsigned 16-bit integer with 0.1 dB resolution.

    Example usage:
        @dataclass
        class SoundPressureLevelCharacteristic(SoundPressureCharacteristic):
            '''Sound pressure level measurement.'''
            pass  # Uses standard sound pressure format
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 2  # type: ignore[assignment]
    min_value: float = 0.0  # type: ignore[assignment]
    max_value: float = 6553.5  # Max uint16 * 0.1  # type: ignore[assignment]
    expected_type: type = float  # type: ignore[assignment]

    def decode_value(self, data: bytearray) -> float:
        """Parse sound pressure level in 0.1 dB resolution."""
        raw_value = DataParser.parse_int16(data, 0, signed=False)
        return raw_value * 0.1

    def encode_value(self, data: float) -> bytearray:
        """Encode sound pressure level to bytes."""
        raw_value = int(data / 0.1)
        return DataParser.encode_int16(raw_value, signed=False)

    @property
    def unit(self) -> str:
        """Return sound pressure unit."""
        return "dB"


@dataclass
class WindSpeedCharacteristic(BaseCharacteristic):
    """Template for wind speed measurements (uint16, 0.01 m/s resolution).

    This template handles wind speed characteristics following the Bluetooth SIG
    standard format: unsigned 16-bit integer with 0.01 m/s resolution.

    Example usage:
        @dataclass
        class ApparentWindSpeedCharacteristic(WindSpeedCharacteristic):
            '''Apparent wind speed measurement.'''
            pass  # Uses standard wind speed format
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 2  # type: ignore[assignment]
    min_value: float = 0.0  # type: ignore[assignment]
    max_value: float = 655.35  # Max uint16 * 0.01  # type: ignore[assignment]
    expected_type: type = float  # type: ignore[assignment]

    def decode_value(self, data: bytearray) -> float:
        """Parse wind speed in 0.01 m/s resolution."""
        raw_value = DataParser.parse_int16(data, 0, signed=False)
        return raw_value * 0.01

    def encode_value(self, data: float) -> bytearray:
        """Encode wind speed to bytes."""
        raw_value = int(data / 0.01)
        return DataParser.encode_int16(raw_value, signed=False)

    @property
    def unit(self) -> str:
        """Return wind speed unit."""
        return "m/s"


@dataclass
class WindDirectionCharacteristic(BaseCharacteristic):
    """Template for wind direction measurements (uint16, 0.01° resolution).

    This template handles wind direction characteristics following the Bluetooth SIG
    standard format: unsigned 16-bit integer with 0.01° resolution.

    Example usage:
        @dataclass
        class ApparentWindDirectionCharacteristic(WindDirectionCharacteristic):
            '''Apparent wind direction measurement.'''
            pass  # Uses standard wind direction format
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 2  # type: ignore[assignment]
    min_value: float = 0.0  # type: ignore[assignment]
    max_value: float = 359.99  # Almost full circle  # type: ignore[assignment]
    expected_type: type = float  # type: ignore[assignment]

    def decode_value(self, data: bytearray) -> float:
        """Parse wind direction in 0.01° resolution."""
        raw_value = DataParser.parse_int16(data, 0, signed=False)
        direction = raw_value * 0.01
        # Ensure direction stays within 0-360° range
        return direction % 360.0

    def encode_value(self, data: float) -> bytearray:
        """Encode wind direction to bytes."""
        # Normalize to 0-360° range
        direction = float(data) % 360.0
        raw_value = int(direction / 0.01)
        return DataParser.encode_int16(raw_value, signed=False)

    @property
    def unit(self) -> str:
        """Return wind direction unit."""
        return "°"


@dataclass
class EnumCharacteristic(BaseCharacteristic):
    """Template for enumerated value characteristics (uint8).

    This template handles characteristics that use enumerated values
    stored as unsigned 8-bit integers.

    Example usage:
        @dataclass
        class BarometricPressureTrendCharacteristic(EnumCharacteristic):
            '''Barometric pressure trend enumeration.'''

            enum_class: type = BarometricPressureTrend  # Must set this
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 1  # type: ignore[assignment]
    expected_type: type = object  # Will be enum type  # type: ignore[assignment]

    # Subclasses MUST override this
    enum_class: type = None  # type: ignore[assignment]

    def decode_value(self, data: bytearray) -> object:
        """Parse enumerated value."""
        if self.enum_class is None:
            raise NotImplementedError("Subclass must set enum_class")

        raw_value = DataParser.parse_int8(data, 0, signed=False)

        # Use from_value method if available for safe conversion
        if hasattr(self.enum_class, "from_value"):
            return self.enum_class.from_value(raw_value)

        try:
            return self.enum_class(raw_value)
        except ValueError:
            # Fallback to raw value if enum doesn't handle it
            return raw_value

    def encode_value(self, data: object) -> bytearray:
        """Encode enumerated value to bytes."""
        if hasattr(data, "value"):
            # Enum type
            raw_value = data.value  # type: ignore[attr-defined]
        else:
            # Raw integer
            raw_value = int(data)  # type: ignore[arg-type]

        return DataParser.encode_int8(raw_value, signed=False)

    @property
    def unit(self) -> str:
        """Return unit (none for enums)."""
        return ""


@dataclass
class Vector2DCharacteristic(BaseCharacteristic):  # pylint: disable=too-many-instance-attributes
    """Template for 2D vector measurements.

    This template handles characteristics that measure 2D vectors like
    2D magnetic flux density.

    Example usage:
        @dataclass
        class MagneticFluxDensity2DCharacteristic(Vector2DCharacteristic):
            '''2D magnetic flux density measurement.'''

            vector_components: list[str] = field(default_factory=lambda: ["x_axis", "y_axis"])
            component_unit: str = "T"
            resolution: float = 1e-7
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 4  # 2 components * 2 bytes each  # type: ignore[assignment]
    min_length: int = 4  # type: ignore[assignment]
    allow_variable_length: bool = False
    expected_type: type = Vector2DData  # type: ignore[assignment]

    # Subclasses should override these
    vector_components: list[str] = field(default_factory=lambda: ["x", "y"])
    component_unit: str = "units"
    resolution: float = 0.01  # Default resolution

    def decode_value(self, data: bytearray) -> Vector2DData:
        """Parse 2D vector components."""
        if len(data) < self.expected_length:
            raise ValueError(
                f"Vector data must be at least {self.expected_length} bytes"
            )

        # Parse x, y components
        x_raw = DataParser.parse_int16(data, 0, signed=True)
        y_raw = DataParser.parse_int16(data, 2, signed=True)

        return Vector2DData(
            x_axis=x_raw * self.resolution,
            y_axis=y_raw * self.resolution,
        )

    def encode_value(self, data: Vector2DData) -> bytearray:
        """Encode 2D vector components to bytes."""
        result = bytearray()

        x_raw = int(data.x_axis / self.resolution)
        y_raw = int(data.y_axis / self.resolution)

        result.extend(DataParser.encode_int16(x_raw, signed=True))
        result.extend(DataParser.encode_int16(y_raw, signed=True))

        return result

    @property
    def unit(self) -> str:
        """Return component unit."""
        return self.component_unit


@dataclass
class SignedSoundPressureCharacteristic(BaseCharacteristic):
    """Template for signed sound pressure level measurements (sint16, 0.1 dB resolution).

    This template handles sound pressure level characteristics that can be negative,
    using signed 16-bit integer with 0.1 dB resolution.

    Example usage:
        @dataclass
        class SoundPressureLevelCharacteristic(SignedSoundPressureCharacteristic):
            '''Sound pressure level measurement with negative values.'''
            pass  # Uses signed sound pressure format
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 2  # type: ignore[assignment]
    min_value: float = -3276.8  # Min sint16 * 0.1  # type: ignore[assignment]
    max_value: float = 3276.7  # Max sint16 * 0.1  # type: ignore[assignment]
    expected_type: type = float  # type: ignore[assignment]

    def decode_value(self, data: bytearray) -> float:
        """Parse signed sound pressure level in 0.1 dB resolution."""
        raw_value = DataParser.parse_int16(data, 0, signed=True)
        return raw_value * 0.1

    def encode_value(self, data: float) -> bytearray:
        """Encode signed sound pressure level to bytes."""
        raw_value = int(data / 0.1)
        return DataParser.encode_int16(raw_value, signed=True)

    @property
    def unit(self) -> str:
        """Return sound pressure unit."""
        return "dB"


__all__ = [
    "VectorData",
    "Vector2DData",
    "SimpleUint8Characteristic",
    "SimpleSint8Characteristic",
    "SimpleUint16Characteristic",
    "ConcentrationCharacteristic",
    "TemperatureCharacteristic",
    "IEEE11073FloatCharacteristic",
    "PercentageCharacteristic",
    "PressureCharacteristic",
    "VectorCharacteristic",
    "ScaledUint16Characteristic",
    "TemperatureLikeSint8Characteristic",
    "TemperatureLikeUint8Characteristic",
    "Uint24ScaledCharacteristic",
    "Sint24ScaledCharacteristic",
    "WindSpeedCharacteristic",
    "WindDirectionCharacteristic",
    "SoundPressureCharacteristic",
    "SignedSoundPressureCharacteristic",
    "EnumCharacteristic",
    "Vector2DCharacteristic",
]

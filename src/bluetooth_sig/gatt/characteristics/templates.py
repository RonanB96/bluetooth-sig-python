"""Template characteristic classes for common patterns.

This module provides reusable template characteristic classes that eliminate
code duplication across the 138+ characteristic implementations. Each template
follows the declarative validation pattern and uses DataParser utilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser

# Data type maximum values constants
UINT8_MAX = (1 << 8) - 1  # 255
UINT16_MAX = (1 << 16) - 1  # 65535
SINT8_MAX = (1 << 7) - 1  # 127
SINT8_MIN = -(1 << 7)  # -128
SINT16_MAX = (1 << 15) - 1  # 32767
SINT16_MIN = -(1 << 15)  # -32768
PERCENTAGE_MAX = 100  # Maximum percentage value
ABSOLUTE_ZERO_CELSIUS = -273.15  # Absolute zero temperature in Celsius


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
    expected_length: int = 1
    min_value: int = 0
    max_value: int = UINT8_MAX
    expected_type: type = int

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
    expected_length: int = 1
    min_value: int = SINT8_MIN  # -128
    max_value: int = SINT8_MAX  # 127
    expected_type: type = int

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
    expected_length: int = 2
    min_value: int = 0
    max_value: int = UINT16_MAX
    expected_type: type = int

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
    expected_length: int = 2
    min_value: float = 0.0
    max_value: float = float(UINT16_MAX)
    expected_type: type = float

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
    expected_length: int = 2
    min_value: float = ABSOLUTE_ZERO_CELSIUS  # Absolute zero in Celsius
    max_value: float = SINT16_MAX * 0.01  # Max sint16 * 0.01
    expected_type: type = float

    def decode_value(self, data: bytearray) -> float:
        """Parse temperature in 0.01°C resolution."""
        raw_value = DataParser.parse_int16(data, 0, signed=True)
        return raw_value * 0.01

    def encode_value(self, data: float) -> bytearray:
        """Encode temperature to bytes."""
        raw_value = int(data / 0.01)
        return DataParser.encode_int16(raw_value, signed=True)

    @property
    def unit(self) -> str:
        """Return temperature unit."""
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
    expected_length: int = 2
    expected_type: type = float
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
    expected_length: int = 1
    min_value: int = 0
    max_value: int = PERCENTAGE_MAX
    expected_type: type = int

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
        class BarometricPressureCharacteristic(PressureCharacteristic):
            '''Barometric pressure measurement.'''
            pass  # Uses standard pressure format
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 4
    min_value: float = 0.0
    max_value: float = 429496729.5  # Max uint32 * 0.1 Pa
    expected_type: type = float

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
class VectorCharacteristic(BaseCharacteristic):
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
    expected_length: int = 6  # 3 components * 2 bytes each
    min_length: int = 6
    allow_variable_length: bool = False
    expected_type: type = dict

    # Subclasses should override these
    vector_components: list[str] = field(default_factory=lambda: ["x", "y", "z"])
    component_unit: str = "units"
    resolution: float = 0.01  # Default resolution

    def decode_value(self, data: bytearray) -> dict[str, float]:
        """Parse vector components."""
        if len(data) < self.expected_length:
            raise ValueError(f"Vector data must be at least {self.expected_length} bytes")
        
        result = {}
        for i, component in enumerate(self.vector_components):
            if i * 2 + 2 <= len(data):
                raw_value = DataParser.parse_int16(data, i * 2, signed=True)
                result[component] = raw_value * self.resolution
        
        return result

    def encode_value(self, data: dict[str, float]) -> bytearray:
        """Encode vector components to bytes."""
        result = bytearray()
        for component in self.vector_components:
            if component in data:
                raw_value = int(data[component] / self.resolution)
                result.extend(DataParser.encode_int16(raw_value, signed=True))
            else:
                result.extend(bytearray(2))  # Zero fill missing components
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
    expected_length: int = 2
    min_value: float = 0.0
    max_value: float = 65535.0  # Will be scaled by resolution
    expected_type: type = float

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
    expected_length: int = 1
    min_value: int = SINT8_MIN  # -128°C
    max_value: int = SINT8_MAX  # 127°C
    expected_type: type = float

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
    expected_length: int = 1
    min_value: int = 0  # 0°C
    max_value: int = UINT8_MAX  # 255°C
    expected_type: type = float

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
    expected_length: int = 3
    min_value: float = 0.0
    max_value: float = 16777215.0  # Max uint24, will be scaled by resolution
    expected_type: type = float

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
        if raw_value > 0xFFFFFF:  # Clamp to uint24 max
            raw_value = 0xFFFFFF
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
    expected_length: int = 3
    min_value: float = -83886.08  # Min sint24 * 0.01
    max_value: float = 83886.07   # Max sint24 * 0.01
    expected_type: type = float

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
    expected_length: int = 2
    min_value: float = 0.0
    max_value: float = 655.35  # Max uint16 * 0.01
    expected_type: type = float

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
    expected_length: int = 2
    min_value: float = 0.0
    max_value: float = 359.99  # Almost full circle
    expected_type: type = float

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
class RainfallCharacteristic(BaseCharacteristic):
    """Template for rainfall measurements (uint16, 1 mm resolution).

    This template handles rainfall characteristics following the Bluetooth SIG
    standard format: unsigned 16-bit integer with 1 mm resolution.

    Example usage:
        @dataclass
        class RainfallCharacteristic(RainfallCharacteristic):
            '''Rainfall measurement.'''
            pass  # Uses standard rainfall format
    """

    _is_template: bool = True  # Mark as template for test exclusion
    expected_length: int = 2
    min_value: float = 0.0
    max_value: float = 65535.0  # Max uint16 mm
    expected_type: type = float

    def decode_value(self, data: bytearray) -> float:
        """Parse rainfall in 1 mm resolution."""
        raw_value = DataParser.parse_int16(data, 0, signed=False)
        return float(raw_value)  # Already in millimeters

    def encode_value(self, data: float) -> bytearray:
        """Encode rainfall to bytes."""
        raw_value = int(round(data))
        return DataParser.encode_int16(raw_value, signed=False)

    @property
    def unit(self) -> str:
        """Return rainfall unit."""
        return "mm"


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
    expected_length: int = 2
    min_value: float = 0.0
    max_value: float = 6553.5  # Max uint16 * 0.1
    expected_type: type = float

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
    expected_length: int = 1
    expected_type: type = object  # Will be enum type
    
    # Subclasses MUST override this
    enum_class: type = None

    def decode_value(self, data: bytearray) -> object:
        """Parse enumerated value."""
        if self.enum_class is None:
            raise NotImplementedError("Subclass must set enum_class")
            
        raw_value = DataParser.parse_int8(data, 0, signed=False)
        
        # Use from_value method if available for safe conversion
        if hasattr(self.enum_class, 'from_value'):
            return self.enum_class.from_value(raw_value)
        else:
            try:
                return self.enum_class(raw_value)
            except ValueError:
                # Fallback to raw value if enum doesn't handle it
                return raw_value

    def encode_value(self, data: object) -> bytearray:
        """Encode enumerated value to bytes."""
        if hasattr(data, 'value'):
            # Enum type
            raw_value = data.value
        else:
            # Raw integer
            raw_value = int(data)
            
        return DataParser.encode_int8(raw_value, signed=False)

    @property
    def unit(self) -> str:
        """Return unit (none for enums)."""
        return ""


@dataclass
class Vector2DCharacteristic(BaseCharacteristic):
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
    expected_length: int = 4  # 2 components * 2 bytes each
    min_length: int = 4
    allow_variable_length: bool = False
    expected_type: type = dict

    # Subclasses should override these
    vector_components: list[str] = field(default_factory=lambda: ["x", "y"])
    component_unit: str = "units"
    resolution: float = 0.01  # Default resolution

    def decode_value(self, data: bytearray) -> dict[str, float]:
        """Parse 2D vector components."""
        if len(data) < self.expected_length:
            raise ValueError(f"Vector data must be at least {self.expected_length} bytes")
        
        result = {}
        for i, component in enumerate(self.vector_components):
            if i * 2 + 2 <= len(data):
                raw_value = DataParser.parse_int16(data, i * 2, signed=True)
                result[component] = raw_value * self.resolution
        
        return result

    def encode_value(self, data: dict[str, float]) -> bytearray:
        """Encode 2D vector components to bytes."""
        result = bytearray()
        for component in self.vector_components:
            if component in data:
                raw_value = int(data[component] / self.resolution)
                result.extend(DataParser.encode_int16(raw_value, signed=True))
            else:
                result.extend(bytearray(2))  # Zero fill missing components
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
    expected_length: int = 2
    min_value: float = -3276.8  # Min sint16 * 0.1
    max_value: float = 3276.7   # Max sint16 * 0.1
    expected_type: type = float

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
    "RainfallCharacteristic",
    "SoundPressureCharacteristic",
    "SignedSoundPressureCharacteristic",
    "EnumCharacteristic",
    "Vector2DCharacteristic",
]

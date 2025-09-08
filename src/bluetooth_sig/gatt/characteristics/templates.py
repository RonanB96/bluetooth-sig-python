"""Template characteristic classes for common patterns.

This module provides reusable template characteristic classes that eliminate
code duplication across the 138+ characteristic implementations. Each template
follows the declarative validation pattern and uses DataParser utilities.
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser

# Data type maximum values constants
UINT8_MAX = (1 << 8) - 1  # 255
UINT16_MAX = (1 << 16) - 1  # 65535
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
        return DataParser.parse_uint8(data, 0)

    def encode_value(self, data: int) -> bytearray:
        """Encode uint8 value to bytes."""
        return DataParser.encode_uint8(data)


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
        return DataParser.parse_uint16(data, 0)

    def encode_value(self, data: int) -> bytearray:
        """Encode uint16 value to bytes."""
        return DataParser.encode_uint16(data)


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
        raw_value = DataParser.parse_uint16(data, 0)
        return raw_value * self.resolution

    def encode_value(self, data: float) -> bytearray:
        """Encode concentration value to bytes."""
        raw_value = int(data / self.resolution)
        return DataParser.encode_uint16(raw_value)

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
        raw_value = DataParser.parse_sint16(data, 0)
        return raw_value * 0.01

    def encode_value(self, data: float) -> bytearray:
        """Encode temperature to bytes."""
        raw_value = int(data / 0.01)
        return DataParser.encode_sint16(raw_value)

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
        # Parse first 2 bytes as uint16 for IEEE11073Parser
        raw_value = DataParser.parse_uint16(data, 0)
        return IEEE11073Parser.parse_sfloat(raw_value)

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
        return DataParser.parse_uint8(data, 0)

    def encode_value(self, data: int) -> bytearray:
        """Encode percentage to bytes."""
        return DataParser.encode_uint8(data)

    @property
    def unit(self) -> str:
        """Return percentage unit."""
        return "%"


__all__ = [
    "SimpleUint8Characteristic",
    "SimpleUint16Characteristic",
    "ConcentrationCharacteristic",
    "TemperatureCharacteristic",
    "IEEE11073FloatCharacteristic",
    "PercentageCharacteristic",
]

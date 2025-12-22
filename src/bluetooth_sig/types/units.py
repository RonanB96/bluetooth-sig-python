"""Domain enums for measurement units in decoded characteristic data.

These enums provide type-safe representations of measurement choices
(e.g., Celsius vs Fahrenheit, metric vs imperial) used in decoded
characteristic return values. They enable static type checking and
IDE autocompletion for unit-aware data.

Note: These are distinct from UnitInfo in registry/uuids/units.py which
provides Bluetooth SIG metadata (UUID, name, symbol) loaded from YAML.
The symbol values here intentionally match the registry symbols for
consistency, but serve different purposes:
- Domain enums: Type hints for decoded data (e.g., `unit: PressureUnit`)
- Registry UnitInfo: UUID resolution and metadata lookup

Reference: https://www.bipm.org/en/measurement-units
"""

from __future__ import annotations

from enum import Enum


class MeasurementSystem(Enum):
    """Measurement system for body composition and weight data."""

    METRIC = "metric"
    IMPERIAL = "imperial"


class WeightUnit(Enum):
    """Units for weight/mass measurements."""

    KG = "kg"
    LB = "lb"


class HeightUnit(Enum):
    """Units for height measurements."""

    METERS = "meters"
    INCHES = "inches"


class TemperatureUnit(Enum):
    """Units for temperature measurements."""

    CELSIUS = "°C"
    FAHRENHEIT = "°F"


class GlucoseConcentrationUnit(Enum):
    """Units for glucose concentration measurements."""

    MG_DL = "mg/dL"
    MMOL_L = "mmol/L"


class PressureUnit(Enum):
    """Units for pressure measurements."""

    KPA = "kPa"
    MMHG = "mmHg"


class ElectricalUnit(Enum):
    """Units for electrical measurements."""

    VOLTS = "V"
    AMPS = "A"
    HERTZ = "Hz"
    DBM = "dBm"


class ConcentrationUnit(Enum):
    """Units for concentration measurements."""

    MICROGRAMS_PER_CUBIC_METER = "µg/m³"
    PARTS_PER_MILLION = "ppm"
    PARTS_PER_BILLION = "ppb"
    KILOGRAMS_PER_CUBIC_METER = "kg/m³"
    GRAINS_PER_CUBIC_METER = "grains/m³"


class PercentageUnit(Enum):
    """Units for percentage measurements."""

    PERCENT = "%"


class AngleUnit(Enum):
    """Units for angle measurements."""

    DEGREES = "°"


class SoundUnit(Enum):
    """Units for sound measurements."""

    DECIBELS_SPL = "dB SPL"


class LengthUnit(Enum):
    """Units for length measurements."""

    MILLIMETERS = "mm"
    METERS = "m"
    INCHES = "'"


class PhysicalUnit(Enum):
    """Units for physical measurements."""

    TESLA = "T"


class SpecialValueType(Enum):
    """Standard Bluetooth SIG special value categories.

    These represent sentinel values in characteristic data that indicate
    the measurement is not a normal reading. GSS YAML files define these
    using patterns like "value is not known" or "value is not valid".
    """

    UNKNOWN = "unknown"  # Value not known/not available (most common)
    INVALID = "invalid"  # Value not valid for current state
    OVERFLOW = "overflow"  # Value exceeds maximum representable
    UNDERFLOW = "underflow"  # Value below minimum representable
    OUT_OF_RANGE = "out_of_range"  # Sensor out of measurement range


def classify_special_value(meaning: str) -> SpecialValueType:
    """Classify a GSS meaning string into a standard category.

    Parses the human-readable meaning from GSS YAML special value definitions
    and maps it to a SpecialValueType enum.

    Args:
        meaning: Human-readable meaning from GSS (e.g., "value is not known")

    Returns:
        The appropriate SpecialValueType category.
    """
    meaning_lower = meaning.lower()

    if "not known" in meaning_lower or "unknown" in meaning_lower:
        return SpecialValueType.UNKNOWN
    if "not valid" in meaning_lower or "invalid" in meaning_lower:
        return SpecialValueType.INVALID
    if "or greater" in meaning_lower or "overflow" in meaning_lower:
        return SpecialValueType.OVERFLOW
    if "less than" in meaning_lower or "underflow" in meaning_lower:
        return SpecialValueType.UNDERFLOW
    if "out of range" in meaning_lower:
        return SpecialValueType.OUT_OF_RANGE

    # Default fallback - most special values indicate unknown
    return SpecialValueType.UNKNOWN

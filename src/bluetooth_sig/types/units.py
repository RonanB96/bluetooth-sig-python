"""Unit enumerations for measurements and data types.

Defines enums for measurement systems, weight units, height units,
temperature units, and other unit types to replace string usage with type-safe alternatives.
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

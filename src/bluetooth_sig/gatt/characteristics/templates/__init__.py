"""Coding templates for characteristic composition patterns.

This package provides reusable coding template classes that can be composed into
characteristics via dependency injection. Templates are pure coding strategies
that do NOT inherit from BaseCharacteristic.

All templates follow the CodingTemplate protocol and can be used by both SIG
and custom characteristics through composition.

Pipeline architecture:
    bytes → [Extractor] → raw_int → [Translator] → typed_value

Templates that handle single-field data expose `extractor` and `translator`
properties for pipeline access. Complex templates (multi-field, variable-length)
keep monolithic decode/encode since there's no single raw value to intercept.
"""

from .base import CodingTemplate
from .composite import TimeDataTemplate, Vector2DTemplate, VectorTemplate
from .data_structures import TimeData, Vector2DData, VectorData
from .domain import ConcentrationTemplate, PressureTemplate, TemperatureTemplate
from .enum import EnumTemplate
from .ieee_float import Float32Template, IEEE11073FloatTemplate
from .numeric import (
    Sint8Template,
    Sint16Template,
    Uint8Template,
    Uint16Template,
    Uint24Template,
    Uint32Template,
)
from .scaled import (
    PercentageTemplate,
    ScaledSint8Template,
    ScaledSint16Template,
    ScaledSint24Template,
    ScaledSint32Template,
    ScaledTemplate,
    ScaledUint8Template,
    ScaledUint16Template,
    ScaledUint24Template,
    ScaledUint32Template,
)
from .string import Utf8StringTemplate, Utf16StringTemplate

__all__ = [
    # Protocol
    "CodingTemplate",
    "ConcentrationTemplate",
    # Enum template
    "EnumTemplate",
    "Float32Template",
    "IEEE11073FloatTemplate",
    # Domain-specific templates
    "PercentageTemplate",
    "PressureTemplate",
    "ScaledSint8Template",
    "ScaledSint16Template",
    "ScaledSint24Template",
    "ScaledSint32Template",
    # Scaled templates (base + concrete)
    "ScaledTemplate",
    "ScaledUint8Template",
    "ScaledUint16Template",
    "ScaledUint24Template",
    "ScaledUint32Template",
    "Sint8Template",
    "Sint16Template",
    "TemperatureTemplate",
    "TimeData",
    "TimeDataTemplate",
    # Basic integer templates
    "Uint8Template",
    "Uint16Template",
    "Uint24Template",
    "Uint32Template",
    # String templates
    "Utf8StringTemplate",
    "Utf16StringTemplate",
    "Vector2DData",
    "Vector2DTemplate",
    # Data structures
    "VectorData",
    # Vector templates
    "VectorTemplate",
]

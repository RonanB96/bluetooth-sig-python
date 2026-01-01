"""Utility classes for GATT characteristic parsing and encoding.

This module provides organized utility classes that characteristics can
import and use as needed, maintaining logical grouping of functionality
while avoiding multiple inheritance complexity.

Pipeline components (extractors/translators) form the encode/decode pipeline:
    bytes → [Extractor] → raw_int → [Translator] → typed_value
"""

from __future__ import annotations

from .bit_field_utils import BitFieldUtils
from .data_parser import DataParser
from .data_validator import DataValidator
from .debug_utils import DebugUtils
from .extractors import (
    FLOAT32,
    SINT8,
    SINT16,
    SINT24,
    SINT32,
    UINT8,
    UINT16,
    UINT24,
    UINT32,
    Float32Extractor,
    RawExtractor,
    Sint8Extractor,
    Sint16Extractor,
    Sint24Extractor,
    Sint32Extractor,
    Uint8Extractor,
    Uint16Extractor,
    Uint24Extractor,
    Uint32Extractor,
    get_extractor,
)
from .ieee11073_parser import IEEE11073Parser
from .parse_trace import ParseTrace
from .translators import (
    FLOAT32_IEEE754,
    FLOAT32_IEEE11073,
    IDENTITY,
    PERCENTAGE,
    SFLOAT,
    Float32IEEE754Translator,
    Float32IEEETranslator,
    IdentityTranslator,
    LinearTranslator,
    PercentageTranslator,
    SfloatTranslator,
    ValueTranslator,
    create_linear_translator,
)

__all__ = [
    # Existing utilities
    "BitFieldUtils",
    "DataParser",
    "DataValidator",
    "DebugUtils",
    "IEEE11073Parser",
    "ParseTrace",
    # Extractors
    "RawExtractor",
    "Uint8Extractor",
    "Sint8Extractor",
    "Uint16Extractor",
    "Sint16Extractor",
    "Uint24Extractor",
    "Sint24Extractor",
    "Uint32Extractor",
    "Sint32Extractor",
    "Float32Extractor",
    "get_extractor",
    "UINT8",
    "SINT8",
    "UINT16",
    "SINT16",
    "UINT24",
    "SINT24",
    "UINT32",
    "SINT32",
    "FLOAT32",
    # Translators
    "ValueTranslator",
    "IdentityTranslator",
    "LinearTranslator",
    "PercentageTranslator",
    "SfloatTranslator",
    "Float32IEEETranslator",
    "Float32IEEE754Translator",
    "create_linear_translator",
    "IDENTITY",
    "PERCENTAGE",
    "SFLOAT",
    "FLOAT32_IEEE11073",
    "FLOAT32_IEEE754",
]

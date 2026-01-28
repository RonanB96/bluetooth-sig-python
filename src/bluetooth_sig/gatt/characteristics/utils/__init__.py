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
    "FLOAT32",
    "FLOAT32_IEEE754",
    "FLOAT32_IEEE11073",
    "IDENTITY",
    "PERCENTAGE",
    "SFLOAT",
    "SINT8",
    "SINT16",
    "SINT24",
    "SINT32",
    "UINT8",
    "UINT16",
    "UINT24",
    "UINT32",
    # Existing utilities
    "BitFieldUtils",
    "DataParser",
    "DataValidator",
    "DebugUtils",
    "Float32Extractor",
    "Float32IEEE754Translator",
    "Float32IEEETranslator",
    "IEEE11073Parser",
    "IdentityTranslator",
    "LinearTranslator",
    "ParseTrace",
    "PercentageTranslator",
    # Extractors
    "RawExtractor",
    "SfloatTranslator",
    "Sint8Extractor",
    "Sint16Extractor",
    "Sint24Extractor",
    "Sint32Extractor",
    "Uint8Extractor",
    "Uint16Extractor",
    "Uint24Extractor",
    "Uint32Extractor",
    # Translators
    "ValueTranslator",
    "create_linear_translator",
    "get_extractor",
]

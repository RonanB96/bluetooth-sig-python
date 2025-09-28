"""Utility classes for GATT characteristic parsing and encoding.

This module provides organized utility classes that characteristics can
import and use as needed, maintaining logical grouping of functionality
while avoiding multiple inheritance complexity.
"""

# Re-export all utilities from the utils package for backward compatibility
from .utils.bit_field_utils import BitFieldUtils
from .utils.data_parser import DataParser
from .utils.data_validator import DataValidator
from .utils.debug_utils import DebugUtils
from .utils.ieee11073_parser import IEEE11073Parser

__all__ = [
    "BitFieldUtils",
    "DataParser",
    "DataValidator",
    "DebugUtils",
    "IEEE11073Parser",
]

"""Utility classes for GATT characteristic parsing and encoding.

This module provides organized utility classes that characteristics can
import and use as needed, maintaining logical grouping of functionality
while avoiding multiple inheritance complexity.
"""

from __future__ import annotations

from .bit_field_utils import BitFieldUtils
from .data_parser import DataParser
from .data_validator import DataValidator
from .debug_utils import DebugUtils
from .ieee11073_parser import IEEE11073Parser
from .parse_trace import ParseTrace

# pylint: disable=duplicate-code
# NOTE: __all__ export list is identical to characteristics/utils.py for backwards compatibility.
# Both files export the same utility classes - this is intentional for dual import path support.
__all__ = [
    "BitFieldUtils",
    "DataParser",
    "DataValidator",
    "DebugUtils",
    "IEEE11073Parser",
    "ParseTrace",
]

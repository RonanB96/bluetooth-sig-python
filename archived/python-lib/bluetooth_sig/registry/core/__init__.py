"""Core specification registries from assigned_numbers/core/.

This module contains registries for:
- AD types (advertising data types)
- Coding formats (LE Audio codecs)
- Format types (characteristic data types)
- Namespace descriptions (CPF description field values)
- URI schemes (beacon parsing)
"""

from __future__ import annotations

from .ad_types import get_ad_types_registry
from .coding_format import get_coding_format_registry
from .formattypes import get_format_types_registry
from .namespace_description import get_namespace_description_registry
from .uri_schemes import get_uri_schemes_registry

__all__ = [
    "get_ad_types_registry",
    "get_coding_format_registry",
    "get_format_types_registry",
    "get_namespace_description_registry",
    "get_uri_schemes_registry",
]

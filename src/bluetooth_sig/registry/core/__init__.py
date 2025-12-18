"""Core specification registries from assigned_numbers/core/.

This module contains registries for:
- AD types (advertising data types)
- Coding formats (LE Audio codecs)
- Format types (characteristic data types)
- Namespace descriptions (CPF description field values)
- URI schemes (beacon parsing)
"""

from __future__ import annotations

from .ad_types import ad_types_registry
from .coding_format import coding_format_registry
from .formattypes import format_types_registry
from .namespace_description import namespace_description_registry
from .uri_schemes import uri_schemes_registry

__all__ = [
    "ad_types_registry",
    "coding_format_registry",
    "format_types_registry",
    "namespace_description_registry",
    "uri_schemes_registry",
]

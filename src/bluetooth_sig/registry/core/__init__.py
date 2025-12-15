"""Core specification registries from assigned_numbers/core/.

This module contains registries for:
- AD types (advertising data types)
- Coding formats (LE Audio codecs)
- Format types (characteristic data types)
- Namespace descriptions (CPF description field values)
- URI schemes (beacon parsing)
"""

from __future__ import annotations

from bluetooth_sig.registry.core.ad_types import ad_types_registry
from bluetooth_sig.registry.core.coding_format import coding_format_registry
from bluetooth_sig.registry.core.formattypes import format_types_registry
from bluetooth_sig.registry.core.namespace_description import namespace_description_registry
from bluetooth_sig.registry.core.uri_schemes import uri_schemes_registry

__all__ = [
    "ad_types_registry",
    "coding_format_registry",
    "format_types_registry",
    "namespace_description_registry",
    "uri_schemes_registry",
]

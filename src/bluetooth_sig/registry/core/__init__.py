"""Core specification registries from assigned_numbers/core/.

This module contains registries for:
- AD types (advertising data types)
- Appearance values (planned)
- Class of Device (CoD) (planned)
- And other core specification registries (planned)
"""

from bluetooth_sig.registry.core.ad_types import ad_types_registry

__all__ = [
    "ad_types_registry",
]

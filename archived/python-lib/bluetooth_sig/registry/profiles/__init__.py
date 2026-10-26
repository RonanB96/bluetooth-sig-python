"""Profile-specific registries from assigned_numbers/profiles_and_services/.

This module contains registries for permitted characteristics and simple
profile parameter lookup tables loaded from the Bluetooth SIG assigned
numbers YAML files.
"""

from __future__ import annotations

from .permitted_characteristics import (
    PermittedCharacteristicsRegistry,
    get_permitted_characteristics_registry,
)
from .profile_lookup import (
    ProfileLookupRegistry,
    get_profile_lookup_registry,
)

__all__ = [
    "PermittedCharacteristicsRegistry",
    "ProfileLookupRegistry",
    "get_permitted_characteristics_registry",
    "get_profile_lookup_registry",
]

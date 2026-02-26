"""Profile-specific registries from assigned_numbers/profiles_and_services/.

This module contains registries for permitted characteristics and simple
profile parameter lookup tables loaded from the Bluetooth SIG assigned
numbers YAML files.
"""

from __future__ import annotations

from .permitted_characteristics import (
    PermittedCharacteristicsRegistry,
    permitted_characteristics_registry,
)
from .profile_lookup import (
    ProfileLookupRegistry,
    profile_lookup_registry,
)

__all__ = [
    "PermittedCharacteristicsRegistry",
    "ProfileLookupRegistry",
    "permitted_characteristics_registry",
    "profile_lookup_registry",
]

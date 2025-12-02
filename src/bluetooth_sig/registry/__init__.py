"""Bluetooth SIG registries mirroring official assigned_numbers structure.

Structure mirrors bluetooth_sig/assigned_numbers/:
- core/ - Core specification registries (AD types, appearance, CoD, etc.)
- company_identifiers/ - Manufacturer company IDs
- uuids/ - All UUID-based registries (services, characteristics, protocols, etc.)
- service_discovery/ - SDP attribute IDs
- profiles/ - Profile-specific registries
"""

from bluetooth_sig.registry.base import BaseUUIDRegistry

__all__ = [
    "BaseUUIDRegistry",
]

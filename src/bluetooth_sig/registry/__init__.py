"""Bluetooth SIG registries mirroring official assigned_numbers structure.

Structure mirrors bluetooth_sig/assigned_numbers/:
- core/ - Core specification registries (AD types, appearance, CoD, etc.)
- company_identifiers/ - Manufacturer company IDs
- uuids/ - All UUID-based registries (services, characteristics, protocols, etc.)
- service_discovery/ - SDP attribute IDs
- profiles/ - Profile-specific registries

All existing registries are re-exported from this module for backward compatibility.
"""

from bluetooth_sig.registry.base import BaseRegistry

# Core registries (from assigned_numbers/core/)
from bluetooth_sig.registry.core import ad_types_registry
from bluetooth_sig.registry.core.appearance_values import appearance_values_registry
from bluetooth_sig.registry.core.class_of_device import class_of_device_registry

# UUID registries (from assigned_numbers/uuids/)
from bluetooth_sig.registry.uuids.browse_groups import browse_groups_registry
from bluetooth_sig.registry.uuids.declarations import declarations_registry
from bluetooth_sig.registry.uuids.members import members_registry
from bluetooth_sig.registry.uuids.mesh_profiles import mesh_profiles_registry
from bluetooth_sig.registry.uuids.object_types import object_types_registry
from bluetooth_sig.registry.uuids.sdo_uuids import sdo_uuids_registry
from bluetooth_sig.registry.uuids.service_classes import service_classes_registry
from bluetooth_sig.registry.uuids.units import units_registry

__all__ = [
    "BaseRegistry",
    # Core registries
    "ad_types_registry",
    "appearance_values_registry",
    "class_of_device_registry",
    # UUID registries
    "browse_groups_registry",
    "declarations_registry",
    "members_registry",
    "mesh_profiles_registry",
    "object_types_registry",
    "sdo_uuids_registry",
    "service_classes_registry",
    "units_registry",
]

"""UUID-based registries from assigned_numbers/uuids/."""

from bluetooth_sig.registry.uuids.browse_groups import browse_groups_registry
from bluetooth_sig.registry.uuids.declarations import declarations_registry
from bluetooth_sig.registry.uuids.members import members_registry
from bluetooth_sig.registry.uuids.mesh_profiles import mesh_profiles_registry
from bluetooth_sig.registry.uuids.object_types import object_types_registry
from bluetooth_sig.registry.uuids.sdo_uuids import sdo_uuids_registry
from bluetooth_sig.registry.uuids.service_classes import service_classes_registry
from bluetooth_sig.registry.uuids.units import units_registry

__all__ = [
    "browse_groups_registry",
    "declarations_registry",
    "members_registry",
    "mesh_profiles_registry",
    "object_types_registry",
    "sdo_uuids_registry",
    "service_classes_registry",
    "units_registry",
]

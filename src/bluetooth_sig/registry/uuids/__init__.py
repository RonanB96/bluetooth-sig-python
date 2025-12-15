"""UUID-based registries from assigned_numbers/uuids/."""

from __future__ import annotations

from .browse_groups import browse_groups_registry
from .declarations import declarations_registry
from .members import members_registry
from .mesh_profiles import mesh_profiles_registry
from .object_types import object_types_registry
from .protocol_identifiers import protocol_identifiers_registry
from .sdo_uuids import sdo_uuids_registry
from .service_classes import service_classes_registry
from .units import units_registry

__all__ = [
    "browse_groups_registry",
    "declarations_registry",
    "members_registry",
    "mesh_profiles_registry",
    "object_types_registry",
    "protocol_identifiers_registry",
    "sdo_uuids_registry",
    "service_classes_registry",
    "units_registry",
]

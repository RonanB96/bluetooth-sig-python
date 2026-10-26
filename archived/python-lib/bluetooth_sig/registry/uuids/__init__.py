"""UUID-based registries from assigned_numbers/uuids/."""

from __future__ import annotations

from .browse_groups import get_browse_groups_registry
from .declarations import get_declarations_registry
from .members import get_members_registry
from .mesh_profiles import get_mesh_profiles_registry
from .object_types import get_object_types_registry
from .protocol_identifiers import get_protocol_identifiers_registry
from .sdo_uuids import get_sdo_uuids_registry
from .service_classes import get_service_classes_registry
from .units import get_units_registry

__all__ = [
    "get_browse_groups_registry",
    "get_declarations_registry",
    "get_members_registry",
    "get_mesh_profiles_registry",
    "get_object_types_registry",
    "get_protocol_identifiers_registry",
    "get_sdo_uuids_registry",
    "get_service_classes_registry",
    "get_units_registry",
]

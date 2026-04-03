"""Registry pre-warming for eager YAML loading.

Consumers that run inside an event loop (e.g. Home Assistant) should call
:func:`prewarm_registries` in an executor thread during setup to avoid
blocking I/O on first access.
"""

from __future__ import annotations

import logging

from ..gatt.characteristics.registry import CharacteristicRegistry
from ..gatt.services.registry import GattServiceRegistry
from ..registry.company_identifiers import company_identifiers_registry
from ..registry.core.ad_types import ad_types_registry
from ..registry.core.appearance_values import appearance_values_registry
from ..registry.core.class_of_device import class_of_device_registry
from ..registry.core.coding_format import coding_format_registry
from ..registry.core.formattypes import format_types_registry
from ..registry.core.namespace_description import namespace_description_registry
from ..registry.core.uri_schemes import uri_schemes_registry
from ..registry.profiles.permitted_characteristics import permitted_characteristics_registry
from ..registry.profiles.profile_lookup import profile_lookup_registry
from ..registry.service_discovery.attribute_ids import service_discovery_attribute_registry
from ..registry.uuids.browse_groups import browse_groups_registry
from ..registry.uuids.declarations import declarations_registry
from ..registry.uuids.members import members_registry
from ..registry.uuids.mesh_profiles import mesh_profiles_registry
from ..registry.uuids.object_types import object_types_registry
from ..registry.uuids.protocol_identifiers import protocol_identifiers_registry
from ..registry.uuids.sdo_uuids import sdo_uuids_registry
from ..registry.uuids.service_classes import service_classes_registry
from ..registry.uuids.units import units_registry
from ..types.uuid import BluetoothUUID

logger = logging.getLogger(__name__)


def prewarm_registries() -> None:
    """Eagerly load all bluetooth-sig YAML registries.

    Triggers the lazy-load path for every registry so that subsequent
    lookups are lock-free and allocation-free.  This function performs
    synchronous file I/O and should be called from an executor thread
    when used inside an async framework.

    Covers:
    - Characteristic registry (all characteristic classes)
    - Service registry (all service classes)
    - Units registry (unit UUID → symbol mapping)
    - Company identifiers registry (manufacturer ID → name)
    - AD types registry (advertising data type codes)
    - Appearance values registry (appearance code → device type)
    - Class of device registry (CoD bitfield → device type)
    - Coding format registry (LE Audio codec identifiers)
    - Format types registry (characteristic data format codes)
    - Namespace description registry (CPF description field values)
    - URI schemes registry (beacon URI scheme codes)
    - Permitted characteristics registry (profile characteristic constraints)
    - Profile lookup registry (profile parameter tables)
    - Service discovery attribute registry (SDP attribute identifiers)
    - Browse groups registry (SDP browse group UUIDs)
    - Declarations registry (GATT declaration UUIDs)
    - Members registry (Bluetooth member organisation UUIDs)
    - Mesh profiles registry (mesh profile UUIDs)
    - Object types registry (OTS object type UUIDs)
    - Protocol identifiers registry (protocol UUID identifiers)
    - SDO UUIDs registry (standards body UUIDs)
    - Service classes registry (service class UUIDs)
    """
    CharacteristicRegistry.get_all_characteristics()
    GattServiceRegistry.get_all_services()

    # Trigger UUID-keyed lookups to populate reverse maps.
    GattServiceRegistry.get_service_class_by_uuid(BluetoothUUID("0000"))
    CharacteristicRegistry.get_characteristic_class_by_uuid(BluetoothUUID("0000"))

    units_registry.ensure_loaded()
    company_identifiers_registry.ensure_loaded()
    ad_types_registry.ensure_loaded()
    appearance_values_registry.ensure_loaded()
    class_of_device_registry.ensure_loaded()
    coding_format_registry.ensure_loaded()
    format_types_registry.ensure_loaded()
    namespace_description_registry.ensure_loaded()
    uri_schemes_registry.ensure_loaded()
    permitted_characteristics_registry.ensure_loaded()
    profile_lookup_registry.ensure_loaded()
    service_discovery_attribute_registry.ensure_loaded()
    browse_groups_registry.ensure_loaded()
    declarations_registry.ensure_loaded()
    members_registry.ensure_loaded()
    mesh_profiles_registry.ensure_loaded()
    object_types_registry.ensure_loaded()
    protocol_identifiers_registry.ensure_loaded()
    sdo_uuids_registry.ensure_loaded()
    service_classes_registry.ensure_loaded()

    logger.debug("bluetooth-sig registries pre-warmed")

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
    """
    CharacteristicRegistry.get_all_characteristics()
    GattServiceRegistry.get_all_services()

    # Trigger UUID-keyed lookups to populate reverse maps.
    GattServiceRegistry.get_service_class_by_uuid(BluetoothUUID("0000"))
    CharacteristicRegistry.get_characteristic_class_by_uuid(BluetoothUUID("0000"))

    units_registry.ensure_loaded()
    company_identifiers_registry.ensure_loaded()
    ad_types_registry.ensure_loaded()

    logger.debug("bluetooth-sig registries pre-warmed")

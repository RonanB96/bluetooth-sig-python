"""Registry pre-warming for eager YAML loading.

Consumers that run inside an event loop (e.g. Home Assistant) should call
:func:`prewarm_registries` in an executor thread during setup to avoid
blocking I/O on first access.
"""

from __future__ import annotations

import logging

from .prewarm_catalog import get_prewarm_loaders

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
    - UUID registry (service/characteristic/descriptor metadata hub)
    """
    for loader_name, loader in get_prewarm_loaders():
        loader()
        logger.debug("pre-warmed %s", loader_name)

    logger.debug("bluetooth-sig registries pre-warmed")

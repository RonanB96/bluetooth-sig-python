"""Registry for advertising data interpreter routing."""

from __future__ import annotations

import logging
from typing import Any

from bluetooth_sig.advertising.base import AdvertisingDataInterpreter, DataSource
from bluetooth_sig.types.uuid import BluetoothUUID

logger = logging.getLogger(__name__)


class AdvertisingInterpreterRegistry:
    """Routes advertisements to interpreter classes.

    Does NOT manage interpreter instances - Device owns those.
    Only handles class registration and lookup.
    """

    def __init__(self) -> None:
        """Initialise empty registry."""
        self._manufacturer_interpreters: dict[int, list[type[AdvertisingDataInterpreter[Any]]]] = {}
        self._service_interpreters: dict[str, list[type[AdvertisingDataInterpreter[Any]]]] = {}
        self._fallback_interpreters: list[type[AdvertisingDataInterpreter[Any]]] = []

    def register(self, interpreter_class: type[AdvertisingDataInterpreter[Any]]) -> None:
        """Register an interpreter class (called by AdvertisingDataInterpreter.__init_subclass__)."""
        if not hasattr(interpreter_class, "_info"):
            logger.warning("Interpreter %s has no _info, skipping", interpreter_class.__name__)
            return

        info = interpreter_class._info  # pylint: disable=protected-access

        if info.data_source == DataSource.MANUFACTURER and info.company_id is not None:
            if info.company_id not in self._manufacturer_interpreters:
                self._manufacturer_interpreters[info.company_id] = []
            self._manufacturer_interpreters[info.company_id].append(interpreter_class)
            logger.debug("Registered %s for company 0x%04X", interpreter_class.__name__, info.company_id)

        elif info.data_source == DataSource.SERVICE and info.service_uuid is not None:
            uuid_key = str(info.service_uuid).upper()
            if uuid_key not in self._service_interpreters:
                self._service_interpreters[uuid_key] = []
            self._service_interpreters[uuid_key].append(interpreter_class)
            logger.debug("Registered %s for UUID %s", interpreter_class.__name__, uuid_key)

        else:
            self._fallback_interpreters.append(interpreter_class)
            logger.debug("Registered fallback interpreter %s", interpreter_class.__name__)

    def unregister(self, interpreter_class: type[AdvertisingDataInterpreter[Any]]) -> None:
        """Unregister an interpreter class."""
        if not hasattr(interpreter_class, "_info"):
            return

        info = interpreter_class._info  # pylint: disable=protected-access

        if info.data_source == DataSource.MANUFACTURER and info.company_id is not None:
            if info.company_id in self._manufacturer_interpreters:
                self._manufacturer_interpreters[info.company_id] = [
                    p for p in self._manufacturer_interpreters[info.company_id] if p is not interpreter_class
                ]

        elif info.data_source == DataSource.SERVICE and info.service_uuid is not None:
            uuid_key = str(info.service_uuid).upper()
            if uuid_key in self._service_interpreters:
                self._service_interpreters[uuid_key] = [
                    p for p in self._service_interpreters[uuid_key] if p is not interpreter_class
                ]

        if interpreter_class in self._fallback_interpreters:
            self._fallback_interpreters.remove(interpreter_class)

    def find_interpreter_class(
        self,
        manufacturer_data: dict[int, bytes],
        service_data: dict[BluetoothUUID, bytes],
        local_name: str | None,
    ) -> type[AdvertisingDataInterpreter[Any]] | None:
        """Find first interpreter class that handles this advertisement."""
        candidates: list[type[AdvertisingDataInterpreter[Any]]] = []

        for company_id in manufacturer_data:
            if company_id in self._manufacturer_interpreters:
                candidates.extend(self._manufacturer_interpreters[company_id])

        for service_uuid in service_data:
            uuid_key = str(service_uuid).upper()
            if uuid_key in self._service_interpreters:
                candidates.extend(self._service_interpreters[uuid_key])

        candidates.extend(self._fallback_interpreters)

        for interpreter_class in candidates:
            if interpreter_class.supports(manufacturer_data, service_data, local_name):
                return interpreter_class

        return None

    def find_all_interpreter_classes(
        self,
        manufacturer_data: dict[int, bytes],
        service_data: dict[BluetoothUUID, bytes],
        local_name: str | None,
    ) -> list[type[AdvertisingDataInterpreter[Any]]]:
        """Find all interpreter classes that handle this advertisement."""
        candidates: list[type[AdvertisingDataInterpreter[Any]]] = []

        for company_id in manufacturer_data:
            if company_id in self._manufacturer_interpreters:
                candidates.extend(self._manufacturer_interpreters[company_id])

        for service_uuid in service_data:
            uuid_key = str(service_uuid).upper()
            if uuid_key in self._service_interpreters:
                candidates.extend(self._service_interpreters[uuid_key])

        candidates.extend(self._fallback_interpreters)

        return [ic for ic in candidates if ic.supports(manufacturer_data, service_data, local_name)]

    def get_registered_interpreters(self) -> list[type[AdvertisingDataInterpreter[Any]]]:
        """Get all registered interpreter classes."""
        all_interpreters: list[type[AdvertisingDataInterpreter[Any]]] = []
        for interpreters in self._manufacturer_interpreters.values():
            all_interpreters.extend(interpreters)
        for interpreters in self._service_interpreters.values():
            all_interpreters.extend(interpreters)
        all_interpreters.extend(self._fallback_interpreters)
        return list(set(all_interpreters))

    def clear(self) -> None:
        """Clear all registered interpreters."""
        self._manufacturer_interpreters.clear()
        self._service_interpreters.clear()
        self._fallback_interpreters.clear()


# Global singleton for class registration
advertising_interpreter_registry = AdvertisingInterpreterRegistry()

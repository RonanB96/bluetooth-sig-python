"""Registry for advertising data interpreter routing."""

from __future__ import annotations

import logging
from typing import Any

import msgspec

from bluetooth_sig.advertising.base import (
    AdvertisingData,
    DataSource,
    PayloadInterpreter,
)
from bluetooth_sig.advertising.state import DeviceAdvertisingState
from bluetooth_sig.types.company import ManufacturerData
from bluetooth_sig.types.uuid import BluetoothUUID


class PayloadContext(msgspec.Struct, kw_only=True, frozen=True):
    """Context information for payload interpretation."""

    mac_address: str
    rssi: int | None = None
    timestamp: float | None = None


logger = logging.getLogger(__name__)


class PayloadInterpreterRegistry:
    """Routes advertisements to PayloadInterpreter classes.

    Does NOT manage interpreter instances or state - caller owns those.
    Only handles class registration and lookup.

    Attributes:
        _by_service_uuid: Interpreters indexed by service UUID.
        _by_company_id: Interpreters indexed by company ID.
        _fallback: Interpreters that match by custom logic only.

    """

    def __init__(self) -> None:
        """Initialise empty registry."""
        self._by_service_uuid: dict[str, list[type[PayloadInterpreter[Any]]]] = {}
        self._by_company_id: dict[int, list[type[PayloadInterpreter[Any]]]] = {}
        self._fallback: list[type[PayloadInterpreter[Any]]] = []

    def register(self, interpreter_class: type[PayloadInterpreter[Any]]) -> None:
        """Register an interpreter class.

        Called automatically by PayloadInterpreter.__init_subclass__.

        Args:
            interpreter_class: The interpreter class to register.

        """
        if not hasattr(interpreter_class, "_info"):
            logger.warning("Interpreter %s has no _info, skipping", interpreter_class.__name__)
            return

        info = interpreter_class._info  # pylint: disable=protected-access

        if info.data_source == DataSource.MANUFACTURER and info.company_id is not None:
            if info.company_id not in self._by_company_id:
                self._by_company_id[info.company_id] = []
            self._by_company_id[info.company_id].append(interpreter_class)
            logger.debug("Registered %s for company 0x%04X", interpreter_class.__name__, info.company_id)

        elif info.data_source == DataSource.SERVICE and info.service_uuid is not None:
            uuid_key = str(info.service_uuid).upper()
            if uuid_key not in self._by_service_uuid:
                self._by_service_uuid[uuid_key] = []
            self._by_service_uuid[uuid_key].append(interpreter_class)
            logger.debug("Registered %s for UUID %s", interpreter_class.__name__, uuid_key)

        else:
            self._fallback.append(interpreter_class)
            logger.debug("Registered fallback interpreter %s", interpreter_class.__name__)

    def unregister(self, interpreter_class: type[PayloadInterpreter[Any]]) -> None:
        """Unregister an interpreter class.

        Args:
            interpreter_class: The interpreter class to unregister.

        """
        if not hasattr(interpreter_class, "_info"):
            return

        info = interpreter_class._info  # pylint: disable=protected-access

        if info.data_source == DataSource.MANUFACTURER and info.company_id is not None:
            if info.company_id in self._by_company_id:
                self._by_company_id[info.company_id] = [
                    p for p in self._by_company_id[info.company_id] if p is not interpreter_class
                ]

        elif info.data_source == DataSource.SERVICE and info.service_uuid is not None:
            uuid_key = str(info.service_uuid).upper()
            if uuid_key in self._by_service_uuid:
                self._by_service_uuid[uuid_key] = [
                    p for p in self._by_service_uuid[uuid_key] if p is not interpreter_class
                ]

        if interpreter_class in self._fallback:
            self._fallback.remove(interpreter_class)

    def find_interpreter_class(self, advertising_data: AdvertisingData) -> type[PayloadInterpreter[Any]] | None:
        """Find first interpreter class that handles this advertisement.

        Args:
            advertising_data: Complete advertising data from BLE packet.

        Returns:
            First matching interpreter class, or None if no match.

        """
        candidates: list[type[PayloadInterpreter[Any]]] = []

        for company_id in advertising_data.manufacturer_data:
            if company_id in self._by_company_id:
                candidates.extend(self._by_company_id[company_id])

        for service_uuid in advertising_data.service_data:
            uuid_key = str(service_uuid).upper()
            if uuid_key in self._by_service_uuid:
                candidates.extend(self._by_service_uuid[uuid_key])

        candidates.extend(self._fallback)

        for interpreter_class in candidates:
            if interpreter_class.supports(advertising_data):
                return interpreter_class

        return None

    def find_all_interpreter_classes(self, advertising_data: AdvertisingData) -> list[type[PayloadInterpreter[Any]]]:
        """Find all interpreter classes that handle this advertisement.

        Useful when multiple protocols coexist in one advertisement
        (e.g., BTHome + Xiaomi UUIDs).

        Args:
            advertising_data: Complete advertising data from BLE packet.

        Returns:
            List of all matching interpreter classes.

        """
        candidates: list[type[PayloadInterpreter[Any]]] = []

        for company_id in advertising_data.manufacturer_data:
            if company_id in self._by_company_id:
                candidates.extend(self._by_company_id[company_id])

        for service_uuid in advertising_data.service_data:
            uuid_key = str(service_uuid).upper()
            if uuid_key in self._by_service_uuid:
                candidates.extend(self._by_service_uuid[uuid_key])

        candidates.extend(self._fallback)

        return [ic for ic in candidates if ic.supports(advertising_data)]

    def get_registered_interpreters(self) -> list[type[PayloadInterpreter[Any]]]:
        """Get all registered interpreter classes.

        Returns:
            List of all registered interpreter classes (deduplicated).

        """
        all_interpreters: list[type[PayloadInterpreter[Any]]] = []
        for interpreters in self._by_company_id.values():
            all_interpreters.extend(interpreters)
        for interpreters in self._by_service_uuid.values():
            all_interpreters.extend(interpreters)
        all_interpreters.extend(self._fallback)
        return list(set(all_interpreters))

    def clear(self) -> None:
        """Clear all registered interpreters."""
        self._by_company_id.clear()
        self._by_service_uuid.clear()
        self._fallback.clear()


# Global singleton for PayloadInterpreter registration
payload_interpreter_registry = PayloadInterpreterRegistry()


def parse_advertising_payloads(
    manufacturer_data: dict[int, bytes],
    service_data: dict[BluetoothUUID, bytes],
    context: PayloadContext,
    state: DeviceAdvertisingState | None = None,
    *,
    registry: PayloadInterpreterRegistry | None = None,
) -> list[Any]:
    """Auto-discover and parse all payloads in an advertisement.

    This is the high-level "just parse everything" API.
    Finds all matching interpreters and parses their payloads.

    Args:
        manufacturer_data: Company ID → payload bytes mapping.
        service_data: Service UUID → payload bytes mapping.
        context: Advertisement context (MAC address, RSSI, timestamp).
        state: Current device advertising state (optional, created if None).
        registry: Interpreter registry to use (defaults to global registry).

    Returns:
        List of parsed data from all matching interpreters.
        Failed interpretations are silently skipped (exceptions logged).

    Example::
        from bluetooth_sig.advertising import parse_advertising_payloads, PayloadContext

        context = PayloadContext(mac_address="AA:BB:CC:DD:EE:FF", rssi=-60)
        results = parse_advertising_payloads(
            manufacturer_data={0x038F: xiaomi_bytes},
            service_data={BTHOME_UUID: bthome_bytes},
            context=context,
        )

        for data in results:
            print(f"Parsed {data}")

    """
    results: list[Any] = []

    # Use global registry if none provided
    if registry is None:
        registry = payload_interpreter_registry

    # Create state if not provided
    if state is None:
        state = DeviceAdvertisingState(address=context.mac_address)

    mfr_data_dict: dict[int, ManufacturerData] = {}
    for company_id, payload in manufacturer_data.items():
        mfr_data_dict[company_id] = ManufacturerData.from_id_and_payload(company_id, payload)

    # Build AdvertisingData struct
    ad_data = AdvertisingData(
        manufacturer_data=mfr_data_dict,
        service_data=service_data,
        local_name=None,
        rssi=context.rssi,
        timestamp=context.timestamp,
    )

    # Find all matching interpreters
    interpreter_classes = registry.find_all_interpreter_classes(ad_data)

    if not interpreter_classes:
        # No interpreters found - return empty list
        return results

    # Run each interpreter
    for interpreter_class in interpreter_classes:
        try:
            interpreter = interpreter_class(context.mac_address)
            data = interpreter.interpret(ad_data, state)
            results.append(data)
        except Exception:  # pylint: disable=broad-exception-caught  # Catch all interpreter errors
            # Log and continue to next interpreter
            logger.debug("Interpreter %s failed", interpreter_class.__name__, exc_info=True)

    return results

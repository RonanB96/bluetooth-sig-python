#!/usr/bin/env python3
"""SimplePyBLE integration utilities for BLE examples.

This module provides SimplePyBLE-specific BLE connection and
characteristic reading functions.
"""

from __future__ import annotations

import asyncio
import types
from typing import TYPE_CHECKING, Any

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics.base import CharacteristicData
from examples.utils.models import DeviceInfo

if TYPE_CHECKING:
    from examples.connection_managers.simpleble import SimplePyBLEConnectionManager
else:
    try:
        from examples.connection_managers.simpleble import SimplePyBLEConnectionManager
    except ImportError:
        SimplePyBLEConnectionManager = None  # type: ignore[misc,assignment]


def scan_devices_simpleble(  # pylint: disable=duplicate-code
    simpleble_module: types.ModuleType, timeout: float = 10.0
) -> list[DeviceInfo]:
    # NOTE: Device listing pattern duplicates bleak_retry_integration scan display logic.
    # Duplication justified because:
    # 1. SimplePyBLE API differs from Bleak (different method names, synchronous)
    # 2. Example code prioritizes readability over DRY for learning purposes
    # 3. Consolidation would require abstract device wrapper, over-engineering for examples
    """Scan for BLE devices using SimplePyBLE utilities."""
    # NOTE: SimplePyBLE exposes dynamic attributes; stubs provide type safety
    adapters = simpleble_module.Adapter.get_adapters()  # pylint: disable=no-member
    if not adapters:
        return []

    adapter = adapters[0]
    adapter.scan_for(int(timeout * 1000))

    devices: list[DeviceInfo] = []
    for peripheral in adapter.scan_get_results():
        info = DeviceInfo(
            name=peripheral.identifier(),
            address=peripheral.address(),
            rssi=peripheral.rssi(),
            raw=peripheral,
        )
        devices.append(info)

    return devices


class SimpleCharacteristic:
    """Simple characteristic object compatible with Device class expectations.

    Lightweight container used by example code to represent characteristic
    metadata for SimplePyBLE adapters.
    """

    def __init__(self, uuid: str, properties: list[str] | None = None) -> None:
        """Create a lightweight characteristic representation for examples.

        Args:
            uuid: The characteristic UUID as a string.
            properties: Optional list of property names (e.g. ['read', 'notify']).

        """
        self.uuid = uuid
        self.properties = properties or []


class SimpleService:
    """Simple service object compatible with Device class expectations.

    Lightweight container used by example code to represent service
    metadata for SimplePyBLE adapters.
    """

    def __init__(self, uuid: str, characteristics: list[SimpleCharacteristic] | None = None) -> None:
        """Create a lightweight service representation for examples.

        Args:
            uuid: The service UUID as a string.
            characteristics: Optional list of SimpleCharacteristic instances.

        """
        self.uuid = uuid
        self.characteristics = characteristics or []


def comprehensive_device_analysis_simpleble(  # pylint: disable=too-many-locals,duplicate-code
    address: str,
    simpleble_module: types.ModuleType,
) -> dict[str, CharacteristicData[Any]]:
    # NOTE: Result parsing pattern duplicates shared_utils and data_parsing display logic.
    # Duplication justified because:
    # 1. SimplePyBLE is synchronous, shared utils are async (different execution models)
    # 2. This returns CharacteristicData objects, shared utils return dicts (different types)
    # 3. Example code prioritizes clarity over abstraction for educational purposes
    """Analyze a BLE device using SimplePyBLE (synchronous).

    Args:
        address: Device address
        simpleble_module: The imported simplepyble module

    Returns:
        Mapping of short UUIDs to characteristic parse data

    """
    if SimplePyBLEConnectionManager is None:
        raise ImportError("SimplePyBLE not available")

    # Reuse the canonical connection helper to read characteristics
    # and then parse the results using the BluetoothSIGTranslator.
    translator = BluetoothSIGTranslator()

    async def _collect() -> dict[str, CharacteristicData[Any]]:
        manager = SimplePyBLEConnectionManager(address, timeout=10.0)
        try:
            await manager.connect()
        except Exception as e:  # pylint: disable=broad-exception-caught
            raise RuntimeError(f"Failed to connect to {address}: {e}") from e

        try:
            services = await manager.get_services()

            # Discover readable characteristics
            target_uuids: list[str] = []
            for service in services:  # type: ignore
                for char in getattr(service, "characteristics", []):
                    # If characteristic object exposes properties, check for 'read'
                    props = getattr(char, "properties", None)
                    if isinstance(props, (list, tuple)) and "read" in props:
                        target_uuids.append(str(char.uuid))

            # Delegate reading to canonical helper
            from examples.utils.connection_helpers import read_characteristics_with_manager

            read_results = await read_characteristics_with_manager(manager, target_uuids)

            parsed: dict[str, CharacteristicData[Any]] = {}
            for short_uuid, read_result in read_results.items():
                try:
                    parsed_outcome = translator.parse_characteristic(short_uuid, read_result.raw_data)
                    parsed[short_uuid] = parsed_outcome
                except Exception:  # pylint: disable=broad-exception-caught
                    # Skip failed parses but continue processing
                    continue

            return parsed
        finally:
            try:
                await manager.disconnect()
            except Exception:
                pass

    return asyncio.run(_collect())

"""Bless-based peripheral manager for bluetooth-sig-python.

This module provides a bless backend implementation for creating BLE GATT
servers that broadcast user-defined services and characteristics.

This file intentionally imports the optional bless module at import time
so that attempting to import this module when the backend is not installed
fails fast and provides a clear diagnostic.

Note:
    On Linux, BlueZ may expose additional system-level services (Audio, Media,
    Handsfree, A/V Remote Control, etc.) alongside your custom GATT services.
    These are system profiles registered by BlueZ plugins and cannot be removed
    from Python. To disable them, modify /etc/bluetooth/main.conf:

        [General]
        DisablePlugins = audio,media,a2dp,avrcp,hfp,hsp

    Then restart the bluetooth service. This is a BlueZ limitation, not a
    limitation of bless or this library.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, ClassVar

from bless import (  # type: ignore[import-not-found,import-untyped,attr-defined]
    BlessGATTCharacteristic,
    BlessServer,
    GATTAttributePermissions,
    GATTCharacteristicProperties,
)
from bless.backends.advertisement import BlessAdvertisementData  # type: ignore[import-not-found]

from bluetooth_sig.device.peripheral import PeripheralManagerProtocol
from bluetooth_sig.types.gatt_enums import GattProperty
from bluetooth_sig.types.uuid import BluetoothUUID

logger = logging.getLogger(__name__)


def _gatt_property_to_bless(properties: GattProperty) -> GATTCharacteristicProperties:
    """Convert bluetooth-sig GattProperty flags to bless GATTCharacteristicProperties."""
    result = GATTCharacteristicProperties(0)

    if properties & GattProperty.READ:
        result |= GATTCharacteristicProperties.read
    if properties & GattProperty.WRITE:
        result |= GATTCharacteristicProperties.write
    if properties & GattProperty.WRITE_WITHOUT_RESPONSE:
        result |= GATTCharacteristicProperties.write_without_response
    if properties & GattProperty.NOTIFY:
        result |= GATTCharacteristicProperties.notify
    if properties & GattProperty.INDICATE:
        result |= GATTCharacteristicProperties.indicate

    return result


def _gatt_property_to_permissions(properties: GattProperty) -> GATTAttributePermissions:
    """Convert bluetooth-sig GattProperty flags to bless GATTAttributePermissions."""
    result = GATTAttributePermissions(0)

    if properties & GattProperty.READ:
        result |= GATTAttributePermissions.readable
    if properties & (GattProperty.WRITE | GattProperty.WRITE_WITHOUT_RESPONSE):
        result |= GATTAttributePermissions.writable

    return result


class BlessPeripheralManager(PeripheralManagerProtocol):
    """Peripheral manager using bless for cross-platform BLE GATT servers.

    This implementation wraps the bless library to provide a consistent
    interface for creating BLE peripherals across macOS, Linux, and Windows.
    """

    supports_advertising: ClassVar[bool] = True

    def __init__(
        self,
        name: str,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        """Initialize the bless peripheral manager.

        Args:
            name: The advertised device name.
            loop: Optional event loop. If None, uses the running loop.

        """
        super().__init__(name)
        self._loop = loop
        self._server: BlessServer | None = None
        self._is_advertising = False

    # -------------------------------------------------------------------------
    # Internal Helpers (Bless-specific)
    # -------------------------------------------------------------------------

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        """Get the event loop to use."""
        if self._loop is not None:
            return self._loop
        return asyncio.get_running_loop()

    def _on_read(
        self,
        characteristic: BlessGATTCharacteristic,
        request: Any = None,  # noqa: ANN401
    ) -> bytearray:
        """Handle read requests from clients.

        Args:
            characteristic: The GATT characteristic being read
            request: The BlessGATTRequest object (backend-specific)

        """
        del request  # Unused but required by bless callback signature
        char_uuid = str(characteristic.uuid).upper()
        logger.debug("Read request for %s", char_uuid)

        # Check for dynamic read callback
        if char_uuid in self._read_callbacks:
            value = self._read_callbacks[char_uuid]()
            characteristic.value = value
            logger.debug("Returning dynamic value for %s: %r", char_uuid, bytes(value))
            return value

        # Return stored value
        value = characteristic.value if characteristic.value else bytearray()
        logger.debug("Returning stored value for %s: %r (%d bytes)", char_uuid, bytes(value), len(value))
        return value

    def _on_write(
        self,
        characteristic: BlessGATTCharacteristic,
        value: Any,  # noqa: ANN401
        request: Any = None,  # noqa: ANN401
    ) -> None:
        """Handle write requests from clients.

        Args:
            characteristic: The GATT characteristic being written
            value: The value being written
            request: The BlessGATTRequest object (backend-specific)

        """
        del request  # Unused but required by bless callback signature
        char_uuid = str(characteristic.uuid).upper()
        logger.debug("Write request for %s: %r", char_uuid, value)

        # Store the value
        if isinstance(value, (bytes, bytearray)):
            characteristic.value = bytearray(value)
        else:
            characteristic.value = bytearray(value)

        # Invoke write callback if registered
        if char_uuid in self._write_callbacks:
            self._write_callbacks[char_uuid](characteristic.value)

    # -------------------------------------------------------------------------
    # Abstract Method Implementations (Bless-specific)
    # -------------------------------------------------------------------------

    @property
    def is_advertising(self) -> bool:
        """Check if the peripheral is currently advertising."""
        return self._is_advertising

    async def start(self) -> None:
        """Start advertising and accepting connections.

        Raises:
            RuntimeError: If no services have been added

        """
        if not self._services:
            raise RuntimeError("No services added. Call add_service() first.")

        if self._is_advertising:
            logger.warning("Peripheral is already advertising")
            return

        loop = self._get_loop()

        # Create the bless server
        self._server = BlessServer(
            name=self._name,
            loop=loop,
        )
        # Set read/write callbacks using the bless API
        # Type ignores needed due to bless backend type signature inconsistencies
        self._server.read_request_func = self._on_read  # type: ignore[assignment]
        self._server.write_request_func = self._on_write  # type: ignore[assignment]

        # Build GATT tree from our service definitions
        gatt: dict[str, dict[str, dict[str, Any]]] = {}

        for service in self._services:
            # Use BluetoothUUID to get full 128-bit format
            service_uuid = str(BluetoothUUID(service.uuid))
            gatt[service_uuid] = {}

            for char_def in service.characteristics:
                char_uuid = str(BluetoothUUID(char_def.uuid))

                # Use bytearray for bless compatibility (not bytes)
                initial_value: bytearray | None = None
                if char_def.initial_value is not None and len(char_def.initial_value) > 0:
                    initial_value = bytearray(char_def.initial_value)

                gatt[service_uuid][char_uuid] = {
                    "Properties": _gatt_property_to_bless(char_def.properties),
                    "Permissions": _gatt_property_to_permissions(char_def.properties),
                    "Value": initial_value,
                }

                logger.debug(
                    "Registered char %s with initial value: %r (%d bytes)",
                    char_uuid,
                    initial_value,
                    len(initial_value) if initial_value else 0,
                )

        # Add the GATT tree and start
        await self._server.add_gatt(gatt)

        # Build advertisement data for bless
        # Bless uses BlessAdvertisementData which BlueZ encodes per-platform
        service_uuid_list = [str(BluetoothUUID(s.uuid)) for s in self._services]

        # Convert service_data keys to strings for bless API
        service_data_for_bless: dict[str, bytes] | None = None
        if self._service_data:
            service_data_for_bless = {str(uuid): data for uuid, data in self._service_data.items()}

        advertisement_data = BlessAdvertisementData(
            local_name=self._name,
            service_uuids=service_uuid_list,
            manufacturer_data=(
                {self._manufacturer_data.company.id: self._manufacturer_data.payload}
                if self._manufacturer_data
                else None
            ),
            service_data=service_data_for_bless,
            is_connectable=self._is_connectable,
            is_discoverable=self._is_discoverable,
            tx_power=self._tx_power,
        )

        logger.info("Advertising service UUIDs: %s", service_uuid_list)
        if self._manufacturer_data:
            logger.info("Manufacturer data: %s", self._manufacturer_data.company)
        await self._server.start(advertisement_data=advertisement_data)

        # Explicitly set characteristic values after server start
        # This ensures values are properly available for read requests
        for service in self._services:
            for char_def in service.characteristics:
                if char_def.initial_value is not None and len(char_def.initial_value) > 0:
                    char_uuid_full = str(BluetoothUUID(char_def.uuid))
                    char = self._server.get_characteristic(char_uuid_full)
                    if char is not None:
                        char.value = bytearray(char_def.initial_value)
                        logger.debug(
                            "Post-start set value for %s: %r",
                            char_uuid_full,
                            bytes(char_def.initial_value),
                        )
                    else:
                        logger.warning(
                            "Could not find characteristic %s after server start",
                            char_uuid_full,
                        )

        self._is_advertising = True
        logger.info("Peripheral '%s' started advertising", self._name)

    async def stop(self) -> None:
        """Stop advertising and disconnect all clients."""
        if self._server is not None:
            await self._server.stop()
            self._server = None
        self._is_advertising = False
        logger.info("Peripheral '%s' stopped", self._name)

    async def update_characteristic(
        self,
        char_uuid: str | BluetoothUUID,
        value: bytearray,
        *,
        notify: bool = True,
    ) -> None:
        """Update a characteristic's value.

        Args:
            char_uuid: UUID of the characteristic to update
            value: New encoded value
            notify: If True, notify subscribed clients

        Raises:
            KeyError: If characteristic UUID not found
            RuntimeError: If peripheral not started

        """
        if self._server is None:
            raise RuntimeError("Peripheral not started")

        # Expand to full UUID format using BluetoothUUID
        uuid_full = str(BluetoothUUID(str(char_uuid)))

        # Find the service containing this characteristic
        service_uuid: str | None = None
        for service in self._services:
            service_uuid_full = str(BluetoothUUID(service.uuid))
            for char_def in service.characteristics:
                char_uuid_full = str(BluetoothUUID(char_def.uuid))
                if char_uuid_full == uuid_full:
                    service_uuid = service_uuid_full
                    break
            if service_uuid:
                break

        if service_uuid is None:
            raise KeyError(f"Characteristic {uuid_full} not found")

        # Update the value
        char = self._server.get_characteristic(uuid_full)
        if char is None:
            raise KeyError(f"Characteristic {uuid_full} not found in server")

        char.value = value

        # Notify subscribers if requested
        if notify:
            self._server.update_value(service_uuid, uuid_full)

        logger.debug("Updated %s to %r", uuid_full, value)

    async def get_characteristic_value(self, char_uuid: str | BluetoothUUID) -> bytearray:
        """Get the current value of a characteristic.

        Args:
            char_uuid: UUID of the characteristic

        Returns:
            The current encoded value

        Raises:
            KeyError: If characteristic UUID not found

        """
        uuid_full = str(BluetoothUUID(str(char_uuid)))

        if self._server is None:
            # Return initial value if not started
            # Check char definitions using full UUID comparison
            for char_def in self._char_definitions.values():
                if str(BluetoothUUID(char_def.uuid)) == uuid_full:
                    return char_def.initial_value
            raise KeyError(f"Characteristic {uuid_full} not found")

        char = self._server.get_characteristic(uuid_full)
        if char is None:
            raise KeyError(f"Characteristic {uuid_full} not found")

        return char.value if char.value else bytearray()


__all__ = ["BlessPeripheralManager"]

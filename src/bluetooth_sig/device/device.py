"""Device class for grouping BLE device services, characteristics, encryption, and advertiser data.

This module provides a high-level Device abstraction that groups all services,
characteristics, encryption requirements, and advertiser data for a BLE device.
It integrates with the BluetoothSIGTranslator for parsing while providing a
unified view of device state.
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Any, Callable, Protocol

from ..gatt.characteristics import CharacteristicName
from ..gatt.context import CharacteristicContext, DeviceInfo
from ..gatt.services import GattServiceRegistry, ServiceName
from ..gatt.services.base import BaseGattService
from ..types import (
    CharacteristicDataProtocol,
    DeviceAdvertiserData,
)
from ..types.data_types import CharacteristicData
from ..types.device_types import DeviceEncryption, DeviceService
from .advertising_parser import AdvertisingParser
from .connection import ConnectionManagerProtocol


class SIGTranslatorProtocol(Protocol):  # pylint: disable=too-few-public-methods
    """Protocol for SIG translator interface."""

    @abstractmethod
    def parse_characteristics(
        self, char_data: dict[str, bytes], ctx: CharacteristicContext | None = None
    ) -> dict[str, Any]:
        """Parse multiple characteristics at once."""

    @abstractmethod
    def parse_characteristic(
        self,
        uuid: str,
        raw_data: bytes,
        ctx: CharacteristicContext | None = None,
        properties: set[str] | None = None,
    ) -> Any:
        """Parse a single characteristic's raw bytes."""

    @abstractmethod
    def get_characteristic_uuid(self, name: str | CharacteristicName) -> str | None:
        """Get the UUID for a characteristic name or enum."""

    @abstractmethod
    def get_service_uuid(self, name: str | ServiceName) -> str | None:
        """Get the UUID for a service name or enum."""

    def get_characteristic_info_by_name(self, name: str) -> Any | None:
        """Get characteristic info by name (optional method)."""


class UnknownService(BaseGattService):
    """Generic service for unknown/unsupported UUIDs."""

    @classmethod
    def get_expected_characteristics(cls) -> dict[str, type]:
        return {}

    @classmethod
    def get_required_characteristics(cls) -> dict[str, type]:
        return {}


class Device:
    """High-level BLE device abstraction."""

    def __init__(self, address: str, translator: SIGTranslatorProtocol) -> None:
        self.address = address
        self.translator = translator
        # Optional connection manager implementing ConnectionManagerProtocol
        self.connection_manager: ConnectionManagerProtocol | None = None
        self._name: str = ""
        self.services: dict[str, DeviceService] = {}
        self.encryption = DeviceEncryption()
        self.advertiser_data = DeviceAdvertiserData(b"")

        # Advertising parser for handling advertising data
        self.advertising_parser = AdvertisingParser()

        # Cached device info - updated when name or advertiser_data changes
        self._device_info: DeviceInfo | None = None
        self._device_info_dirty: bool = True

    @property
    def name(self) -> str:
        """Get the device name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the device name and invalidate device info cache if changed."""
        if self._name != value:
            self._name = value
            self._invalidate_device_info_cache()

    @property
    def device_info(self) -> DeviceInfo:
        """Get cached device info, updating only when necessary."""
        if self._device_info is None:
            # First time - create new object
            self._device_info = DeviceInfo(
                address=self.address,
                name=self.name,
                manufacturer_data=self.advertiser_data.manufacturer_data,
                service_uuids=self.advertiser_data.service_uuids,
            )
            self._device_info_dirty = False
        elif self._device_info_dirty:
            # Update existing object in place to avoid object allocation
            self._device_info.address = self.address
            self._device_info.name = self.name
            self._device_info.manufacturer_data = self.advertiser_data.manufacturer_data
            self._device_info.service_uuids = self.advertiser_data.service_uuids
            self._device_info_dirty = False
        return self._device_info

    def _invalidate_device_info_cache(self) -> None:
        """Mark cached device info as dirty when underlying data changes."""
        self._device_info_dirty = True

    def __str__(self) -> str:
        service_count = len(self.services)
        char_count = sum(
            len(service.characteristics) for service in self.services.values()
        )
        return f"Device({self.address}, name={self.name}, {service_count} services, {char_count} characteristics)"

    def add_service(
        self, service_name: str | ServiceName, characteristics: dict[str, bytes]
    ) -> None:
        """Add a service to the device with its characteristics.

        Args:
            service_name: Name or enum of the service to add
            characteristics: Dictionary mapping characteristic UUIDs to raw data
        """
        # Handle service identification - could be name, enum, or UUID
        service_uuid = None

        if isinstance(service_name, ServiceName):
            # It's an enum, get UUID from translator
            service_uuid = self.translator.get_service_uuid(service_name.value)
            if not service_uuid:
                # Enum not recognized - treat enum value as unknown UUID
                service_uuid = service_name.value
        else:
            # It's a string - try as name first, then as UUID
            service_uuid = self.translator.get_service_uuid(service_name)
            if not service_uuid:
                # Try treating it as a UUID directly
                service_class = GattServiceRegistry.get_service_class(service_name)
                if service_class:
                    service_uuid = service_name
                else:
                    # Neither translator nor registry recognize it - treat as unknown UUID
                    service_uuid = service_name

        service_class = GattServiceRegistry.get_service_class(service_uuid)
        if not service_class:
            service: BaseGattService = UnknownService()
        else:
            service = service_class()

        base_ctx = CharacteristicContext(device_info=self.device_info)

        parsed_characteristics = self.translator.parse_characteristics(
            characteristics, ctx=base_ctx
        )

        for char_data in parsed_characteristics.values():
            self.update_encryption_requirements(char_data)

        device_service = DeviceService(
            service=service, characteristics=parsed_characteristics
        )

        service_key = (
            service_name if isinstance(service_name, str) else service_name.value
        )
        self.services[service_key] = device_service

    def attach_connection_manager(self, manager: ConnectionManagerProtocol) -> None:
        """Attach a connection manager to handle BLE connections.

        Args:
            manager: Connection manager implementing the ConnectionManagerProtocol
        """
        self.connection_manager = manager

    async def detach_connection_manager(self) -> None:
        """Detach the current connection manager and disconnect if connected."""
        if self.connection_manager:
            await self.disconnect()
        self.connection_manager = None

    async def connect(self) -> None:
        """Connect to the BLE device.

        Raises:
            RuntimeError: If no connection manager is attached
        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")
        await self.connection_manager.connect()

    async def disconnect(self) -> None:
        """Disconnect from the BLE device.

        Raises:
            RuntimeError: If no connection manager is attached
        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")
        await self.connection_manager.disconnect()

    async def read(self, char_name: str | CharacteristicName) -> Any | None:
        """Read a characteristic value from the device.

        Args:
            char_name: Name or enum of the characteristic to read

        Returns:
            Parsed characteristic value or None if read fails

        Raises:
            RuntimeError: If no connection manager is attached
        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        resolved_uuid = self._resolve_characteristic_name(char_name)
        raw = await self.connection_manager.read_gatt_char(resolved_uuid)
        parsed = self.translator.parse_characteristic(resolved_uuid, raw)
        return parsed

    async def write(self, char_name: str | CharacteristicName, data: bytes) -> None:
        """Write data to a characteristic on the device.

        Args:
            char_name: Name or enum of the characteristic to write to
            data: Raw bytes to write

        Raises:
            RuntimeError: If no connection manager is attached
        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        resolved_uuid = self._resolve_characteristic_name(char_name)
        await self.connection_manager.write_gatt_char(resolved_uuid, data)

    async def start_notify(
        self, char_name: str | CharacteristicName, callback: Callable[[Any], None]
    ) -> None:
        """Start notifications for a characteristic.

        Args:
            char_name: Name or enum of the characteristic to monitor
            callback: Function to call when notifications are received

        Raises:
            RuntimeError: If no connection manager is attached
        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        resolved_uuid = self._resolve_characteristic_name(char_name)

        def _internal_cb(sender: str, data: bytes) -> None:
            parsed = self.translator.parse_characteristic(sender, data)
            try:
                callback(parsed)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logging.exception("Notification callback raised an exception: %s", exc)

        await self.connection_manager.start_notify(resolved_uuid, _internal_cb)

    def _resolve_characteristic_name(self, identifier: str | CharacteristicName) -> str:
        """Resolve a characteristic name or enum to its UUID.

        Args:
            identifier: Characteristic name string or enum

        Returns:
            Characteristic UUID string

        Raises:
            ValueError: If the characteristic name cannot be resolved
        """
        if isinstance(identifier, CharacteristicName):
            name = identifier.value
        else:
            name = identifier

        uuid = self.translator.get_characteristic_uuid(name)
        if uuid:
            return uuid

        norm = name.strip()
        stripped = norm.replace("-", "")
        if len(stripped) in (4, 8, 32) and all(
            c in "0123456789abcdefABCDEF" for c in stripped
        ):
            return norm

        raise ValueError(f"Unknown characteristic name: '{identifier}'")

    async def stop_notify(self, char_name: str | CharacteristicName) -> None:
        """Stop notifications for a characteristic.

        Args:
            char_name: Characteristic name or UUID
        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached")

        resolved_uuid = self._resolve_characteristic_name(char_name)
        await self.connection_manager.stop_notify(resolved_uuid)

    def parse_advertiser_data(self, raw_data: bytes) -> None:
        """Parse raw advertising data and update device information.

        Args:
            raw_data: Raw bytes from BLE advertising packet
        """
        parsed_data = self.advertising_parser.parse_advertising_data(raw_data)
        self.advertiser_data = parsed_data

        # Invalidate device info cache since advertiser data changed
        self._invalidate_device_info_cache()

        # Update device name if not set
        if parsed_data.local_name and not self.name:
            self.name = parsed_data.local_name
            # Cache already invalidated above, no need to call again

    def get_characteristic_data(
        self, service_name: str | ServiceName, char_uuid: str
    ) -> CharacteristicDataProtocol | None:
        """Get parsed characteristic data for a specific service and characteristic.

        Args:
            service_name: Name or enum of the service
            char_uuid: UUID of the characteristic

        Returns:
            Parsed characteristic data or None if not found
        """
        service_key = (
            service_name if isinstance(service_name, str) else service_name.value
        )
        service = self.services.get(service_key)
        if service:
            return service.characteristics.get(char_uuid)
        return None

    def update_encryption_requirements(self, char_data: CharacteristicData) -> None:
        """Update device encryption requirements based on characteristic properties.

        Args:
            char_data: Parsed characteristic data with properties
        """
        if hasattr(char_data, "properties") and char_data.properties:
            if (
                "encrypt-read" in char_data.properties
                or "encrypt-write" in char_data.properties
            ):
                self.encryption.requires_encryption = True
            if (
                "auth-read" in char_data.properties
                or "auth-write" in char_data.properties
            ):
                self.encryption.requires_authentication = True

    async def discover_services(self) -> dict[str, Any]:
        """Discover all services and characteristics from the device.

        Returns:
            Dictionary mapping service UUIDs to service information

        Raises:
            RuntimeError: If no connection manager is attached
        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        services_data = await self.connection_manager.get_services()

        # Store discovered services in our internal structure
        for service_info in services_data:
            service_uuid = service_info.uuid
            if service_uuid not in self.services:
                # Create a service instance - we'll use UnknownService for undiscovered services
                service_instance = UnknownService()
                device_service = DeviceService(
                    service=service_instance, characteristics={}
                )
                self.services[service_uuid] = device_service

            # Add characteristics to the service
            for char_info in service_info.characteristics:
                char_uuid = char_info.uuid
                self.services[service_uuid].characteristics[char_uuid] = char_info

        return dict(self.services)

    async def get_characteristic_info(self, char_uuid: str) -> Any | None:
        """Get information about a characteristic from the connection manager.

        Args:
            char_uuid: UUID of the characteristic

        Returns:
            Characteristic information or None if not found

        Raises:
            RuntimeError: If no connection manager is attached
        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        services_data = await self.connection_manager.get_services()
        for service_info in services_data:
            for char_info in service_info.characteristics:
                if char_info.uuid == char_uuid:
                    return char_info
        return None

    async def read_multiple(
        self, char_names: list[str | CharacteristicName]
    ) -> dict[str, Any | None]:
        """Read multiple characteristics in batch.

        Args:
            char_names: List of characteristic names or enums to read

        Returns:
            Dictionary mapping characteristic UUIDs to parsed values

        Raises:
            RuntimeError: If no connection manager is attached
        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        results = {}
        for char_name in char_names:
            try:
                value = await self.read(char_name)
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[resolved_uuid] = value
            except (OSError, ValueError, KeyError) as exc:
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[resolved_uuid] = None
                logging.warning("Failed to read characteristic %s: %s", char_name, exc)

        return results

    async def write_multiple(
        self, data_map: dict[str | CharacteristicName, bytes]
    ) -> dict[str, bool]:
        """Write to multiple characteristics in batch.

        Args:
            data_map: Dictionary mapping characteristic names/enums to data bytes

        Returns:
            Dictionary mapping characteristic UUIDs to success status

        Raises:
            RuntimeError: If no connection manager is attached
        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        results = {}
        for char_name, data in data_map.items():
            try:
                await self.write(char_name, data)
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[resolved_uuid] = True
            except (OSError, ValueError, KeyError) as exc:
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[resolved_uuid] = False
                logging.warning("Failed to write characteristic %s: %s", char_name, exc)

        return results

    @property
    def is_connected(self) -> bool:
        """Check if the device is currently connected.

        Returns:
            True if connected, False otherwise
        """
        if not self.connection_manager:
            return False
        return self.connection_manager.is_connected

    def get_service_by_uuid(self, service_uuid: str) -> DeviceService | None:
        """Get a service by its UUID.

        Args:
            service_uuid: UUID of the service

        Returns:
            DeviceService instance or None if not found
        """
        return self.services.get(service_uuid)

    def get_services_by_name(
        self, service_name: str | ServiceName
    ) -> list[DeviceService]:
        """Get services by name.

        Args:
            service_name: Name or enum of the service

        Returns:
            List of matching DeviceService instances
        """
        service_uuid = self.translator.get_service_uuid(
            service_name if isinstance(service_name, str) else service_name.value
        )
        if service_uuid and service_uuid in self.services:
            return [self.services[service_uuid]]
        return []

    def list_characteristics(
        self, service_uuid: str | None = None
    ) -> dict[str, list[str]]:
        """List all characteristics, optionally filtered by service.

        Args:
            service_uuid: Optional service UUID to filter by

        Returns:
            Dictionary mapping service UUIDs to lists of characteristic UUIDs
        """
        if service_uuid:
            service = self.services.get(service_uuid)
            if service:
                return {service_uuid: list(service.characteristics.keys())}
            return {}

        return {
            svc_uuid: list(service.characteristics.keys())
            for svc_uuid, service in self.services.items()
        }

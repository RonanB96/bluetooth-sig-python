"""Device class for grouping BLE device services, characteristics, encryption, and advertiser data.

This module provides a high-level Device abstraction that groups all
services, characteristics, encryption requirements, and advertiser data
for a BLE device. It integrates with the BluetoothSIGTranslator for
parsing while providing a unified view of device state.
"""

from __future__ import annotations

import logging
import re
from abc import abstractmethod
from typing import Any, Callable, Protocol

from ..gatt.characteristics import CharacteristicName
from ..gatt.context import CharacteristicContext, DeviceInfo
from ..gatt.services import GattServiceRegistry, ServiceName
from ..gatt.services.base import BaseGattService, UnknownService
from ..types import (
    BLEAdvertisementTypes,
    BLEAdvertisingPDU,
    CharacteristicDataProtocol,
    DeviceAdvertiserData,
    ParsedADStructures,
    PDUConstants,
)
from ..types.data_types import CharacteristicData
from ..types.device_types import DeviceEncryption, DeviceService
from ..types.gatt_enums import GattProperty
from ..types.uuid import BluetoothUUID
from .advertising_parser import AdvertisingParser
from .connection import ConnectionManagerProtocol

__all__ = [
    "Device",
    "SIGTranslatorProtocol",
    "UnknownService",
]


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
    ) -> Any:  # noqa: ANN401  # Returns characteristic-specific types (int, float, dataclass, etc.)
        """Parse a single characteristic's raw bytes."""

    @abstractmethod
    def get_characteristic_uuid_by_name(self, name: CharacteristicName) -> BluetoothUUID | None:
        """Get the UUID for a characteristic name enum (enum-only API)."""

    @abstractmethod
    def get_service_uuid_by_name(self, name: str | ServiceName) -> BluetoothUUID | None:
        """Get the UUID for a service name or enum."""

    def get_characteristic_info_by_name(self, name: CharacteristicName) -> Any | None:  # noqa: ANN401  # Adapter-specific characteristic info
        """Get characteristic info by enum name (optional method)."""


def _is_uuid_like(value: str) -> bool:
    """Check if a string looks like a Bluetooth UUID."""
    # Remove dashes and check if it's a valid hex string of UUID length
    clean = value.replace("-", "")
    return bool(re.match(r"^[0-9A-Fa-f]+$", clean)) and len(clean) in [4, 8, 32]


class Device:  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    r"""High-level BLE device abstraction.

    This class groups all services, characteristics, encryption requirements, and
    advertiser data for a BLE device. It integrates with
    [BluetoothSIGTranslator][bluetooth_sig.BluetoothSIGTranslator]
    for parsing while providing a unified view of device state.

    Key features:
    - Parse advertiser data from BLE scan results
    - Add and manage GATT services with their characteristics
    - Access parsed characteristic data by UUID
    - Handle device encryption requirements
    - Cache device information for performance

    Example:
        Create and configure a device:

        ```python
        from bluetooth_sig import BluetoothSIGTranslator, Device

        translator = BluetoothSIGTranslator()
        device = Device("AA:BB:CC:DD:EE:FF", translator)

        # Add a service
        device.add_service("180F", {"2A19": b"\\x64"})  # Battery service

        # Get parsed data
        battery = device.get_characteristic_data("2A19")
        print(f"Battery: {battery.value}%")
        ```

    """

    def __init__(self, address: str, translator: SIGTranslatorProtocol) -> None:
        """Initialise Device instance with address and translator.

        Args:
            address: BLE device address
            translator: SIGTranslatorProtocol instance

        """
        self.address = address
        self.translator = translator
        # Optional connection manager implementing ConnectionManagerProtocol
        self.connection_manager: ConnectionManagerProtocol | None = None
        self._name: str = ""
        self.services: dict[str, DeviceService] = {}
        self.encryption = DeviceEncryption()
        self.advertiser_data = DeviceAdvertiserData(raw_data=b"")

        # Advertising parser for handling advertising data
        self.advertising_parser = AdvertisingParser()

        # Cache for device_info property
        self._device_info_cache: DeviceInfo | None = None

    def __str__(self) -> str:
        """Return string representation of Device.

        Returns:
            str: String representation of Device.

        """
        service_count = len(self.services)
        char_count = sum(len(service.characteristics) for service in self.services.values())
        return f"Device({self.address}, name={self.name}, {service_count} services, {char_count} characteristics)"

    def add_service(self, service_name: str | ServiceName, characteristics: dict[str, bytes]) -> None:
        """Add a service to the device with its characteristics.

        Args:
            service_name: Name or enum of the service to add
            characteristics: Dictionary mapping characteristic UUIDs to raw data

        """
        # Resolve service UUID: accept UUID-like strings directly, else ask translator
        # service_uuid can be a BluetoothUUID or None (translator may return None)
        service_uuid: BluetoothUUID | None
        if isinstance(service_name, str) and _is_uuid_like(service_name):
            service_uuid = BluetoothUUID(service_name)
        else:
            service_uuid = self.translator.get_service_uuid_by_name(service_name)

        if not service_uuid:
            # No UUID found - this is an error condition
            service_name_str = service_name if isinstance(service_name, str) else service_name.value
            raise ValueError(
                f"Cannot resolve service UUID for '{service_name_str}'. "
                "Service name not found in registry and not a valid UUID format."
            )

        service_class = GattServiceRegistry.get_service_class(service_uuid)
        service: BaseGattService
        if not service_class:
            service = UnknownService(uuid=service_uuid)
        else:
            service = service_class()

        device_info = DeviceInfo(
            address=self.address,
            name=self.name,
            manufacturer_data=self.advertiser_data.manufacturer_data,
            service_uuids=self.advertiser_data.service_uuids,
        )

        base_ctx = CharacteristicContext(device_info=device_info)

        parsed_characteristics = self.translator.parse_characteristics(characteristics, ctx=base_ctx)

        for char_data in parsed_characteristics.values():
            self.update_encryption_requirements(char_data)

        device_service = DeviceService(service=service, characteristics=parsed_characteristics)

        service_key = service_name if isinstance(service_name, str) else service_name.value
        self.services[service_key] = device_service

    def attach_connection_manager(self, manager: ConnectionManagerProtocol) -> None:
        """Attach a connection manager to handle BLE connections.

        Args:
            manager: Connection manager implementing the ConnectionManagerProtocol

        """
        self.connection_manager = manager

    async def detach_connection_manager(self) -> None:
        """Detach the current connection manager and disconnect if connected.

        Disconnects if a connection manager is present, then removes it.
        """
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

    async def read(self, char_name: str | CharacteristicName) -> Any | None:  # noqa: ANN401  # Returns characteristic-specific types
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
        parsed = self.translator.parse_characteristic(str(resolved_uuid), raw)
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

    async def start_notify(self, char_name: str | CharacteristicName, callback: Callable[[Any], None]) -> None:
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

    def _resolve_characteristic_name(self, identifier: str | CharacteristicName) -> BluetoothUUID:
        """Resolve a characteristic name or enum to its UUID.

        Args:
            identifier: Characteristic name string or enum

        Returns:
            Characteristic UUID string

        Raises:
            ValueError: If the characteristic name cannot be resolved

        """
        if isinstance(identifier, CharacteristicName):
            # For enum inputs, ask the translator for the UUID
            uuid = self.translator.get_characteristic_uuid_by_name(identifier)
            if uuid:
                return uuid
            norm = identifier.value.strip()
        else:
            norm = identifier
        stripped = norm.replace("-", "")
        if len(stripped) in (4, 8, 32) and all(c in "0123456789abcdefABCDEF" for c in stripped):
            return BluetoothUUID(norm)

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

        # Update device name if not set
        if parsed_data.local_name and not self.name:
            self.name = parsed_data.local_name

    def get_characteristic_data(
        self, service_name: str | ServiceName, char_uuid: str
    ) -> CharacteristicDataProtocol | None:
        """Get parsed characteristic data for a specific service and characteristic.

        Args:
            service_name: Name or enum of the service
            char_uuid: UUID of the characteristic

        Returns:
            Parsed characteristic data or None if not found.

        """
        service_key = service_name if isinstance(service_name, str) else service_name.value
        service = self.services.get(service_key)
        if service:
            return service.characteristics.get(char_uuid)
        return None

    def update_encryption_requirements(self, char_data: CharacteristicData) -> None:
        """Update device encryption requirements based on characteristic properties.

        Args:
            char_data: The parsed characteristic data with properties

        """
        properties = char_data.properties

        # Check for encryption requirements
        encrypt_props = [GattProperty.ENCRYPT_READ, GattProperty.ENCRYPT_WRITE, GattProperty.ENCRYPT_NOTIFY]
        if any(prop in properties for prop in encrypt_props):
            self.encryption.requires_encryption = True

        # Check for authentication requirements
        auth_props = [GattProperty.AUTH_READ, GattProperty.AUTH_WRITE, GattProperty.AUTH_NOTIFY]
        if any(prop in properties for prop in auth_props):
            self.encryption.requires_authentication = True

    def _parse_auxiliary_packets(self, aux_ptr: bytes) -> list[BLEAdvertisingPDU]:
        if len(aux_ptr) != PDUConstants.AUX_PTR:
            return []

        return []

    # pylint: disable=duplicate-code
    # NOTE: This method duplicates AdvertisingParser._parse_legacy_advertising for backwards compatibility.
    # TODO: Refactor to delegate to AdvertisingParser.parse() instead of maintaining duplicate BLE spec parsing.
    # Duplication exists because Device has legacy inline parsing; consolidation requires API migration.
    def _parse_legacy_advertising(self, raw_data: bytes) -> None:
        manufacturer_data: dict[int, bytes] = {}
        service_uuids: list[str] = []
        local_name: str = ""
        tx_power: int | None = None
        flags: int | None = None

        i = 0
        while i < len(raw_data):
            if i + 1 >= len(raw_data):
                break

            length = raw_data[i]
            if length == 0 or i + length + 1 > len(raw_data):
                break

            ad_type = raw_data[i + 1]
            ad_data = raw_data[i + 2 : i + length + 1]

            if ad_type == BLEAdvertisementTypes.FLAGS and len(ad_data) >= 1:
                flags = ad_data[0]
            elif ad_type in (
                BLEAdvertisementTypes.INCOMPLETE_16BIT_SERVICE_UUIDS,
                BLEAdvertisementTypes.COMPLETE_16BIT_SERVICE_UUIDS,
            ):
                for j in range(0, len(ad_data), 2):
                    if j + 1 < len(ad_data):
                        uuid_short = ad_data[j] | (ad_data[j + 1] << 8)
                        service_uuids.append(f"{uuid_short:04X}")
            elif ad_type in (
                BLEAdvertisementTypes.SHORTENED_LOCAL_NAME,
                BLEAdvertisementTypes.COMPLETE_LOCAL_NAME,
            ):
                try:
                    local_name = ad_data.decode("utf-8")
                except UnicodeDecodeError:
                    local_name = ad_data.hex()
            elif ad_type == BLEAdvertisementTypes.TX_POWER_LEVEL and len(ad_data) >= 1:
                tx_power = int.from_bytes(ad_data[:1], byteorder="little", signed=True)
            elif ad_type == BLEAdvertisementTypes.MANUFACTURER_SPECIFIC_DATA and len(ad_data) >= 2:
                company_id = ad_data[0] | (ad_data[1] << 8)
                manufacturer_data[company_id] = ad_data[2:]

            i += length + 1

        self.advertiser_data = DeviceAdvertiserData(
            raw_data=raw_data,
            local_name=local_name,
            manufacturer_data=manufacturer_data,
            service_uuids=service_uuids,
            tx_power=tx_power,
            flags=flags,
        )

        if local_name and not self.name:
            self.name = local_name

    # pylint: disable=duplicate-code
    # NOTE: This method duplicates AdvertisingParser._parse_ad_structures for backwards compatibility.
    # TODO: Refactor to delegate to AdvertisingParser instead of maintaining duplicate BLE spec parsing.
    # Duplication exists because Device has legacy inline parsing; consolidation requires API migration.
    def _parse_ad_structures(self, data: bytes) -> ParsedADStructures:
        """Parse advertising data structures from raw bytes.

        Args:
            data: Raw advertising data payload

        Returns:
            ParsedADStructures object with extracted data

        """
        # pylint: disable=too-many-branches,too-many-statements
        parsed = ParsedADStructures()

        i = 0
        while i < len(data):
            if i + 1 >= len(data):
                break

            length = data[i]
            if length == 0 or i + length + 1 > len(data):
                break

            ad_type = data[i + 1]
            ad_data = data[i + 2 : i + length + 1]

            if ad_type == BLEAdvertisementTypes.FLAGS and len(ad_data) >= 1:
                parsed.flags = ad_data[0]
            elif ad_type in (
                BLEAdvertisementTypes.INCOMPLETE_16BIT_SERVICE_UUIDS,
                BLEAdvertisementTypes.COMPLETE_16BIT_SERVICE_UUIDS,
            ):
                for j in range(0, len(ad_data), 2):
                    if j + 1 < len(ad_data):
                        uuid_short = ad_data[j] | (ad_data[j + 1] << 8)
                        parsed.service_uuids.append(f"{uuid_short:04X}")
            elif ad_type in (
                BLEAdvertisementTypes.SHORTENED_LOCAL_NAME,
                BLEAdvertisementTypes.COMPLETE_LOCAL_NAME,
            ):
                try:
                    parsed.local_name = ad_data.decode("utf-8")
                except UnicodeDecodeError:
                    parsed.local_name = ad_data.hex()
            elif ad_type == BLEAdvertisementTypes.TX_POWER_LEVEL and len(ad_data) >= 1:
                parsed.tx_power = int.from_bytes(ad_data[:1], byteorder="little", signed=True)
            elif ad_type == BLEAdvertisementTypes.MANUFACTURER_SPECIFIC_DATA and len(ad_data) >= 2:
                company_id = ad_data[0] | (ad_data[1] << 8)
                parsed.manufacturer_data[company_id] = ad_data[2:]
            elif ad_type == BLEAdvertisementTypes.APPEARANCE and len(ad_data) >= 2:
                parsed.appearance = ad_data[0] | (ad_data[1] << 8)
            elif ad_type == BLEAdvertisementTypes.SERVICE_DATA_16BIT and len(ad_data) >= 2:
                service_uuid = f"{ad_data[0] | (ad_data[1] << 8):04X}"
                parsed.service_data[service_uuid] = ad_data[2:]
            elif ad_type == BLEAdvertisementTypes.URI:
                try:
                    parsed.uri = ad_data.decode("utf-8")
                except UnicodeDecodeError:
                    parsed.uri = ad_data.hex()
            elif ad_type == BLEAdvertisementTypes.INDOOR_POSITIONING:
                parsed.indoor_positioning = ad_data
            elif ad_type == BLEAdvertisementTypes.TRANSPORT_DISCOVERY_DATA:
                parsed.transport_discovery_data = ad_data
            elif ad_type == BLEAdvertisementTypes.LE_SUPPORTED_FEATURES:
                parsed.le_supported_features = ad_data
            elif ad_type == BLEAdvertisementTypes.ENCRYPTED_ADVERTISING_DATA:
                parsed.encrypted_advertising_data = ad_data
            elif ad_type == BLEAdvertisementTypes.PERIODIC_ADVERTISING_RESPONSE_TIMING_INFORMATION:
                parsed.periodic_advertising_response_timing = ad_data
            elif ad_type == BLEAdvertisementTypes.ELECTRONIC_SHELF_LABEL:
                parsed.electronic_shelf_label = ad_data
            elif ad_type == BLEAdvertisementTypes.THREE_D_INFORMATION_DATA:
                parsed.three_d_information = ad_data
            elif ad_type == BLEAdvertisementTypes.BROADCAST_NAME:
                try:
                    parsed.broadcast_name = ad_data.decode("utf-8")
                except UnicodeDecodeError:
                    parsed.broadcast_name = ad_data.hex()
            elif ad_type == BLEAdvertisementTypes.BROADCAST_CODE:
                parsed.broadcast_code = ad_data
            elif ad_type == BLEAdvertisementTypes.BIGINFO:
                parsed.biginfo = ad_data
            elif ad_type == BLEAdvertisementTypes.MESH_MESSAGE:
                parsed.mesh_message = ad_data
            elif ad_type == BLEAdvertisementTypes.MESH_BEACON:
                parsed.mesh_beacon = ad_data
            elif ad_type == BLEAdvertisementTypes.PUBLIC_TARGET_ADDRESS:
                for j in range(0, len(ad_data), 6):
                    if j + 5 < len(ad_data):
                        addr_bytes = ad_data[j : j + 6]
                        addr_str = ":".join(f"{b:02X}" for b in addr_bytes[::-1])
                        parsed.public_target_address.append(addr_str)
            elif ad_type == BLEAdvertisementTypes.RANDOM_TARGET_ADDRESS:
                for j in range(0, len(ad_data), 6):
                    if j + 5 < len(ad_data):
                        addr_bytes = ad_data[j : j + 6]
                        addr_str = ":".join(f"{b:02X}" for b in addr_bytes[::-1])
                        parsed.random_target_address.append(addr_str)
            elif ad_type == BLEAdvertisementTypes.ADVERTISING_INTERVAL and len(ad_data) >= 2:
                parsed.advertising_interval = ad_data[0] | (ad_data[1] << 8)
            elif ad_type == BLEAdvertisementTypes.ADVERTISING_INTERVAL_LONG and len(ad_data) >= 3:
                parsed.advertising_interval_long = ad_data[0] | (ad_data[1] << 8) | (ad_data[2] << 16)
            elif ad_type == BLEAdvertisementTypes.LE_BLUETOOTH_DEVICE_ADDRESS and len(ad_data) >= 6:
                addr_bytes = ad_data[:6]
                parsed.le_bluetooth_device_address = ":".join(f"{b:02X}" for b in addr_bytes[::-1])
            elif ad_type == BLEAdvertisementTypes.LE_ROLE and len(ad_data) >= 1:
                parsed.le_role = ad_data[0]
            elif ad_type == BLEAdvertisementTypes.CLASS_OF_DEVICE and len(ad_data) >= 3:
                parsed.class_of_device = ad_data[0] | (ad_data[1] << 8) | (ad_data[2] << 16)
            elif ad_type == BLEAdvertisementTypes.SIMPLE_PAIRING_HASH_C:
                parsed.simple_pairing_hash_c = ad_data
            elif ad_type == BLEAdvertisementTypes.SIMPLE_PAIRING_RANDOMIZER_R:
                parsed.simple_pairing_randomizer_r = ad_data
            elif ad_type == BLEAdvertisementTypes.SECURITY_MANAGER_TK_VALUE:
                parsed.security_manager_tk_value = ad_data
            elif ad_type == BLEAdvertisementTypes.SECURITY_MANAGER_OUT_OF_BAND_FLAGS:
                parsed.security_manager_out_of_band_flags = ad_data
            elif ad_type == BLEAdvertisementTypes.SLAVE_CONNECTION_INTERVAL_RANGE:
                parsed.slave_connection_interval_range = ad_data
            elif ad_type == BLEAdvertisementTypes.SECURE_CONNECTIONS_CONFIRMATION_VALUE:
                parsed.secure_connections_confirmation = ad_data
            elif ad_type == BLEAdvertisementTypes.SECURE_CONNECTIONS_RANDOM_VALUE:
                parsed.secure_connections_random = ad_data
            elif ad_type == BLEAdvertisementTypes.CHANNEL_MAP_UPDATE_INDICATION:
                parsed.channel_map_update_indication = ad_data
            elif ad_type == BLEAdvertisementTypes.PB_ADV:
                parsed.pb_adv = ad_data
            elif ad_type == BLEAdvertisementTypes.RESOLVABLE_SET_IDENTIFIER:
                parsed.resolvable_set_identifier = ad_data

            i += length + 1

        return parsed

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
                service_instance = UnknownService(uuid=BluetoothUUID(service_uuid))
                device_service = DeviceService(service=service_instance, characteristics={})
                self.services[service_uuid] = device_service

            # Add characteristics to the service
            for char_info in service_info.characteristics:
                char_uuid = char_info.uuid
                self.services[service_uuid].characteristics[char_uuid] = char_info

        return dict(self.services)

    async def get_characteristic_info(self, char_uuid: str) -> Any | None:  # noqa: ANN401  # Adapter-specific characteristic metadata
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

    async def read_multiple(self, char_names: list[str | CharacteristicName]) -> dict[str, Any | None]:
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

        results: dict[str, Any | None] = {}
        for char_name in char_names:
            try:
                value = await self.read(char_name)
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[str(resolved_uuid)] = value
            except Exception as exc:  # pylint: disable=broad-exception-caught
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[str(resolved_uuid)] = None
                logging.warning("Failed to read characteristic %s: %s", char_name, exc)

        return results

    async def write_multiple(self, data_map: dict[str | CharacteristicName, bytes]) -> dict[str, bool]:
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

        results: dict[str, bool] = {}
        for char_name, data in data_map.items():
            try:
                await self.write(char_name, data)
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[str(resolved_uuid)] = True
            except Exception as exc:  # pylint: disable=broad-exception-caught
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[str(resolved_uuid)] = False
                logging.warning("Failed to write characteristic %s: %s", char_name, exc)

        return results

    @property
    def device_info(self) -> DeviceInfo:
        """Get cached device info object.

        Returns:
            DeviceInfo with current device metadata

        """
        if self._device_info_cache is None:
            self._device_info_cache = DeviceInfo(
                address=self.address,
                name=self.name,
                manufacturer_data=self.advertiser_data.manufacturer_data,
                service_uuids=self.advertiser_data.service_uuids,
            )
        else:
            # Update existing cache object with current data
            self._device_info_cache.name = self.name
            self._device_info_cache.manufacturer_data = self.advertiser_data.manufacturer_data
            self._device_info_cache.service_uuids = self.advertiser_data.service_uuids
        return self._device_info_cache

    @property
    def name(self) -> str:
        """Get the device name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the device name and update cached device_info."""
        self._name = value
        # Update existing cache object if it exists
        if self._device_info_cache is not None:
            self._device_info_cache.name = value

    @property
    def is_connected(self) -> bool:
        """Check if the device is currently connected.

        Returns:
            True if connected, False otherwise

        """
        if self.connection_manager is None:
            return False
        # Check if the connection manager has an is_connected property
        return getattr(self.connection_manager, "is_connected", False)

    def get_service_by_uuid(self, service_uuid: str) -> DeviceService | None:
        """Get a service by its UUID.

        Args:
            service_uuid: UUID of the service

        Returns:
            DeviceService instance or None if not found

        """
        return self.services.get(service_uuid)

    def get_services_by_name(self, service_name: str | ServiceName) -> list[DeviceService]:
        """Get services by name.

        Args:
            service_name: Name or enum of the service

        Returns:
            List of matching DeviceService instances

        """
        service_uuid = self.translator.get_service_uuid_by_name(
            service_name if isinstance(service_name, str) else service_name.value
        )
        if service_uuid and str(service_uuid) in self.services:
            return [self.services[str(service_uuid)]]
        return []

    def list_characteristics(self, service_uuid: str | None = None) -> dict[str, list[str]]:
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

        return {svc_uuid: list(service.characteristics.keys()) for svc_uuid, service in self.services.items()}

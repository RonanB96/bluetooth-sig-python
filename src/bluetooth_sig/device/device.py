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
    BLEAdvertisementTypes,
    BLEAdvertisingPDU,
    BLEExtendedHeader,
    CharacteristicDataProtocol,
    DeviceAdvertiserData,
    ParsedADStructures,
    PDUConstants,
    PDUFlags,
    PDUType,
)
from ..types.data_types import CharacteristicData
from ..types.device_types import DeviceEncryption, DeviceService
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
        self.name: str = ""
        self.services: dict[str, DeviceService] = {}
        self.encryption = DeviceEncryption()
        self.advertiser_data = DeviceAdvertiserData(b"")

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
        # Get the service UUID from the name
        service_uuid = self.translator.get_service_uuid(service_name)
        if not service_uuid:
            # Fallback to unknown service if name not found
            service: BaseGattService = UnknownService()
            device_service = DeviceService(service=service, characteristics={})
            self.services[
                service_name if isinstance(service_name, str) else service_name.value
            ] = device_service
            return

        service_class = GattServiceRegistry.get_service_class(service_uuid)
        if not service_class:
            service = UnknownService()
        else:
            service = service_class()

        device_info = DeviceInfo(
            address=self.address,
            name=self.name,
            manufacturer_data=self.advertiser_data.manufacturer_data,
            service_uuids=self.advertiser_data.service_uuids,
        )

        base_ctx = CharacteristicContext(device_info=device_info)

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
            char_name: Name or enum of the characteristic to stop monitoring

        Raises:
            RuntimeError: If no connection manager is attached
        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")
        resolved_uuid = self._resolve_characteristic_name(char_name)
        await self.connection_manager.stop_notify(resolved_uuid)

    def parse_advertiser_data(self, raw_data: bytes) -> None:
        """Parse raw advertising data and update device information.

        Args:
            raw_data: Raw bytes from BLE advertising packet
        """
        if self._is_extended_advertising_pdu(raw_data):
            self._parse_extended_advertising(raw_data)
        else:
            self._parse_legacy_advertising(raw_data)

    def _is_extended_advertising_pdu(self, data: bytes) -> bool:
        """Check if the advertising data is an extended advertising PDU.

        Args:
            data: Raw advertising data bytes

        Returns:
            True if extended advertising PDU, False otherwise
        """
        if len(data) < PDUConstants.PDU_HEADER:
            return False

        pdu_header = data[0]
        pdu_type = pdu_header & PDUFlags.TYPE_MASK

        return pdu_type in (PDUType.ADV_EXT_IND.value, PDUType.ADV_AUX_IND.value)

    def _parse_extended_advertising(self, raw_data: bytes) -> None:
        if len(raw_data) < PDUConstants.MIN_EXTENDED_PDU:
            self._parse_legacy_advertising(raw_data)
            return

        pdu = self._parse_extended_pdu(raw_data)

        if not pdu:
            self._parse_legacy_advertising(raw_data)
            return

        parsed_data = ParsedADStructures()

        if pdu.payload:
            parsed_data = self._parse_ad_structures(pdu.payload)

        auxiliary_packets: list[BLEAdvertisingPDU] = []
        if pdu.extended_header and pdu.extended_header.auxiliary_pointer:
            aux_packets = self._parse_auxiliary_packets(
                pdu.extended_header.auxiliary_pointer
            )
            auxiliary_packets.extend(aux_packets)

        self.advertiser_data = DeviceAdvertiserData(
            raw_data=raw_data,
            local_name=parsed_data.local_name,
            manufacturer_data=parsed_data.manufacturer_data,
            service_uuids=parsed_data.service_uuids,
            tx_power=parsed_data.tx_power,
            flags=parsed_data.flags,
            extended_payload=pdu.payload,
            auxiliary_packets=auxiliary_packets,
        )

        if parsed_data.local_name and not self.name:
            self.name = parsed_data.local_name

    def _parse_extended_pdu(self, data: bytes) -> BLEAdvertisingPDU | None:
        if len(data) < PDUConstants.MIN_EXTENDED_PDU:
            return None

        header = int.from_bytes(data[0 : PDUConstants.PDU_HEADER], byteorder="little")
        pdu_type = header & PDUFlags.TYPE_MASK
        tx_add = bool(header & PDUFlags.TX_ADD_MASK)
        rx_add = bool(header & PDUFlags.RX_ADD_MASK)

        length = data[PDUConstants.PDU_LENGTH_OFFSET]

        if len(data) < PDUConstants.MIN_EXTENDED_PDU + length:
            return None

        extended_header_start = PDUConstants.EXTENDED_HEADER_START

        extended_header = self._parse_extended_header(data[extended_header_start:])

        if not extended_header:
            return None

        payload_start = (
            extended_header_start
            + extended_header.extended_header_length
            + PDUConstants.EXT_HEADER_LENGTH
        )
        payload_length = length - (
            extended_header.extended_header_length + PDUConstants.EXT_HEADER_LENGTH
        )

        if payload_start + payload_length > len(data):
            return None

        payload = data[payload_start : payload_start + payload_length]

        adva = extended_header.extended_advertiser_address
        targeta = extended_header.extended_target_address

        return BLEAdvertisingPDU(
            pdu_type=PDUType(pdu_type),
            tx_add=tx_add,
            rx_add=rx_add,
            length=length,
            advertiser_address=adva,
            target_address=targeta,
            payload=payload,
            extended_header=extended_header,
        )

    def _parse_extended_header(self, data: bytes) -> BLEExtendedHeader | None:
        # pylint: disable=too-many-return-statements,too-many-branches
        if len(data) < 1:
            return None

        header = BLEExtendedHeader()
        header.extended_header_length = data[0]

        if len(data) < header.extended_header_length + 1:
            return None

        adv_mode = data[1]
        header.adv_mode = adv_mode

        offset = PDUConstants.ADV_ADDR_OFFSET  # Start after length and mode bytes

        if header.has_extended_advertiser_address:
            if offset + PDUConstants.BLE_ADDR > len(data):
                return None
            header.extended_advertiser_address = data[
                offset : offset + PDUConstants.BLE_ADDR
            ]
            offset += PDUConstants.BLE_ADDR

        if header.has_extended_target_address:
            if offset + PDUConstants.BLE_ADDR > len(data):
                return None
            header.extended_target_address = data[
                offset : offset + PDUConstants.BLE_ADDR
            ]
            offset += PDUConstants.BLE_ADDR

        if header.has_cte_info:
            if offset + PDUConstants.CTE_INFO > len(data):
                return None
            header.cte_info = data[offset : offset + PDUConstants.CTE_INFO]
            offset += PDUConstants.CTE_INFO

        if header.has_advertising_data_info:
            if offset + PDUConstants.ADV_DATA_INFO > len(data):
                return None
            header.advertising_data_info = data[
                offset : offset + PDUConstants.ADV_DATA_INFO
            ]
            offset += PDUConstants.ADV_DATA_INFO

        if header.has_auxiliary_pointer:
            if offset + PDUConstants.AUX_PTR > len(data):
                return None
            header.auxiliary_pointer = data[offset : offset + PDUConstants.AUX_PTR]
            offset += PDUConstants.AUX_PTR

        if header.has_sync_info:
            if offset + PDUConstants.SYNC_INFO > len(data):
                return None
            header.sync_info = data[offset : offset + PDUConstants.SYNC_INFO]
            offset += PDUConstants.SYNC_INFO

        if header.has_tx_power:
            if offset + PDUConstants.TX_POWER > len(data):
                return None
            header.tx_power = int.from_bytes(
                data[offset : offset + PDUConstants.TX_POWER],
                byteorder="little",
                signed=True,
            )
            offset += PDUConstants.TX_POWER

        if header.has_additional_controller_data:
            header.additional_controller_advertising_data = data[offset:]

        return header

    def _parse_auxiliary_packets(self, aux_ptr: bytes) -> list[BLEAdvertisingPDU]:
        if len(aux_ptr) != PDUConstants.AUX_PTR:
            return []

        return []

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
            elif (
                ad_type == BLEAdvertisementTypes.MANUFACTURER_SPECIFIC_DATA
                and len(ad_data) >= 2
            ):
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
                parsed.tx_power = int.from_bytes(
                    ad_data[:1], byteorder="little", signed=True
                )
            elif (
                ad_type == BLEAdvertisementTypes.MANUFACTURER_SPECIFIC_DATA
                and len(ad_data) >= 2
            ):
                company_id = ad_data[0] | (ad_data[1] << 8)
                parsed.manufacturer_data[company_id] = ad_data[2:]
            elif ad_type == BLEAdvertisementTypes.APPEARANCE and len(ad_data) >= 2:
                parsed.appearance = ad_data[0] | (ad_data[1] << 8)
            elif (
                ad_type == BLEAdvertisementTypes.SERVICE_DATA_16BIT
                and len(ad_data) >= 2
            ):
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
            elif (
                ad_type
                == BLEAdvertisementTypes.PERIODIC_ADVERTISING_RESPONSE_TIMING_INFORMATION
            ):
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
            elif (
                ad_type == BLEAdvertisementTypes.ADVERTISING_INTERVAL
                and len(ad_data) >= 2
            ):
                parsed.advertising_interval = ad_data[0] | (ad_data[1] << 8)
            elif (
                ad_type == BLEAdvertisementTypes.ADVERTISING_INTERVAL_LONG
                and len(ad_data) >= 3
            ):
                parsed.advertising_interval_long = (
                    ad_data[0] | (ad_data[1] << 8) | (ad_data[2] << 16)
                )
            elif (
                ad_type == BLEAdvertisementTypes.LE_BLUETOOTH_DEVICE_ADDRESS
                and len(ad_data) >= 6
            ):
                addr_bytes = ad_data[:6]
                parsed.le_bluetooth_device_address = ":".join(
                    f"{b:02X}" for b in addr_bytes[::-1]
                )
            elif ad_type == BLEAdvertisementTypes.LE_ROLE and len(ad_data) >= 1:
                parsed.le_role = ad_data[0]
            elif ad_type == BLEAdvertisementTypes.CLASS_OF_DEVICE and len(ad_data) >= 3:
                parsed.class_of_device = (
                    ad_data[0] | (ad_data[1] << 8) | (ad_data[2] << 16)
                )
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

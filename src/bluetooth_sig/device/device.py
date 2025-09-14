"""Device class for grouping BLE device services, characteristics, encryption, and advertiser data.

This module provides a high-level Device abstraction that groups all services,
characteristics, encryption requirements, and advertiser data for a BLE device.
It integrates with the BluetoothSIGTranslator for parsing while providing a
unified view of device state.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol

from ..gatt.context import CharacteristicContext, DeviceInfo
from ..gatt.services import GattServiceRegistry
from ..gatt.services.base import BaseGattService
from ..types import (
    BLEAdvertisementTypes,
    BLEAdvertisingPDU,
    BLEExtendedHeader,
    CharacteristicDataProtocol,
    DeviceAdvertiserData,
    ParsedADStructures,
)
from ..types.data_types import CharacteristicData
from ..types.device_types import DeviceEncryption, DeviceService


class SIGTranslatorProtocol(Protocol):  # pylint: disable=too-few-public-methods
    """Protocol defining the interface needed by Device class from a SIG translator."""

    @abstractmethod
    def parse_characteristics(
        self, char_data: dict[str, bytes], ctx: CharacteristicContext | None = None
    ) -> dict[str, Any]:
        """Parse multiple characteristics at once.

        Args:
            char_data: Dictionary mapping UUIDs to raw data bytes
            ctx: Optional base CharacteristicContext

        Returns:
            Dictionary mapping UUIDs to parsed characteristic data
        """


class UnknownService(BaseGattService):
    """Generic service for unknown/unsupported service UUIDs."""

    @classmethod
    def get_expected_characteristics(cls) -> dict[str, type]:
        """No expected characteristics for unknown services."""
        return {}

    @classmethod
    def get_required_characteristics(cls) -> dict[str, type]:
        """No required characteristics for unknown services."""
        return {}


class Device:
    """High-level representation of a BLE device with all its services and data.

    This class provides a unified view of a BLE device's services, characteristics,
    encryption requirements, and advertiser data. It serves as a pure SIG standards
    translator abstraction, not a BLE connection manager.

    The Device class integrates with BluetoothSIGTranslator for characteristic parsing
    while maintaining device-level context and relationships between services and
    characteristics.
    """

    def __init__(self, address: str, translator: SIGTranslatorProtocol) -> None:
        """Initialize a Device instance.

        Args:
            address: The device MAC address or identifier
            translator: BluetoothSIGTranslator instance for parsing characteristics
        """
        self.address = address
        self.translator = translator
        self.name: str = ""
        self.services: dict[str, DeviceService] = {}
        self.encryption = DeviceEncryption()
        self.advertiser_data: DeviceAdvertiserData | None = None

    def __str__(self) -> str:
        """Return string representation of the device."""
        service_count = len(self.services)
        char_count = sum(
            len(service.characteristics) for service in self.services.values()
        )
        return f"Device({self.address}, name={self.name}, {service_count} services, {char_count} characteristics)"

    def add_service(self, service_uuid: str, characteristics: dict[str, bytes]) -> None:
        """Add a service with its characteristics to the device.

        Args:
            service_uuid: The service UUID
            characteristics: Dictionary mapping characteristic UUIDs to raw data bytes
        """
        # Get the service class for this UUID
        service_class = GattServiceRegistry.get_service_class(service_uuid)
        if not service_class:
            # Create a generic service if no specific class found
            service: BaseGattService = UnknownService()
        else:
            service = service_class()

        # Create device context for parsing
        device_info = DeviceInfo(
            address=self.address,
            name=self.name,
            manufacturer_data=self.advertiser_data.manufacturer_data
            if self.advertiser_data and self.advertiser_data.manufacturer_data
            else {},
            service_uuids=self.advertiser_data.service_uuids
            if self.advertiser_data and self.advertiser_data.service_uuids
            else [],
        )

        base_ctx = CharacteristicContext(device_info=device_info)

        # Parse all characteristics for this service
        parsed_characteristics = self.translator.parse_characteristics(
            characteristics, ctx=base_ctx
        )

        # Update encryption requirements based on parsed characteristics
        for char_data in parsed_characteristics.values():
            self.update_encryption_requirements(char_data)

        # Create device service instance
        device_service = DeviceService(
            service=service, characteristics=parsed_characteristics
        )

        # Store the service
        self.services[service_uuid] = device_service

    def parse_advertiser_data(self, raw_data: bytes) -> None:
        """Parse and store advertiser data for the device.

        Supports both legacy advertising (BLE 4.x) and extended advertising (BLE 5.0+).

        Args:
            raw_data: Raw advertisement data bytes
        """
        # First, try to detect if this is extended advertising
        if self._is_extended_advertising_pdu(raw_data):
            self._parse_extended_advertising(raw_data)
        else:
            self._parse_legacy_advertising(raw_data)

    def _is_extended_advertising_pdu(self, data: bytes) -> bool:
        """Check if the data contains an extended advertising PDU.

        Args:
            data: Raw PDU data

        Returns:
            True if this is an extended advertising PDU
        """
        if len(data) < 2:
            return False

        # Extended advertising PDUs have specific PDU types
        pdu_header = data[0]
        pdu_type = pdu_header & 0x0F  # Lower 4 bits

        # ADV_EXT_IND (0x07) and ADV_AUX_IND (0x08) are extended advertising
        return pdu_type in (0x07, 0x08)

    def _parse_extended_advertising(self, raw_data: bytes) -> None:
        """Parse extended advertising data (BLE 5.0+).

        Args:
            raw_data: Raw extended advertising PDU data
        """
        if len(raw_data) < 3:
            # Not enough data for a valid PDU
            self._parse_legacy_advertising(raw_data)
            return

        # Parse the extended advertising PDU
        pdu = self._parse_extended_pdu(raw_data)

        if not pdu:
            # Fallback to legacy parsing if extended parsing fails
            self._parse_legacy_advertising(raw_data)
            return

        # Initialize advertiser data with extended payload
        parsed_data = ParsedADStructures()

        # Parse the extended payload for AD structures
        if pdu.payload:
            parsed_data = self._parse_ad_structures(pdu.payload)

        # Handle auxiliary packets if present
        auxiliary_packets: list[BLEAdvertisingPDU] = []
        if pdu.extended_header and pdu.extended_header.auxiliary_pointer:
            aux_packets = self._parse_auxiliary_packets(
                pdu.extended_header.auxiliary_pointer
            )
            auxiliary_packets.extend(aux_packets)

        # Create extended advertiser data
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

        # Update device name from advertisement if available
        if parsed_data.local_name and not self.name:
            self.name = parsed_data.local_name

    def _parse_extended_pdu(self, data: bytes) -> BLEAdvertisingPDU | None:
        """Parse an extended advertising PDU.

        Args:
            data: Raw PDU data

        Returns:
            Parsed PDU or None if parsing fails
        """
        if len(data) < 3:
            return None

        # Parse PDU header (first 2 bytes)
        header = int.from_bytes(data[0:2], byteorder="little")
        pdu_type = header & 0x0F
        tx_add = bool((header >> 6) & 0x01)
        rx_add = bool((header >> 7) & 0x01)

        # Length field (next byte)
        length = data[2]

        if len(data) < 3 + length:
            return None  # Invalid length

        # Extended header starts after length byte
        extended_header_start = 3

        # Parse extended header
        extended_header = self._parse_extended_header(data[extended_header_start:])

        if not extended_header:
            return None

        # Calculate payload start and length
        payload_start = (
            extended_header_start + extended_header.extended_header_length + 1
        )
        payload_length = length - (extended_header.extended_header_length + 1)

        if payload_start + payload_length > len(data):
            return None

        payload = data[payload_start : payload_start + payload_length]

        # Extract addresses if present
        adva = extended_header.extended_advertiser_address
        targeta = extended_header.extended_target_address

        return BLEAdvertisingPDU(
            pdu_type=pdu_type,
            tx_add=tx_add,
            rx_add=rx_add,
            length=length,
            advertiser_address=adva,
            target_address=targeta,
            payload=payload,
            extended_header=extended_header,
        )

    def _parse_extended_header(self, data: bytes) -> BLEExtendedHeader | None:
        """Parse extended advertising header.

        Args:
            data: Extended header data

        Returns:
            Parsed extended header or None if parsing fails
        """
        # pylint: disable=too-many-return-statements,too-many-branches
        if len(data) < 1:
            return None

        header = BLEExtendedHeader()
        header.extended_header_length = data[0]

        if len(data) < header.extended_header_length + 1:
            return None

        # Parse header flags (next byte after length)
        adv_mode = data[1]
        header.adv_mode = adv_mode

        # Parse optional fields based on mode bits
        offset = 2  # Start after length and mode bytes

        if header.has_extended_advertiser_address:
            if offset + 6 > len(data):
                return None
            header.extended_advertiser_address = data[offset : offset + 6]
            offset += 6

        if header.has_extended_target_address:
            if offset + 6 > len(data):
                return None
            header.extended_target_address = data[offset : offset + 6]
            offset += 6

        if header.has_cte_info:
            if offset + 1 > len(data):
                return None
            header.cte_info = data[offset : offset + 1]
            offset += 1

        if header.has_advertising_data_info:
            if offset + 2 > len(data):
                return None
            header.advertising_data_info = data[offset : offset + 2]
            offset += 2

        if header.has_auxiliary_pointer:
            if offset + 3 > len(data):
                return None
            header.auxiliary_pointer = data[offset : offset + 3]
            offset += 3

        if header.has_sync_info:
            if offset + 18 > len(data):
                return None
            header.sync_info = data[offset : offset + 18]
            offset += 18

        if header.has_tx_power:
            if offset + 1 > len(data):
                return None
            header.tx_power = int.from_bytes(
                data[offset : offset + 1], byteorder="little", signed=True
            )
            offset += 1

        if header.has_additional_controller_data:
            # Remaining data is additional controller advertising data
            header.additional_controller_advertising_data = data[offset:]

        return header

    def _parse_auxiliary_packets(self, aux_ptr: bytes) -> list[BLEAdvertisingPDU]:
        """Parse auxiliary packets pointed to by auxiliary pointer.

        Args:
            aux_ptr: Auxiliary pointer data (3 bytes)

        Returns:
            List of parsed auxiliary PDUs
        """
        if len(aux_ptr) != 3:
            return []

        # Parse auxiliary pointer (3 bytes)
        # Format: [Channel Index (6 bits)] [CA (1 bit)] [Offset Units (1 bit)] [AUX Offset (13 bits)] [AUX PHY (3 bits)]
        # aux_ptr_value = int.from_bytes(aux_ptr, byteorder="little")

        # Extract fields from auxiliary pointer (parsed but not used in this implementation)
        # These variables are placeholders for future auxiliary packet parsing
        # channel_index = aux_ptr_value & 0x3F  # 6 bits
        # ca = bool((aux_ptr_value >> 6) & 0x01)  # 1 bit
        # offset_units = bool((aux_ptr_value >> 7) & 0x01)  # 1 bit
        # aux_offset = (aux_ptr_value >> 8) & 0x1FFF  # 13 bits
        # aux_phy = (aux_ptr_value >> 21) & 0x07  # 3 bits

        # Note: In a real implementation, we would need to:
        # 1. Calculate the timing for when to listen on the auxiliary channel
        # 2. Switch to the specified channel (channel_index)
        # 3. Listen for the auxiliary PDU at the calculated time
        # 4. Parse the received auxiliary PDU
        #
        # For this implementation, we'll return an empty list since we don't have
        # access to the actual radio hardware or timing information needed to
        # receive auxiliary packets.

        return []

    def _parse_legacy_advertising(self, raw_data: bytes) -> None:
        """Parse legacy advertising data (BLE 4.x).

        Args:
            raw_data: Raw legacy advertisement data bytes
        """
        # BLE Legacy Advertisement Data Format:
        # Each AD structure: [Length (1 byte)] [AD Type (1 byte)] [AD Data (Length-1 bytes)]

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

            if ad_type == BLEAdvertisementTypes.FLAGS and len(ad_data) >= 1:  # Flags
                flags = ad_data[0]
            elif ad_type in (
                BLEAdvertisementTypes.INCOMPLETE_16BIT_SERVICE_UUIDS,
                BLEAdvertisementTypes.COMPLETE_16BIT_SERVICE_UUIDS,
            ):  # Service UUIDs (16-bit)
                # Parse 16-bit UUIDs (little endian)
                for j in range(0, len(ad_data), 2):
                    if j + 1 < len(ad_data):
                        uuid_short = ad_data[j] | (ad_data[j + 1] << 8)
                        service_uuids.append(f"{uuid_short:04X}")
            elif ad_type in (
                BLEAdvertisementTypes.SHORTENED_LOCAL_NAME,
                BLEAdvertisementTypes.COMPLETE_LOCAL_NAME,
            ):  # Local Name
                try:
                    local_name = ad_data.decode("utf-8")
                except UnicodeDecodeError:
                    local_name = ad_data.hex()
            elif (
                ad_type == BLEAdvertisementTypes.TX_POWER_LEVEL and len(ad_data) >= 1
            ):  # Tx Power
                tx_power = int.from_bytes(ad_data[:1], byteorder="little", signed=True)
            elif (
                ad_type == BLEAdvertisementTypes.MANUFACTURER_SPECIFIC_DATA
                and len(ad_data) >= 2
            ):  # Manufacturer Data
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

        # Update device name from advertisement if available
        if local_name and not self.name:
            self.name = local_name

    def _parse_ad_structures(self, data: bytes) -> ParsedADStructures:
        """Parse AD structures from advertisement data.

        Args:
            data: Raw AD data

        Returns:
            ParsedADStructures with parsed AD structure data
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
                # Parse 6-byte addresses
                for j in range(0, len(ad_data), 6):
                    if j + 5 < len(ad_data):
                        addr_bytes = ad_data[j : j + 6]
                        addr_str = ":".join(
                            f"{b:02X}" for b in addr_bytes[::-1]
                        )  # Little endian to big endian
                        parsed.public_target_address.append(addr_str)
            elif ad_type == BLEAdvertisementTypes.RANDOM_TARGET_ADDRESS:
                # Parse 6-byte addresses
                for j in range(0, len(ad_data), 6):
                    if j + 5 < len(ad_data):
                        addr_bytes = ad_data[j : j + 6]
                        addr_str = ":".join(
                            f"{b:02X}" for b in addr_bytes[::-1]
                        )  # Little endian to big endian
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
        self, service_uuid: str, char_uuid: str
    ) -> CharacteristicDataProtocol | None:
        """Get parsed characteristic data for a specific characteristic.

        Args:
            service_uuid: The service UUID
            char_uuid: The characteristic UUID

        Returns:
            CharacteristicData if found, None otherwise
        """
        service = self.services.get(service_uuid)
        if service:
            return service.characteristics.get(char_uuid)
        return None

    def update_encryption_requirements(self, char_data: CharacteristicData) -> None:
        """Update encryption requirements based on characteristic parsing results.

        Args:
            char_data: Parsed characteristic data that may indicate encryption needs
        """
        # Check if characteristic requires encryption based on properties
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

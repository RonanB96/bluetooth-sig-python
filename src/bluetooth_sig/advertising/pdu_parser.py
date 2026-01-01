"""BLE Advertising PDU parser.

This module provides a parser for BLE advertising PDU data packets,
extracting device information, manufacturer data, and service UUIDs
from both legacy and extended advertising formats.

This is the low-level BLE spec parser. For interpreting vendor-specific
sensor data (e.g., Xiaomi, RuuviTag, BTHome), see the AdvertisingDataInterpreter
base class.
"""

from __future__ import annotations

import logging

from bluetooth_sig.gatt.characteristics.utils import DataParser
from bluetooth_sig.registry.company_identifiers import company_identifiers_registry
from bluetooth_sig.registry.core.ad_types import ad_types_registry
from bluetooth_sig.registry.core.appearance_values import appearance_values_registry
from bluetooth_sig.registry.core.class_of_device import class_of_device_registry
from bluetooth_sig.types import (
    AdvertisingData,
    AdvertisingDataStructures,
    BLEAdvertisingFlags,
    BLEAdvertisingPDU,
    BLEExtendedHeader,
    ExtendedAdvertisingData,
    PDUHeaderFlags,
    PDULayout,
    PDUType,
)
from bluetooth_sig.types.ad_types_constants import ADType
from bluetooth_sig.types.appearance import AppearanceData
from bluetooth_sig.types.uri import URIData
from bluetooth_sig.types.uuid import BluetoothUUID

logger = logging.getLogger(__name__)


class AdvertisingPDUParser:  # pylint: disable=too-few-public-methods
    """Parser for BLE advertising PDU data packets.

    Parses raw BLE advertising PDU bytes into structured AdvertisingData,
    handling both legacy and extended advertising formats.

    This is the low-level parsing layer that extracts:
    - Manufacturer data (company_id → payload)
    - Service data (UUID → payload)
    - Flags, local name, appearance, TX power
    - Extended advertising fields (BLE 5.0+)

    For vendor-specific interpretation (e.g., BTHome sensor values),
    use AdvertisingDataInterpreter subclasses.
    """

    def parse_advertising_data(self, raw_data: bytes) -> AdvertisingData:
        """Parse raw advertising data and return structured information.

        Args:
            raw_data: Raw bytes from BLE advertising packet

        Returns:
            AdvertisingData with parsed information

        """
        if self._is_extended_advertising_pdu(raw_data):
            return self._parse_extended_advertising(raw_data)
        return self._parse_legacy_advertising(raw_data)

    def _is_extended_advertising_pdu(self, data: bytes) -> bool:
        """Check if the advertising data is an extended advertising PDU.

        Args:
            data: Raw advertising data bytes

        Returns:
            True if extended advertising PDU, False otherwise

        """
        if len(data) < PDULayout.PDU_HEADER:
            return False

        pdu_header = data[0]
        pdu_type = pdu_header & PDUHeaderFlags.TYPE_MASK

        return pdu_type in (PDUType.ADV_EXT_IND.value, PDUType.ADV_AUX_IND.value)

    def _parse_extended_advertising(self, raw_data: bytes) -> AdvertisingData:
        """Parse extended advertising data.

        Args:
            raw_data: Raw extended advertising data

        Returns:
            Parsed AdvertisingData

        """
        if len(raw_data) < PDULayout.MIN_EXTENDED_PDU:
            return self._parse_legacy_advertising(raw_data)

        pdu = self._parse_extended_pdu(raw_data)

        if not pdu:
            return self._parse_legacy_advertising(raw_data)

        parsed_data = AdvertisingDataStructures()

        if pdu.payload:
            parsed_data = self._parse_ad_structures(pdu.payload)

        auxiliary_packets: list[BLEAdvertisingPDU] = []
        if pdu.extended_header and pdu.extended_header.auxiliary_pointer:
            aux_packets = self._parse_auxiliary_packets(pdu.extended_header.auxiliary_pointer)
            auxiliary_packets.extend(aux_packets)

        return AdvertisingData(
            raw_data=raw_data,
            ad_structures=parsed_data,
            extended=ExtendedAdvertisingData(
                extended_payload=pdu.payload,
                auxiliary_packets=auxiliary_packets,
            ),
        )

    def _parse_extended_pdu(self, data: bytes) -> BLEAdvertisingPDU | None:
        """Parse extended PDU header and payload.

        Args:
            data: Raw PDU data

        Returns:
            Parsed BLEAdvertisingPDU or None if invalid

        """
        if len(data) < PDULayout.MIN_EXTENDED_PDU:
            return None

        header = int.from_bytes(data[0 : PDULayout.PDU_HEADER], byteorder="little")
        pdu_type = header & PDUHeaderFlags.TYPE_MASK
        tx_add = bool(header & PDUHeaderFlags.TX_ADD_MASK)
        rx_add = bool(header & PDUHeaderFlags.RX_ADD_MASK)

        length = data[PDULayout.PDU_LENGTH_OFFSET]

        if len(data) < PDULayout.MIN_EXTENDED_PDU + length:
            return None

        extended_header_start = PDULayout.EXTENDED_HEADER_START

        extended_header = self._parse_extended_header(data[extended_header_start:])

        if not extended_header:
            return None

        payload_start = extended_header_start + extended_header.extended_header_length + PDULayout.EXT_HEADER_LENGTH
        payload_length = length - (extended_header.extended_header_length + PDULayout.EXT_HEADER_LENGTH)

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
        """Parse extended header from PDU data.

        Args:
            data: Extended header data

        Returns:
            Parsed BLEExtendedHeader or None if invalid

        """
        # pylint: disable=too-many-return-statements,too-many-branches
        if len(data) < 1:
            return None

        header = BLEExtendedHeader()
        header.extended_header_length = data[0]

        if len(data) < header.extended_header_length + 1:
            return None

        adv_mode = data[1]
        header.adv_mode = adv_mode

        offset = PDULayout.ADV_ADDR_OFFSET  # Start after length and mode bytes

        if header.has_extended_advertiser_address:
            if offset + PDULayout.BLE_ADDR > len(data):
                return None
            header.extended_advertiser_address = data[offset : offset + PDULayout.BLE_ADDR]
            offset += PDULayout.BLE_ADDR

        if header.has_extended_target_address:
            if offset + PDULayout.BLE_ADDR > len(data):
                return None
            header.extended_target_address = data[offset : offset + PDULayout.BLE_ADDR]
            offset += PDULayout.BLE_ADDR

        if header.has_cte_info:
            if offset + PDULayout.CTE_INFO > len(data):
                return None
            header.cte_info = data[offset : offset + PDULayout.CTE_INFO]
            offset += PDULayout.CTE_INFO

        if header.has_advertising_data_info:
            if offset + PDULayout.ADV_DATA_INFO > len(data):
                return None
            header.advertising_data_info = data[offset : offset + PDULayout.ADV_DATA_INFO]
            offset += PDULayout.ADV_DATA_INFO

        if header.has_auxiliary_pointer:
            if offset + PDULayout.AUX_PTR > len(data):
                return None
            header.auxiliary_pointer = data[offset : offset + PDULayout.AUX_PTR]
            offset += PDULayout.AUX_PTR

        if header.has_sync_info:
            if offset + PDULayout.SYNC_INFO > len(data):
                return None
            header.sync_info = data[offset : offset + PDULayout.SYNC_INFO]
            offset += PDULayout.SYNC_INFO

        if header.has_tx_power:
            if offset + PDULayout.TX_POWER > len(data):
                return None
            header.tx_power = int.from_bytes(
                data[offset : offset + PDULayout.TX_POWER],
                byteorder="little",
                signed=True,
            )
            offset += PDULayout.TX_POWER

        if header.has_additional_controller_data:
            header.additional_controller_advertising_data = data[offset:]

        return header

    def _parse_auxiliary_packets(self, aux_ptr: bytes) -> list[BLEAdvertisingPDU]:
        """Parse auxiliary packets referenced by auxiliary pointer.

        Args:
            aux_ptr: Auxiliary pointer data

        Returns:
            List of auxiliary packets (currently returns empty list)

        """
        if len(aux_ptr) != PDULayout.AUX_PTR:
            return []

        return []

    def _parse_legacy_advertising(self, raw_data: bytes) -> AdvertisingData:
        """Parse legacy advertising data.

        Args:
            raw_data: Raw legacy advertising data

        Returns:
            Parsed AdvertisingData

        """
        parsed_data = self._parse_ad_structures(raw_data)
        return AdvertisingData(
            raw_data=raw_data,
            ad_structures=parsed_data,
        )

    @staticmethod
    def _parse_address_list(ad_data: bytes) -> list[str]:
        """Parse list of 6-byte Bluetooth addresses from raw data.

        Args:
            ad_data: Raw address data (multiple 6-byte addresses)

        Returns:
            List of formatted address strings (XX:XX:XX:XX:XX:XX)
        """
        addresses: list[str] = []
        for j in range(0, len(ad_data), 6):
            if j + 5 < len(ad_data):
                addr_bytes = ad_data[j : j + 6]
                addresses.append(":".join(f"{b:02X}" for b in addr_bytes[::-1]))
        return addresses

    @staticmethod
    def _parse_16bit_uuids(ad_data: bytes) -> list[BluetoothUUID]:
        """Parse list of 16-bit service UUIDs from raw data.

        Args:
            ad_data: Raw UUID data

        Returns:
            List of BluetoothUUID objects
        """
        uuids: list[BluetoothUUID] = []
        for j in range(0, len(ad_data), 2):
            if j + 1 < len(ad_data):
                uuid_short = DataParser.parse_int16(ad_data, j, signed=False)
                uuids.append(BluetoothUUID(uuid_short))
        return uuids

    @staticmethod
    def _parse_128bit_uuids(ad_data: bytes) -> list[BluetoothUUID]:
        """Parse list of 128-bit service UUIDs from raw data.

        Args:
            ad_data: Raw UUID data

        Returns:
            List of BluetoothUUID objects
        """
        uuids: list[BluetoothUUID] = []
        for j in range(0, len(ad_data), 16):
            if j + 15 < len(ad_data):
                uuids.append(BluetoothUUID(ad_data[j : j + 16].hex().upper()))
        return uuids

    def _parse_manufacturer_data(self, ad_data: bytes, parsed: AdvertisingDataStructures) -> None:
        """Parse manufacturer-specific data and resolve company name.

        Args:
            ad_data: Raw manufacturer-specific data bytes
            parsed: AdvertisingDataStructures object to update

        """
        company_id = DataParser.parse_int16(ad_data, 0, signed=False)
        parsed.core.manufacturer_data[company_id] = ad_data[2:]
        # Resolve company name from registry
        company_name = company_identifiers_registry.get_company_name(company_id)
        if company_name is not None:
            parsed.core.manufacturer_names[company_id] = company_name

    def _parse_ad_structures(self, data: bytes) -> AdvertisingDataStructures:
        """Parse advertising data structures from raw bytes.

        Args:
            data: Raw advertising data payload

        Returns:
            AdvertisingDataStructures object with extracted data

        """
        # pylint: disable=too-many-branches,too-many-statements
        parsed = AdvertisingDataStructures()

        i = 0
        while i < len(data):
            if i + 1 >= len(data):
                break

            length = data[i]
            if length == 0 or i + length + 1 > len(data):
                break

            ad_type = data[i + 1]
            ad_data = data[i + 2 : i + length + 1]

            # Warn about unknown AD types
            if not ad_types_registry.is_known_ad_type(ad_type):
                logger.warning("Unknown AD type encountered: 0x%02X", ad_type)

            if ad_type == ADType.FLAGS and len(ad_data) >= 1:
                parsed.properties.flags = BLEAdvertisingFlags(ad_data[0])
            elif ad_type in (
                ADType.INCOMPLETE_16BIT_SERVICE_UUIDS,
                ADType.COMPLETE_16BIT_SERVICE_UUIDS,
            ):
                parsed.core.service_uuids.extend(self._parse_16bit_uuids(ad_data))
            elif ad_type in (
                ADType.INCOMPLETE_128BIT_SERVICE_UUIDS,
                ADType.COMPLETE_128BIT_SERVICE_UUIDS,
            ):
                parsed.core.service_uuids.extend(self._parse_128bit_uuids(ad_data))
            elif ad_type in (ADType.SHORTENED_LOCAL_NAME, ADType.COMPLETE_LOCAL_NAME):
                try:
                    parsed.core.local_name = ad_data.decode("utf-8")
                except UnicodeDecodeError:
                    parsed.core.local_name = ad_data.hex()
            elif ad_type == ADType.TX_POWER_LEVEL and len(ad_data) >= 1:
                parsed.properties.tx_power = int.from_bytes(ad_data[:1], byteorder="little", signed=True)
            elif ad_type == ADType.MANUFACTURER_SPECIFIC_DATA and len(ad_data) >= 2:
                self._parse_manufacturer_data(ad_data, parsed)
            elif ad_type == ADType.APPEARANCE and len(ad_data) >= 2:
                raw_value = DataParser.parse_int16(ad_data, 0, signed=False)
                appearance_info = appearance_values_registry.get_appearance_info(raw_value)
                parsed.properties.appearance = AppearanceData(raw_value=raw_value, info=appearance_info)
            elif ad_type == ADType.SERVICE_DATA_16BIT and len(ad_data) >= 2:
                service_uuid = BluetoothUUID(DataParser.parse_int16(ad_data, 0, signed=False))
                parsed.core.service_data[service_uuid] = ad_data[2:]
                if service_uuid not in parsed.core.service_uuids:
                    parsed.core.service_uuids.append(service_uuid)
            elif ad_type == ADType.SERVICE_DATA_128BIT and len(ad_data) >= 16:
                service_uuid = BluetoothUUID(ad_data[:16].hex().upper())
                parsed.core.service_data[service_uuid] = ad_data[16:]
                if service_uuid not in parsed.core.service_uuids:
                    parsed.core.service_uuids.append(service_uuid)
            elif ad_type == ADType.URI:
                parsed.core.uri_data = URIData.from_raw_data(ad_data)
            elif ad_type == ADType.INDOOR_POSITIONING:
                parsed.location.indoor_positioning = ad_data
            elif ad_type == ADType.TRANSPORT_DISCOVERY_DATA:
                parsed.location.transport_discovery_data = ad_data
            elif ad_type == ADType.LE_SUPPORTED_FEATURES:
                parsed.properties.le_supported_features = ad_data
            elif ad_type == ADType.ENCRYPTED_ADVERTISING_DATA:
                parsed.security.encrypted_advertising_data = ad_data
            elif ad_type == ADType.PERIODIC_ADVERTISING_RESPONSE_TIMING_INFORMATION:
                parsed.mesh.periodic_advertising_response_timing = ad_data
            elif ad_type == ADType.ELECTRONIC_SHELF_LABEL:
                parsed.mesh.electronic_shelf_label = ad_data
            elif ad_type == ADType.THREE_D_INFORMATION_DATA:
                parsed.location.three_d_information = ad_data
            elif ad_type == ADType.BROADCAST_NAME:
                try:
                    parsed.mesh.broadcast_name = ad_data.decode("utf-8")
                except UnicodeDecodeError:
                    parsed.mesh.broadcast_name = ad_data.hex()
            elif ad_type == ADType.BROADCAST_CODE:
                parsed.mesh.broadcast_code = ad_data
            elif ad_type == ADType.BIGINFO:
                parsed.mesh.biginfo = ad_data
            elif ad_type == ADType.MESH_MESSAGE:
                parsed.mesh.mesh_message = ad_data
            elif ad_type == ADType.MESH_BEACON:
                parsed.mesh.mesh_beacon = ad_data
            elif ad_type == ADType.PUBLIC_TARGET_ADDRESS:
                parsed.directed.public_target_address.extend(self._parse_address_list(ad_data))
            elif ad_type == ADType.RANDOM_TARGET_ADDRESS:
                parsed.directed.random_target_address.extend(self._parse_address_list(ad_data))
            elif ad_type == ADType.ADVERTISING_INTERVAL and len(ad_data) >= 2:
                parsed.directed.advertising_interval = DataParser.parse_int16(ad_data, 0, signed=False)
            elif ad_type == ADType.ADVERTISING_INTERVAL_LONG and len(ad_data) >= 3:
                parsed.directed.advertising_interval_long = int.from_bytes(
                    ad_data[:3], byteorder="little", signed=False
                )
            elif ad_type == ADType.LE_BLUETOOTH_DEVICE_ADDRESS and len(ad_data) >= 6:
                addr_bytes = ad_data[:6]
                parsed.directed.le_bluetooth_device_address = ":".join(f"{b:02X}" for b in addr_bytes[::-1])
            elif ad_type == ADType.LE_ROLE and len(ad_data) >= 1:
                parsed.properties.le_role = ad_data[0]
            elif ad_type == ADType.CLASS_OF_DEVICE and len(ad_data) >= 3:
                raw_cod = int.from_bytes(ad_data[:3], byteorder="little", signed=False)
                parsed.properties.class_of_device = class_of_device_registry.decode_class_of_device(raw_cod)
            elif ad_type == ADType.SIMPLE_PAIRING_HASH_C:
                parsed.oob_security.simple_pairing_hash_c = ad_data
            elif ad_type == ADType.SIMPLE_PAIRING_RANDOMIZER_R:
                parsed.oob_security.simple_pairing_randomizer_r = ad_data
            elif ad_type == ADType.SECURITY_MANAGER_TK_VALUE:
                parsed.oob_security.security_manager_tk_value = ad_data
            elif ad_type == ADType.SECURITY_MANAGER_OUT_OF_BAND_FLAGS:
                parsed.oob_security.security_manager_oob_flags = ad_data
            elif ad_type == ADType.SLAVE_CONNECTION_INTERVAL_RANGE:
                parsed.directed.peripheral_connection_interval_range = ad_data
            elif ad_type == ADType.SECURE_CONNECTIONS_CONFIRMATION_VALUE:
                parsed.oob_security.secure_connections_confirmation = ad_data
            elif ad_type == ADType.SECURE_CONNECTIONS_RANDOM_VALUE:
                parsed.oob_security.secure_connections_random = ad_data
            elif ad_type == ADType.CHANNEL_MAP_UPDATE_INDICATION:
                parsed.location.channel_map_update_indication = ad_data
            elif ad_type == ADType.PB_ADV:
                parsed.mesh.pb_adv = ad_data
            elif ad_type == ADType.RESOLVABLE_SET_IDENTIFIER:
                parsed.security.resolvable_set_identifier = ad_data

            i += length + 1

        return parsed

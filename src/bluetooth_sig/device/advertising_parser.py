"""Advertising data parser for BLE devices.

This module provides a dedicated parser for BLE advertising data
packets, extracting device information, manufacturer data, and service
UUIDs from both legacy and extended advertising formats.
"""

from __future__ import annotations

import logging

from ..gatt.characteristics.utils import DataParser
from ..registry import ad_types_registry, appearance_values_registry, class_of_device_registry
from ..types import (
    BLEAdvertisingFlags,
    BLEAdvertisingPDU,
    BLEExtendedHeader,
    DeviceAdvertiserData,
    ParsedADStructures,
    PDUConstants,
    PDUFlags,
    PDUType,
)
from ..types.ad_types_constants import ADType
from ..types.appearance import AppearanceData

logger = logging.getLogger(__name__)


class AdvertisingParser:  # pylint: disable=too-few-public-methods
    """Parser for BLE advertising data packets.

    Handles both legacy and extended advertising PDU formats, extracting
    device information, manufacturer data, and service UUIDs.
    """

    def parse_advertising_data(self, raw_data: bytes) -> DeviceAdvertiserData:
        """Parse raw advertising data and return structured information.

        Args:
            raw_data: Raw bytes from BLE advertising packet

        Returns:
            DeviceAdvertiserData with parsed information

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
        if len(data) < PDUConstants.PDU_HEADER:
            return False

        pdu_header = data[0]
        pdu_type = pdu_header & PDUFlags.TYPE_MASK

        return pdu_type in (PDUType.ADV_EXT_IND.value, PDUType.ADV_AUX_IND.value)

    def _parse_extended_advertising(self, raw_data: bytes) -> DeviceAdvertiserData:
        """Parse extended advertising data.

        Args:
            raw_data: Raw extended advertising data

        Returns:
            Parsed DeviceAdvertiserData

        """
        if len(raw_data) < PDUConstants.MIN_EXTENDED_PDU:
            return self._parse_legacy_advertising(raw_data)

        pdu = self._parse_extended_pdu(raw_data)

        if not pdu:
            return self._parse_legacy_advertising(raw_data)

        parsed_data = ParsedADStructures()

        if pdu.payload:
            parsed_data = self._parse_ad_structures(pdu.payload)

        auxiliary_packets: list[BLEAdvertisingPDU] = []
        if pdu.extended_header and pdu.extended_header.auxiliary_pointer:
            aux_packets = self._parse_auxiliary_packets(pdu.extended_header.auxiliary_pointer)
            auxiliary_packets.extend(aux_packets)

        return DeviceAdvertiserData(
            raw_data=raw_data,
            local_name=parsed_data.local_name,
            manufacturer_data=parsed_data.manufacturer_data,
            service_uuids=parsed_data.service_uuids,
            tx_power=parsed_data.tx_power,
            flags=parsed_data.flags,
            appearance=parsed_data.appearance,
            service_data=parsed_data.service_data,
            solicited_service_uuids=parsed_data.solicited_service_uuids,
            uri=parsed_data.uri,
            indoor_positioning=parsed_data.indoor_positioning,
            transport_discovery_data=parsed_data.transport_discovery_data,
            le_supported_features=parsed_data.le_supported_features,
            encrypted_advertising_data=parsed_data.encrypted_advertising_data,
            periodic_advertising_response_timing=parsed_data.periodic_advertising_response_timing,
            electronic_shelf_label=parsed_data.electronic_shelf_label,
            three_d_information=parsed_data.three_d_information,
            broadcast_name=parsed_data.broadcast_name,
            biginfo=parsed_data.biginfo,
            mesh_message=parsed_data.mesh_message,
            mesh_beacon=parsed_data.mesh_beacon,
            public_target_address=parsed_data.public_target_address,
            random_target_address=parsed_data.random_target_address,
            advertising_interval=parsed_data.advertising_interval,
            advertising_interval_long=parsed_data.advertising_interval_long,
            le_bluetooth_device_address=parsed_data.le_bluetooth_device_address,
            le_role=parsed_data.le_role,
            class_of_device=parsed_data.class_of_device,
            class_of_device_info=parsed_data.class_of_device_info,
            simple_pairing_hash_c=parsed_data.simple_pairing_hash_c,
            simple_pairing_randomizer_r=parsed_data.simple_pairing_randomizer_r,
            security_manager_tk_value=parsed_data.security_manager_tk_value,
            security_manager_out_of_band_flags=parsed_data.security_manager_out_of_band_flags,
            slave_connection_interval_range=parsed_data.slave_connection_interval_range,
            secure_connections_confirmation=parsed_data.secure_connections_confirmation,
            secure_connections_random=parsed_data.secure_connections_random,
            channel_map_update_indication=parsed_data.channel_map_update_indication,
            pb_adv=parsed_data.pb_adv,
            resolvable_set_identifier=parsed_data.resolvable_set_identifier,
            extended_payload=pdu.payload,
            auxiliary_packets=auxiliary_packets,
        )

    def _parse_extended_pdu(self, data: bytes) -> BLEAdvertisingPDU | None:
        """Parse extended PDU header and payload.

        Args:
            data: Raw PDU data

        Returns:
            Parsed BLEAdvertisingPDU or None if invalid

        """
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

        payload_start = extended_header_start + extended_header.extended_header_length + PDUConstants.EXT_HEADER_LENGTH
        payload_length = length - (extended_header.extended_header_length + PDUConstants.EXT_HEADER_LENGTH)

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

        offset = PDUConstants.ADV_ADDR_OFFSET  # Start after length and mode bytes

        if header.has_extended_advertiser_address:
            if offset + PDUConstants.BLE_ADDR > len(data):
                return None
            header.extended_advertiser_address = data[offset : offset + PDUConstants.BLE_ADDR]
            offset += PDUConstants.BLE_ADDR

        if header.has_extended_target_address:
            if offset + PDUConstants.BLE_ADDR > len(data):
                return None
            header.extended_target_address = data[offset : offset + PDUConstants.BLE_ADDR]
            offset += PDUConstants.BLE_ADDR

        if header.has_cte_info:
            if offset + PDUConstants.CTE_INFO > len(data):
                return None
            header.cte_info = data[offset : offset + PDUConstants.CTE_INFO]
            offset += PDUConstants.CTE_INFO

        if header.has_advertising_data_info:
            if offset + PDUConstants.ADV_DATA_INFO > len(data):
                return None
            header.advertising_data_info = data[offset : offset + PDUConstants.ADV_DATA_INFO]
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
        """Parse auxiliary packets referenced by auxiliary pointer.

        Args:
            aux_ptr: Auxiliary pointer data

        Returns:
            List of auxiliary packets (currently returns empty list)

        """
        if len(aux_ptr) != PDUConstants.AUX_PTR:
            return []

        return []

    def _parse_legacy_advertising(self, raw_data: bytes) -> DeviceAdvertiserData:
        """Parse legacy advertising data.

        Args:
            raw_data: Raw legacy advertising data

        Returns:
            Parsed DeviceAdvertiserData

        """
        parsed_data = self._parse_ad_structures(raw_data)

        return DeviceAdvertiserData(
            raw_data=raw_data,
            local_name=parsed_data.local_name,
            manufacturer_data=parsed_data.manufacturer_data,
            service_uuids=parsed_data.service_uuids,
            tx_power=parsed_data.tx_power if parsed_data.tx_power != 0 else None,
            flags=parsed_data.flags if parsed_data.flags != 0 else None,
            appearance=parsed_data.appearance,
            service_data=parsed_data.service_data,
            solicited_service_uuids=parsed_data.solicited_service_uuids,
            uri=parsed_data.uri,
            indoor_positioning=parsed_data.indoor_positioning,
            transport_discovery_data=parsed_data.transport_discovery_data,
            le_supported_features=parsed_data.le_supported_features,
            encrypted_advertising_data=parsed_data.encrypted_advertising_data,
            periodic_advertising_response_timing=parsed_data.periodic_advertising_response_timing,
            electronic_shelf_label=parsed_data.electronic_shelf_label,
            three_d_information=parsed_data.three_d_information,
            broadcast_name=parsed_data.broadcast_name,
            biginfo=parsed_data.biginfo,
            mesh_message=parsed_data.mesh_message,
            mesh_beacon=parsed_data.mesh_beacon,
            public_target_address=parsed_data.public_target_address,
            random_target_address=parsed_data.random_target_address,
            advertising_interval=parsed_data.advertising_interval,
            advertising_interval_long=parsed_data.advertising_interval_long,
            le_bluetooth_device_address=parsed_data.le_bluetooth_device_address,
            le_role=parsed_data.le_role,
            class_of_device=parsed_data.class_of_device,
            class_of_device_info=parsed_data.class_of_device_info,
            simple_pairing_hash_c=parsed_data.simple_pairing_hash_c,
            simple_pairing_randomizer_r=parsed_data.simple_pairing_randomizer_r,
            security_manager_tk_value=parsed_data.security_manager_tk_value,
            security_manager_out_of_band_flags=parsed_data.security_manager_out_of_band_flags,
            slave_connection_interval_range=parsed_data.slave_connection_interval_range,
            secure_connections_confirmation=parsed_data.secure_connections_confirmation,
            secure_connections_random=parsed_data.secure_connections_random,
            channel_map_update_indication=parsed_data.channel_map_update_indication,
            pb_adv=parsed_data.pb_adv,
            resolvable_set_identifier=parsed_data.resolvable_set_identifier,
        )

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

            # Warn about unknown AD types
            if not ad_types_registry.is_known_ad_type(ad_type):
                logger.warning("Unknown AD type encountered: 0x%02X", ad_type)

            if ad_type == ADType.FLAGS and len(ad_data) >= 1:
                parsed.flags = BLEAdvertisingFlags(ad_data[0])
            elif ad_type in (
                ADType.INCOMPLETE_16BIT_SERVICE_UUIDS,
                ADType.COMPLETE_16BIT_SERVICE_UUIDS,
            ):
                for j in range(0, len(ad_data), 2):
                    if j + 1 < len(ad_data):
                        uuid_short = DataParser.parse_int16(ad_data, j, signed=False)
                        parsed.service_uuids.append(f"{uuid_short:04X}")
            elif ad_type in (ADType.SHORTENED_LOCAL_NAME, ADType.COMPLETE_LOCAL_NAME):
                try:
                    parsed.local_name = ad_data.decode("utf-8")
                except UnicodeDecodeError:
                    parsed.local_name = ad_data.hex()
            elif ad_type == ADType.TX_POWER_LEVEL and len(ad_data) >= 1:
                parsed.tx_power = int.from_bytes(ad_data[:1], byteorder="little", signed=True)
            elif ad_type == ADType.MANUFACTURER_SPECIFIC_DATA and len(ad_data) >= 2:
                company_id = DataParser.parse_int16(ad_data, 0, signed=False)
                parsed.manufacturer_data[company_id] = ad_data[2:]
            elif ad_type == ADType.APPEARANCE and len(ad_data) >= 2:
                raw_value = DataParser.parse_int16(ad_data, 0, signed=False)
                appearance_info = appearance_values_registry.get_appearance_info(raw_value)
                parsed.appearance = AppearanceData(raw_value=raw_value, info=appearance_info)
            elif ad_type == ADType.SERVICE_DATA_16BIT and len(ad_data) >= 2:
                service_uuid = f"{DataParser.parse_int16(ad_data, 0, signed=False):04X}"
                parsed.service_data[service_uuid] = ad_data[2:]
            elif ad_type == ADType.SERVICE_DATA_16BIT and len(ad_data) >= 2:
                service_uuid = f"{DataParser.parse_int16(ad_data, 0, signed=False):04X}"
                parsed.service_data[service_uuid] = ad_data[2:]
            elif ad_type == ADType.URI:
                try:
                    parsed.uri = ad_data.decode("utf-8")
                except UnicodeDecodeError:
                    parsed.uri = ad_data.hex()
            elif ad_type == ADType.INDOOR_POSITIONING:
                parsed.indoor_positioning = ad_data
            elif ad_type == ADType.TRANSPORT_DISCOVERY_DATA:
                parsed.transport_discovery_data = ad_data
            elif ad_type == ADType.LE_SUPPORTED_FEATURES:
                parsed.le_supported_features = ad_data
            elif ad_type == ADType.ENCRYPTED_ADVERTISING_DATA:
                parsed.encrypted_advertising_data = ad_data
            elif ad_type == ADType.PERIODIC_ADVERTISING_RESPONSE_TIMING_INFORMATION:
                parsed.periodic_advertising_response_timing = ad_data
            elif ad_type == ADType.ELECTRONIC_SHELF_LABEL:
                parsed.electronic_shelf_label = ad_data
            elif ad_type == ADType.THREE_D_INFORMATION_DATA:
                parsed.three_d_information = ad_data
            elif ad_type == ADType.BROADCAST_NAME:
                try:
                    parsed.broadcast_name = ad_data.decode("utf-8")
                except UnicodeDecodeError:
                    parsed.broadcast_name = ad_data.hex()
            elif ad_type == ADType.BROADCAST_CODE:
                parsed.broadcast_code = ad_data
            elif ad_type == ADType.BIGINFO:
                parsed.biginfo = ad_data
            elif ad_type == ADType.MESH_MESSAGE:
                parsed.mesh_message = ad_data
            elif ad_type == ADType.MESH_BEACON:
                parsed.mesh_beacon = ad_data
            elif ad_type == ADType.PUBLIC_TARGET_ADDRESS:
                for j in range(0, len(ad_data), 6):
                    if j + 5 < len(ad_data):
                        addr_bytes = ad_data[j : j + 6]
                        addr_str = ":".join(f"{b:02X}" for b in addr_bytes[::-1])
                        parsed.public_target_address.append(addr_str)
            elif ad_type == ADType.RANDOM_TARGET_ADDRESS:
                for j in range(0, len(ad_data), 6):
                    if j + 5 < len(ad_data):
                        addr_bytes = ad_data[j : j + 6]
                        addr_str = ":".join(f"{b:02X}" for b in addr_bytes[::-1])
                        parsed.random_target_address.append(addr_str)
            elif ad_type == ADType.ADVERTISING_INTERVAL and len(ad_data) >= 2:
                parsed.advertising_interval = DataParser.parse_int16(ad_data, 0, signed=False)
            elif ad_type == ADType.ADVERTISING_INTERVAL_LONG and len(ad_data) >= 3:
                parsed.advertising_interval_long = int.from_bytes(ad_data[:3], byteorder="little", signed=False)
            elif ad_type == ADType.LE_BLUETOOTH_DEVICE_ADDRESS and len(ad_data) >= 6:
                addr_bytes = ad_data[:6]
                parsed.le_bluetooth_device_address = ":".join(f"{b:02X}" for b in addr_bytes[::-1])
            elif ad_type == ADType.LE_ROLE and len(ad_data) >= 1:
                parsed.le_role = ad_data[0]
            elif ad_type == ADType.CLASS_OF_DEVICE and len(ad_data) >= 3:
                parsed.class_of_device = int.from_bytes(ad_data[:3], byteorder="little", signed=False)
            elif ad_type == ADType.SIMPLE_PAIRING_HASH_C:
                parsed.simple_pairing_hash_c = ad_data
            elif ad_type == ADType.SIMPLE_PAIRING_RANDOMIZER_R:
                parsed.simple_pairing_randomizer_r = ad_data
            elif ad_type == ADType.SECURITY_MANAGER_TK_VALUE:
                parsed.security_manager_tk_value = ad_data
            elif ad_type == ADType.SECURITY_MANAGER_OUT_OF_BAND_FLAGS:
                parsed.security_manager_out_of_band_flags = ad_data
            elif ad_type == ADType.SLAVE_CONNECTION_INTERVAL_RANGE:
                parsed.slave_connection_interval_range = ad_data
            elif ad_type == ADType.SECURE_CONNECTIONS_CONFIRMATION_VALUE:
                parsed.secure_connections_confirmation = ad_data
            elif ad_type == ADType.SECURE_CONNECTIONS_RANDOM_VALUE:
                parsed.secure_connections_random = ad_data
            elif ad_type == ADType.CHANNEL_MAP_UPDATE_INDICATION:
                parsed.channel_map_update_indication = ad_data
            elif ad_type == ADType.PB_ADV:
                parsed.pb_adv = ad_data
            elif ad_type == ADType.RESOLVABLE_SET_IDENTIFIER:
                parsed.resolvable_set_identifier = ad_data

            i += length + 1

        # Decode class_of_device if present
        if parsed.class_of_device is not None:
            parsed.class_of_device_info = class_of_device_registry.decode_class_of_device(parsed.class_of_device)

        return parsed

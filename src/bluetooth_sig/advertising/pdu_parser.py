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
from bluetooth_sig.gatt.constants import SIZE_UINT16, SIZE_UINT24, SIZE_UINT32, SIZE_UINT48, SIZE_UUID128
from bluetooth_sig.registry.core.ad_types import ad_types_registry
from bluetooth_sig.registry.core.appearance_values import appearance_values_registry
from bluetooth_sig.registry.core.class_of_device import class_of_device_registry
from bluetooth_sig.types import ManufacturerData
from bluetooth_sig.types.ad_types_constants import ADType
from bluetooth_sig.types.advertising.ad_structures import (
    AdvertisingDataStructures,
    ConnectionIntervalRange,
    ExtendedAdvertisingData,
)
from bluetooth_sig.types.advertising.channel_map_update import ChannelMapUpdateIndication
from bluetooth_sig.types.advertising.extended import (
    AdvertisingDataInfo,
    AuxiliaryPointer,
    CTEInfo,
    CTEType,
    PHYType,
    SyncInfo,
)
from bluetooth_sig.types.advertising.features import LEFeatures
from bluetooth_sig.types.advertising.flags import BLEAdvertisingFlags
from bluetooth_sig.types.advertising.indoor_positioning import IndoorPositioningData
from bluetooth_sig.types.advertising.pdu import (
    BLEAdvertisingPDU,
    BLEExtendedHeader,
    ExtendedHeaderFlags,
    PDUHeaderFlags,
    PDULayout,
    PDUType,
)
from bluetooth_sig.types.advertising.result import AdvertisingData
from bluetooth_sig.types.advertising.three_d_information import ThreeDInformationData
from bluetooth_sig.types.advertising.transport_discovery import TransportDiscoveryData
from bluetooth_sig.types.appearance import AppearanceData
from bluetooth_sig.types.mesh import (
    MeshBeaconType,
    MeshMessage,
    ProvisioningBearerData,
    SecureNetworkBeacon,
    UnprovisionedDeviceBeacon,
)
from bluetooth_sig.types.uri import URIData
from bluetooth_sig.types.uuid import BluetoothUUID

logger = logging.getLogger(__name__)


class _ExtendedHeaderBitMasks:
    """Bit masks for parsing extended header fields (Core Spec Vol 6, Part B)."""

    # CTE Info field (1 byte)
    CTE_TIME_MASK: int = 0x1F  # Bits 0-4: CTE time (0-19)
    CTE_TYPE_SHIFT: int = 6
    CTE_TYPE_MASK: int = 0x03  # Bits 6-7: CTE type

    # Advertising Data Info (ADI) field (2 bytes)
    ADI_DID_MASK: int = 0x0FFF  # Bits 0-11: Data ID
    ADI_SID_SHIFT: int = 12
    ADI_SID_MASK: int = 0x0F  # Bits 12-15: Set ID

    # Auxiliary Pointer field (3 bytes)
    AUX_CHANNEL_MASK: int = 0x3F  # Bits 0-5: Channel index
    AUX_CA_SHIFT: int = 6
    AUX_OFFSET_UNITS_SHIFT: int = 7
    AUX_OFFSET_SHIFT: int = 8
    AUX_OFFSET_MASK: int = 0x1FFF  # Bits 8-20: 13-bit offset
    AUX_PHY_SHIFT: int = 21
    AUX_PHY_MASK: int = 0x07  # Bits 21-23: PHY

    # SyncInfo field (18 bytes)
    SYNC_OFFSET_MASK: int = 0x1FFF  # Bits 0-12: 13-bit offset
    SYNC_OFFSET_UNITS_SHIFT: int = 13
    SYNC_CHANNEL_MAP_MASK: int = 0x1FFFFFFFFF  # 37-bit channel map
    SYNC_SCA_SHIFT: int = 5
    SYNC_SCA_MASK: int = 0x07  # Bits 5-7: SCA
    SYNC_ADDR_TYPE_SHIFT: int = 4


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

        header = DataParser.parse_int16(data, 0, signed=False)
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

    @staticmethod
    def _parse_address_to_string(addr_bytes: bytes) -> str:
        """Convert 6-byte Bluetooth address to formatted string.

        Args:
            addr_bytes: 6-byte address in little-endian order

        Returns:
            Formatted address string (XX:XX:XX:XX:XX:XX)
        """
        return ":".join(f"{b:02X}" for b in addr_bytes[::-1])

    @staticmethod
    def _parse_cte_info(data: bytes) -> CTEInfo:
        """Parse CTE info from raw byte.

        Args:
            data: 1-byte CTE info

        Returns:
            Parsed CTEInfo struct
        """
        cte_byte = data[0]
        cte_time = cte_byte & _ExtendedHeaderBitMasks.CTE_TIME_MASK
        cte_type_raw = (cte_byte >> _ExtendedHeaderBitMasks.CTE_TYPE_SHIFT) & _ExtendedHeaderBitMasks.CTE_TYPE_MASK
        return CTEInfo(cte_time=cte_time, cte_type=CTEType(cte_type_raw))

    @staticmethod
    def _parse_advertising_data_info(data: bytes) -> AdvertisingDataInfo:
        """Parse Advertising Data Info (ADI) from raw bytes.

        Args:
            data: 2-byte ADI field

        Returns:
            Parsed AdvertisingDataInfo struct
        """
        adi_value = DataParser.parse_int16(data, 0, signed=False)
        did = adi_value & _ExtendedHeaderBitMasks.ADI_DID_MASK
        sid = (adi_value >> _ExtendedHeaderBitMasks.ADI_SID_SHIFT) & _ExtendedHeaderBitMasks.ADI_SID_MASK
        return AdvertisingDataInfo(advertising_data_id=did, advertising_set_id=sid)

    @staticmethod
    def _parse_auxiliary_pointer_struct(data: bytes) -> AuxiliaryPointer:
        """Parse Auxiliary Pointer from raw bytes.

        Args:
            data: 3-byte AuxPtr field

        Returns:
            Parsed AuxiliaryPointer struct
        """
        aux_value = DataParser.parse_int24(data, 0, signed=False)
        channel_index = aux_value & _ExtendedHeaderBitMasks.AUX_CHANNEL_MASK
        ca = bool((aux_value >> _ExtendedHeaderBitMasks.AUX_CA_SHIFT) & 0x01)
        offset_units = (aux_value >> _ExtendedHeaderBitMasks.AUX_OFFSET_UNITS_SHIFT) & 0x01
        aux_offset = (aux_value >> _ExtendedHeaderBitMasks.AUX_OFFSET_SHIFT) & _ExtendedHeaderBitMasks.AUX_OFFSET_MASK
        aux_phy_raw = (aux_value >> _ExtendedHeaderBitMasks.AUX_PHY_SHIFT) & _ExtendedHeaderBitMasks.AUX_PHY_MASK
        aux_phy = PHYType(min(aux_phy_raw, PHYType.LE_CODED))  # Clamp to valid range
        return AuxiliaryPointer(
            channel_index=channel_index,
            ca=ca,
            offset_units=offset_units,
            aux_offset=aux_offset,
            aux_phy=aux_phy,
        )

    def _parse_sync_info(self, data: bytes) -> SyncInfo:
        """Parse SyncInfo from raw bytes.

        Args:
            data: 18-byte SyncInfo field

        Returns:
            Parsed SyncInfo struct
        """
        # Bytes 0-1: Sync packet offset and units (13 bits offset + 1 bit units + 2 reserved)
        offset_field = DataParser.parse_int16(data, 0, signed=False)
        sync_packet_offset = offset_field & _ExtendedHeaderBitMasks.SYNC_OFFSET_MASK
        offset_units = (offset_field >> _ExtendedHeaderBitMasks.SYNC_OFFSET_UNITS_SHIFT) & 0x01

        # Bytes 2-3: Interval
        interval = DataParser.parse_int16(data, 2, signed=False)

        # Bytes 4-8: Channel map (37 bits, stored in 5 bytes)
        # Note: 40-bit field exceeds DataParser's 32-bit limit, use int.from_bytes directly
        channel_map = int.from_bytes(data[4:9], byteorder="little") & _ExtendedHeaderBitMasks.SYNC_CHANNEL_MAP_MASK

        # Byte 9: SCA (3 bits) and other fields
        sca_byte = DataParser.parse_int8(data, 9, signed=False)
        sleep_clock_accuracy = (
            sca_byte >> _ExtendedHeaderBitMasks.SYNC_SCA_SHIFT
        ) & _ExtendedHeaderBitMasks.SYNC_SCA_MASK

        # Bytes 10-15: Access Address (we interpret this as advertiser address)
        advertising_address = self._parse_address_to_string(data[10:16])
        advertising_address_type = (sca_byte >> _ExtendedHeaderBitMasks.SYNC_ADDR_TYPE_SHIFT) & 0x01

        # Bytes 16-17: Sync counter/CRC init
        sync_counter = DataParser.parse_int16(data, 16, signed=False)

        return SyncInfo(
            sync_packet_offset=sync_packet_offset,
            offset_units=offset_units,
            interval=interval,
            channel_map=channel_map,
            sleep_clock_accuracy=sleep_clock_accuracy,
            advertising_address=advertising_address,
            advertising_address_type=advertising_address_type,
            sync_counter=sync_counter,
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

        extended_header_length = data[0]

        if len(data) < extended_header_length + 1:
            return None

        adv_mode = data[1]
        offset = PDULayout.ADV_ADDR_OFFSET  # Start after length and mode bytes

        extended_advertiser_address = ""
        extended_target_address = ""
        cte_info: CTEInfo | None = None
        advertising_data_info: AdvertisingDataInfo | None = None
        auxiliary_pointer: AuxiliaryPointer | None = None
        sync_info: SyncInfo | None = None
        tx_power: int | None = None
        additional_controller_advertising_data = b""

        # Check ADV_ADDR flag
        if adv_mode & ExtendedHeaderFlags.ADV_ADDR:
            if offset + PDULayout.BLE_ADDR > len(data):
                return None
            extended_advertiser_address = self._parse_address_to_string(data[offset : offset + PDULayout.BLE_ADDR])
            offset += PDULayout.BLE_ADDR

        # Check TARGET_ADDR flag
        if adv_mode & ExtendedHeaderFlags.TARGET_ADDR:
            if offset + PDULayout.BLE_ADDR > len(data):
                return None
            extended_target_address = self._parse_address_to_string(data[offset : offset + PDULayout.BLE_ADDR])
            offset += PDULayout.BLE_ADDR

        # Check CTE_INFO flag
        if adv_mode & ExtendedHeaderFlags.CTE_INFO:
            if offset + PDULayout.CTE_INFO > len(data):
                return None
            cte_info = self._parse_cte_info(data[offset : offset + PDULayout.CTE_INFO])
            offset += PDULayout.CTE_INFO

        # Check ADV_DATA_INFO flag
        if adv_mode & ExtendedHeaderFlags.ADV_DATA_INFO:
            if offset + PDULayout.ADV_DATA_INFO > len(data):
                return None
            advertising_data_info = self._parse_advertising_data_info(data[offset : offset + PDULayout.ADV_DATA_INFO])
            offset += PDULayout.ADV_DATA_INFO

        # Check AUX_PTR flag
        if adv_mode & ExtendedHeaderFlags.AUX_PTR:
            if offset + PDULayout.AUX_PTR > len(data):
                return None
            auxiliary_pointer = self._parse_auxiliary_pointer_struct(data[offset : offset + PDULayout.AUX_PTR])
            offset += PDULayout.AUX_PTR

        # Check SYNC_INFO flag
        if adv_mode & ExtendedHeaderFlags.SYNC_INFO:
            if offset + PDULayout.SYNC_INFO > len(data):
                return None
            sync_info = self._parse_sync_info(data[offset : offset + PDULayout.SYNC_INFO])
            offset += PDULayout.SYNC_INFO

        # Check TX_POWER flag
        if adv_mode & ExtendedHeaderFlags.TX_POWER:
            if offset + PDULayout.TX_POWER > len(data):
                return None
            tx_power = DataParser.parse_int8(data, offset, signed=True)
            offset += PDULayout.TX_POWER

        # Check ACAD flag
        if adv_mode & ExtendedHeaderFlags.ACAD:
            additional_controller_advertising_data = data[offset:]

        return BLEExtendedHeader(
            extended_header_length=extended_header_length,
            adv_mode=adv_mode,
            extended_advertiser_address=extended_advertiser_address,
            extended_target_address=extended_target_address,
            cte_info=cte_info,
            advertising_data_info=advertising_data_info,
            auxiliary_pointer=auxiliary_pointer,
            sync_info=sync_info,
            tx_power=tx_power,
            additional_controller_advertising_data=additional_controller_advertising_data,
        )

    def _parse_auxiliary_packets(self, aux_ptr: AuxiliaryPointer) -> list[BLEAdvertisingPDU]:
        """Parse auxiliary packets referenced by auxiliary pointer.

        Args:
            aux_ptr: Parsed AuxiliaryPointer struct

        Returns:
            List of auxiliary packets (currently returns empty list)

        Note:
            This is a placeholder. Full implementation would require
            receiving raw PDU data from the auxiliary channel specified
            in the AuxiliaryPointer (channel_index, aux_offset, aux_phy).
        """
        # Auxiliary packets are received over the air on a different channel
        # at a later time. This cannot be parsed from a single PDU capture.
        # The AuxiliaryPointer tells us where to listen, not the data itself.
        _ = aux_ptr  # Acknowledge the parameter for future implementation
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
    def _parse_32bit_uuids(ad_data: bytes) -> list[BluetoothUUID]:
        """Parse list of 32-bit service UUIDs from raw data.

        Args:
            ad_data: Raw UUID data

        Returns:
            List of BluetoothUUID objects
        """
        uuids: list[BluetoothUUID] = []
        for j in range(0, len(ad_data), 4):
            if j + 3 < len(ad_data):
                uuid_32 = DataParser.parse_int32(ad_data, j, signed=False)
                uuids.append(BluetoothUUID(uuid_32))
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
            ad_data: Raw manufacturer-specific data bytes (company ID + payload)
            parsed: AdvertisingDataStructures object to update

        """
        mfr_data = ManufacturerData.from_bytes(ad_data)
        parsed.core.manufacturer_data[mfr_data.company.id] = mfr_data

    def _handle_core_ad_types(self, ad_type: int, ad_data: bytes, parsed: AdvertisingDataStructures) -> bool:
        """Handle core advertising data types (service UUIDs, names, etc).

        Returns:
            True if ad_type was handled, False otherwise
        """
        if ad_type in (ADType.INCOMPLETE_16BIT_SERVICE_UUIDS, ADType.COMPLETE_16BIT_SERVICE_UUIDS):
            parsed.core.service_uuids.extend(self._parse_16bit_uuids(ad_data))
        elif ad_type in (ADType.INCOMPLETE_32BIT_SERVICE_UUIDS, ADType.COMPLETE_32BIT_SERVICE_UUIDS):
            parsed.core.service_uuids.extend(self._parse_32bit_uuids(ad_data))
        elif ad_type in (ADType.INCOMPLETE_128BIT_SERVICE_UUIDS, ADType.COMPLETE_128BIT_SERVICE_UUIDS):
            parsed.core.service_uuids.extend(self._parse_128bit_uuids(ad_data))
        elif ad_type == ADType.SOLICITED_SERVICE_UUIDS_16BIT:
            parsed.core.solicited_service_uuids.extend(self._parse_16bit_uuids(ad_data))
        elif ad_type == ADType.SOLICITED_SERVICE_UUIDS_32BIT:
            parsed.core.solicited_service_uuids.extend(self._parse_32bit_uuids(ad_data))
        elif ad_type == ADType.SOLICITED_SERVICE_UUIDS_128BIT:
            parsed.core.solicited_service_uuids.extend(self._parse_128bit_uuids(ad_data))
        elif ad_type in (ADType.SHORTENED_LOCAL_NAME, ADType.COMPLETE_LOCAL_NAME):
            try:
                parsed.core.local_name = ad_data.decode("utf-8")
            except UnicodeDecodeError:
                parsed.core.local_name = ad_data.hex()
        elif ad_type == ADType.URI:
            parsed.core.uri_data = URIData.from_raw_data(ad_data)
        elif ad_type == ADType.SERVICE_DATA_16BIT and len(ad_data) >= SIZE_UINT16:
            service_uuid = BluetoothUUID(DataParser.parse_int16(ad_data, 0, signed=False))
            parsed.core.service_data[service_uuid] = ad_data[2:]
            if service_uuid not in parsed.core.service_uuids:
                parsed.core.service_uuids.append(service_uuid)
        elif ad_type == ADType.SERVICE_DATA_32BIT and len(ad_data) >= SIZE_UINT32:
            service_uuid = BluetoothUUID(DataParser.parse_int32(ad_data, 0, signed=False))
            parsed.core.service_data[service_uuid] = ad_data[4:]
            if service_uuid not in parsed.core.service_uuids:
                parsed.core.service_uuids.append(service_uuid)
        elif ad_type == ADType.SERVICE_DATA_128BIT and len(ad_data) >= SIZE_UUID128:
            service_uuid = BluetoothUUID(ad_data[:16].hex().upper())
            parsed.core.service_data[service_uuid] = ad_data[16:]
            if service_uuid not in parsed.core.service_uuids:
                parsed.core.service_uuids.append(service_uuid)
        else:
            return False
        return True

    def _handle_property_ad_types(self, ad_type: int, ad_data: bytes, parsed: AdvertisingDataStructures) -> bool:
        """Handle device property advertising data types (flags, power, appearance, etc).

        Returns:
            True if ad_type was handled, False otherwise
        """
        if ad_type == ADType.FLAGS and len(ad_data) >= 1:
            parsed.properties.flags = BLEAdvertisingFlags(ad_data[0])
        elif ad_type == ADType.TX_POWER_LEVEL and len(ad_data) >= 1:
            parsed.properties.tx_power = int.from_bytes(ad_data[:1], byteorder="little", signed=True)
        elif ad_type == ADType.APPEARANCE and len(ad_data) >= SIZE_UINT16:
            raw_value = DataParser.parse_int16(ad_data, 0, signed=False)
            appearance_info = appearance_values_registry.get_appearance_info(raw_value)
            parsed.properties.appearance = AppearanceData(raw_value=raw_value, info=appearance_info)
        elif ad_type == ADType.LE_SUPPORTED_FEATURES:
            parsed.properties.le_supported_features = LEFeatures(raw_value=ad_data)
        elif ad_type == ADType.LE_ROLE and len(ad_data) >= 1:
            parsed.properties.le_role = ad_data[0]
        elif ad_type == ADType.CLASS_OF_DEVICE and len(ad_data) >= SIZE_UINT24:
            raw_cod = int.from_bytes(ad_data[:3], byteorder="little", signed=False)
            parsed.properties.class_of_device = class_of_device_registry.decode_class_of_device(raw_cod)
        elif ad_type == ADType.MANUFACTURER_SPECIFIC_DATA and len(ad_data) >= SIZE_UINT16:
            self._parse_manufacturer_data(ad_data, parsed)
        else:
            return False
        return True

    def _handle_mesh_ad_types(self, ad_type: int, ad_data: bytes, parsed: AdvertisingDataStructures) -> bool:
        """Handle mesh networking advertising data types.

        Returns:
            True if ad_type was handled, False otherwise
        """
        if ad_type == ADType.PERIODIC_ADVERTISING_RESPONSE_TIMING_INFORMATION:
            parsed.mesh.periodic_advertising_response_timing = ad_data
        elif ad_type == ADType.ELECTRONIC_SHELF_LABEL:
            parsed.mesh.electronic_shelf_label = ad_data
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
            parsed.mesh.mesh_message = MeshMessage.decode(ad_data)
        elif ad_type == ADType.MESH_BEACON:
            self._parse_mesh_beacon(ad_data, parsed)
        elif ad_type == ADType.PB_ADV:
            parsed.mesh.provisioning_bearer = ProvisioningBearerData.decode(ad_data)
        else:
            return False
        return True

    def _parse_mesh_beacon(self, ad_data: bytes, parsed: AdvertisingDataStructures) -> None:
        """Parse mesh beacon data into appropriate typed beacon.

        Args:
            ad_data: Raw beacon advertisement data
            parsed: Advertising data structures to populate

        """
        if len(ad_data) < 1:
            return

        beacon_type = ad_data[0]
        beacon_data = ad_data[1:]

        if beacon_type == MeshBeaconType.SECURE_NETWORK:
            parsed.mesh.secure_network_beacon = SecureNetworkBeacon.decode(beacon_data)
        elif beacon_type == MeshBeaconType.UNPROVISIONED_DEVICE:
            parsed.mesh.unprovisioned_device_beacon = UnprovisionedDeviceBeacon.decode(beacon_data)

    def _handle_security_ad_types(self, ad_type: int, ad_data: bytes, parsed: AdvertisingDataStructures) -> bool:
        """Handle security/pairing advertising data types.

        Returns:
            True if ad_type was handled, False otherwise
        """
        if ad_type == ADType.ENCRYPTED_ADVERTISING_DATA:
            parsed.security.encrypted_advertising_data = ad_data
        elif ad_type == ADType.RESOLVABLE_SET_IDENTIFIER:
            parsed.security.resolvable_set_identifier = ad_data
        elif ad_type == ADType.SIMPLE_PAIRING_HASH_C:
            parsed.oob_security.simple_pairing_hash_c = ad_data
        elif ad_type == ADType.SIMPLE_PAIRING_RANDOMIZER_R:
            parsed.oob_security.simple_pairing_randomizer_r = ad_data
        elif ad_type == ADType.SECURITY_MANAGER_TK_VALUE:
            parsed.oob_security.security_manager_tk_value = ad_data
        elif ad_type == ADType.SECURITY_MANAGER_OUT_OF_BAND_FLAGS:
            parsed.oob_security.security_manager_oob_flags = ad_data
        elif ad_type == ADType.SECURE_CONNECTIONS_CONFIRMATION_VALUE:
            parsed.oob_security.secure_connections_confirmation = ad_data
        elif ad_type == ADType.SECURE_CONNECTIONS_RANDOM_VALUE:
            parsed.oob_security.secure_connections_random = ad_data
        else:
            return False
        return True

    def _handle_directed_ad_types(self, ad_type: int, ad_data: bytes, parsed: AdvertisingDataStructures) -> bool:
        """Handle directed/connection advertising data types.

        Returns:
            True if ad_type was handled, False otherwise
        """
        if ad_type == ADType.PUBLIC_TARGET_ADDRESS:
            parsed.directed.public_target_address.extend(self._parse_address_list(ad_data))
        elif ad_type == ADType.RANDOM_TARGET_ADDRESS:
            parsed.directed.random_target_address.extend(self._parse_address_list(ad_data))
        elif ad_type == ADType.ADVERTISING_INTERVAL and len(ad_data) >= SIZE_UINT16:
            parsed.directed.advertising_interval = DataParser.parse_int16(ad_data, 0, signed=False)
        elif ad_type == ADType.ADVERTISING_INTERVAL_LONG and len(ad_data) >= SIZE_UINT24:
            parsed.directed.advertising_interval_long = int.from_bytes(ad_data[:3], byteorder="little", signed=False)
        elif ad_type == ADType.LE_BLUETOOTH_DEVICE_ADDRESS and len(ad_data) >= SIZE_UINT48:
            addr_bytes = ad_data[:6]
            parsed.directed.le_bluetooth_device_address = ":".join(f"{b:02X}" for b in addr_bytes[::-1])
        elif ad_type == ADType.SLAVE_CONNECTION_INTERVAL_RANGE and len(ad_data) >= SIZE_UINT32:
            min_interval = DataParser.parse_int16(ad_data, 0, signed=False)
            max_interval = DataParser.parse_int16(ad_data, 2, signed=False)
            parsed.directed.peripheral_connection_interval_range = ConnectionIntervalRange(
                min_interval=min_interval,
                max_interval=max_interval,
            )
        else:
            return False
        return True

    def _handle_location_ad_types(self, ad_type: int, ad_data: bytes, parsed: AdvertisingDataStructures) -> bool:
        """Handle location/positioning advertising data types.

        Returns:
            True if ad_type was handled, False otherwise
        """
        if ad_type == ADType.INDOOR_POSITIONING:
            parsed.location.indoor_positioning = IndoorPositioningData.decode(ad_data)
        elif ad_type == ADType.TRANSPORT_DISCOVERY_DATA:
            parsed.location.transport_discovery_data = TransportDiscoveryData.decode(ad_data)
        elif ad_type == ADType.THREE_D_INFORMATION_DATA:
            parsed.location.three_d_information = ThreeDInformationData.decode(ad_data)
        elif ad_type == ADType.CHANNEL_MAP_UPDATE_INDICATION:
            parsed.location.channel_map_update_indication = ChannelMapUpdateIndication.decode(ad_data)
        else:
            return False
        return True

    def _parse_ad_structures(self, data: bytes) -> AdvertisingDataStructures:
        """Parse advertising data structures from raw bytes.

        Args:
            data: Raw advertising data payload

        Returns:
            AdvertisingDataStructures object with extracted data

        """
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

            if not ad_types_registry.is_known_ad_type(ad_type):
                logger.warning("Unknown AD type encountered: 0x%02X", ad_type)

            # Dispatch to category handlers
            self._handle_core_ad_types(ad_type, ad_data, parsed) or self._handle_property_ad_types(
                ad_type, ad_data, parsed
            ) or self._handle_mesh_ad_types(ad_type, ad_data, parsed) or self._handle_security_ad_types(
                ad_type, ad_data, parsed
            ) or self._handle_directed_ad_types(ad_type, ad_data, parsed) or self._handle_location_ad_types(
                ad_type, ad_data, parsed
            )

            i += length + 1

        return parsed

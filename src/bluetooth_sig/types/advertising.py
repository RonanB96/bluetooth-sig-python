"""BLE Advertising data types and parsing utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, IntFlag
from typing import cast


class PDUFlags(IntFlag):
    """BLE PDU parsing bit masks for header operations.

    These masks are pre-positioned to their correct bit locations,
    eliminating the need for shifts during extraction.
    """

    TYPE_MASK = 0x0F
    RFU_BIT_4 = 0x10
    RFU_BIT_5 = 0x20
    TX_ADD_MASK = 0x40
    RX_ADD_MASK = 0x80

    @classmethod
    def extract_bits(cls, header: int, mask: int) -> int | bool:
        """Extract bits from header using the specified mask.

        Returns int for multi-bit masks, bool for single-bit masks.
        """
        value = header & mask
        # If mask has multiple bits set, return the raw value
        # If mask has only one bit set, return boolean
        if mask & (mask - 1):  # Check if mask has multiple bits set
            return value
        return bool(value)

    @classmethod
    def extract_pdu_type(cls, header: int) -> PDUType:
        """Extract PDU type from header byte and return as PDUType enum."""
        raw_type = int(cls.extract_bits(header, cls.TYPE_MASK))
        try:
            return PDUType(raw_type)
        except ValueError as exc:
            # For unknown PDU types, we could either raise or return a special value
            raise ValueError(f"Unknown PDU type: 0x{raw_type:02X}") from exc

    @classmethod
    def extract_tx_add(cls, header: int) -> bool:
        """Extract TX address type from header."""
        return bool(cls.extract_bits(header, cls.TX_ADD_MASK))

    @classmethod
    def extract_rx_add(cls, header: int) -> bool:
        """Extract RX address type from header."""
        return bool(cls.extract_bits(header, cls.RX_ADD_MASK))


@dataclass(frozen=True)
class PDUConstants:  # pylint: disable=too-many-instance-attributes
    """BLE PDU parsing constants for sizes and offsets.

    Following best practices, this uses a dataclass for related
    constants rather than mixing them with enums/flags.
    """

    # PDU Size constants
    BLE_ADDR: int = 6
    AUX_PTR: int = 3
    ADV_DATA_INFO: int = 2
    CTE_INFO: int = 1
    SYNC_INFO: int = 18
    TX_POWER: int = 1
    PDU_HEADER: int = 2
    MIN_EXTENDED_PDU: int = 3
    EXT_HEADER_LENGTH: int = 1

    # PDU Offsets
    EXTENDED_HEADER_START: int = 3
    ADV_MODE: int = 1
    ADV_ADDR_OFFSET: int = 2
    TARGET_ADDR_OFFSET: int = 2
    CTE_INFO_OFFSET: int = 1
    ADV_DATA_INFO_OFFSET: int = 2
    AUX_PTR_OFFSET: int = 3
    SYNC_INFO_OFFSET: int = 18
    TX_POWER_OFFSET: int = 1
    PDU_LENGTH_OFFSET: int = 2


# Global instance for easy access
PDU_CONSTANTS = PDUConstants()


class ExtendedHeaderMode(IntEnum):
    """Extended Header Mode bit masks (BLE 5.0+)."""

    ADV_ADDR = 0x01
    TARGET_ADDR = 0x02
    CTE_INFO = 0x04
    ADV_DATA_INFO = 0x08
    AUX_PTR = 0x10
    SYNC_INFO = 0x20
    TX_POWER = 0x40
    ACAD = 0x80


class PDUType(IntEnum):
    """BLE Advertising PDU Types."""

    ADV_IND = 0x00
    ADV_DIRECT_IND = 0x01
    ADV_NONCONN_IND = 0x02
    SCAN_REQ = 0x03
    SCAN_RSP = 0x04
    CONNECT_IND = 0x05
    ADV_SCAN_IND = 0x06
    ADV_EXT_IND = 0x07
    ADV_AUX_IND = 0x08

    @property
    def is_extended_advertising(self) -> bool:
        """Check if this is an extended advertising PDU."""
        return self in (PDUType.ADV_EXT_IND, PDUType.ADV_AUX_IND)

    @property
    def is_legacy_advertising(self) -> bool:
        """Check if this is a legacy advertising PDU."""
        return self in (
            PDUType.ADV_IND,
            PDUType.ADV_DIRECT_IND,
            PDUType.ADV_NONCONN_IND,
            PDUType.SCAN_REQ,
            PDUType.SCAN_RSP,
            PDUType.CONNECT_IND,
            PDUType.ADV_SCAN_IND,
        )


class BLEAdvertisementTypes(IntEnum):
    """BLE Advertisement Data Types (AD Types) as defined in Bluetooth Core
    Specification."""

    # Legacy Advertising AD Types
    FLAGS = 0x01
    INCOMPLETE_16BIT_SERVICE_UUIDS = 0x02
    COMPLETE_16BIT_SERVICE_UUIDS = 0x03
    INCOMPLETE_32BIT_SERVICE_UUIDS = 0x04
    COMPLETE_32BIT_SERVICE_UUIDS = 0x05
    INCOMPLETE_128BIT_SERVICE_UUIDS = 0x06
    COMPLETE_128BIT_SERVICE_UUIDS = 0x07
    SHORTENED_LOCAL_NAME = 0x08
    COMPLETE_LOCAL_NAME = 0x09
    TX_POWER_LEVEL = 0x0A
    CLASS_OF_DEVICE = 0x0D
    SIMPLE_PAIRING_HASH_C = 0x0E
    SIMPLE_PAIRING_RANDOMIZER_R = 0x0F
    SECURITY_MANAGER_TK_VALUE = 0x10
    SECURITY_MANAGER_OUT_OF_BAND_FLAGS = 0x11
    SLAVE_CONNECTION_INTERVAL_RANGE = 0x12
    SOLICITED_SERVICE_UUIDS_16BIT = 0x14
    SOLICITED_SERVICE_UUIDS_128BIT = 0x15
    SERVICE_DATA_16BIT = 0x16
    PUBLIC_TARGET_ADDRESS = 0x17
    RANDOM_TARGET_ADDRESS = 0x18
    APPEARANCE = 0x19
    ADVERTISING_INTERVAL = 0x1A
    LE_BLUETOOTH_DEVICE_ADDRESS = 0x1B
    LE_ROLE = 0x1C
    SIMPLE_PAIRING_HASH_C256 = 0x1D
    SIMPLE_PAIRING_RANDOMIZER_R256 = 0x1E
    SERVICE_DATA_32BIT = 0x20
    SERVICE_DATA_128BIT = 0x21
    SECURE_CONNECTIONS_CONFIRMATION_VALUE = 0x22
    SECURE_CONNECTIONS_RANDOM_VALUE = 0x23
    URI = 0x24
    INDOOR_POSITIONING = 0x25
    TRANSPORT_DISCOVERY_DATA = 0x26
    LE_SUPPORTED_FEATURES = 0x27
    CHANNEL_MAP_UPDATE_INDICATION = 0x28
    PB_ADV = 0x29
    MESH_MESSAGE = 0x2A
    MESH_BEACON = 0x2B
    BIGINFO = 0x2C
    BROADCAST_CODE = 0x2D
    RESOLVABLE_SET_IDENTIFIER = 0x2E
    ADVERTISING_INTERVAL_LONG = 0x2F
    BROADCAST_NAME = 0x30
    ENCRYPTED_ADVERTISING_DATA = 0x31
    PERIODIC_ADVERTISING_RESPONSE_TIMING_INFORMATION = 0x32
    ELECTRONIC_SHELF_LABEL = 0x34
    THREE_D_INFORMATION_DATA = 0x3D
    MANUFACTURER_SPECIFIC_DATA = 0xFF


@dataclass
class BLEExtendedHeader:  # pylint: disable=too-many-instance-attributes
    """Extended Advertising Header fields (BLE 5.0+)."""

    extended_header_length: int = 0
    adv_mode: int = 0

    extended_advertiser_address: bytes = b""
    extended_target_address: bytes = b""
    cte_info: bytes = b""
    advertising_data_info: bytes = b""
    auxiliary_pointer: bytes = b""
    sync_info: bytes = b""
    tx_power: int | None = None
    additional_controller_advertising_data: bytes = b""

    @property
    def has_extended_advertiser_address(self) -> bool:
        """Check if extended advertiser address is present."""
        return bool(self.adv_mode & ExtendedHeaderMode.ADV_ADDR)

    @property
    def has_extended_target_address(self) -> bool:
        """Check if extended target address is present."""
        return bool(self.adv_mode & ExtendedHeaderMode.TARGET_ADDR)

    @property
    def has_cte_info(self) -> bool:
        """Check if CTE info is present."""
        return bool(self.adv_mode & ExtendedHeaderMode.CTE_INFO)

    @property
    def has_advertising_data_info(self) -> bool:
        """Check if advertising data info is present."""
        return bool(self.adv_mode & ExtendedHeaderMode.ADV_DATA_INFO)

    @property
    def has_auxiliary_pointer(self) -> bool:
        """Check if auxiliary pointer is present."""
        return bool(self.adv_mode & ExtendedHeaderMode.AUX_PTR)

    @property
    def has_sync_info(self) -> bool:
        """Check if sync info is present."""
        return bool(self.adv_mode & ExtendedHeaderMode.SYNC_INFO)

    @property
    def has_tx_power(self) -> bool:
        """Check if TX power is present."""
        return bool(self.adv_mode & ExtendedHeaderMode.TX_POWER)

    @property
    def has_additional_controller_data(self) -> bool:
        """Check if additional controller advertising data is present."""
        return bool(self.adv_mode & ExtendedHeaderMode.ACAD)


@dataclass
class BLEAdvertisingPDU:  # pylint: disable=too-many-instance-attributes
    """BLE Advertising PDU structure."""

    pdu_type: PDUType
    tx_add: bool
    rx_add: bool
    length: int
    advertiser_address: bytes = b""
    target_address: bytes = b""
    payload: bytes = b""
    extended_header: BLEExtendedHeader | None = None

    @property
    def is_extended_advertising(self) -> bool:
        """Check if this is an extended advertising PDU."""
        return self.pdu_type.is_extended_advertising

    @property
    def is_legacy_advertising(self) -> bool:
        """Check if this is a legacy advertising PDU."""
        return self.pdu_type.is_legacy_advertising

    @property
    def pdu_name(self) -> str:
        """Get human-readable PDU type name."""
        return self.pdu_type.name


@dataclass
class ParsedADStructures:  # pylint: disable=too-many-instance-attributes
    """Parsed Advertising Data structures from advertisement payload."""

    manufacturer_data: dict[int, bytes] = field(default_factory=lambda: cast(dict[int, bytes], {}))
    service_uuids: list[str] = field(default_factory=lambda: cast(list[str], []))
    local_name: str = ""
    tx_power: int = 0
    flags: int = 0
    appearance: int | None = None
    service_data: dict[str, bytes] = field(default_factory=lambda: cast(dict[str, bytes], {}))
    solicited_service_uuids: list[str] = field(default_factory=lambda: cast(list[str], []))
    uri: str = ""
    indoor_positioning: bytes = b""
    transport_discovery_data: bytes = b""
    le_supported_features: bytes = b""
    encrypted_advertising_data: bytes = b""
    periodic_advertising_response_timing: bytes = b""
    electronic_shelf_label: bytes = b""
    three_d_information: bytes = b""
    broadcast_name: str = ""
    broadcast_code: bytes = b""
    biginfo: bytes = b""
    mesh_message: bytes = b""
    mesh_beacon: bytes = b""
    public_target_address: list[str] = field(default_factory=lambda: cast(list[str], []))
    random_target_address: list[str] = field(default_factory=lambda: cast(list[str], []))
    advertising_interval: int | None = None
    advertising_interval_long: int | None = None
    le_bluetooth_device_address: str = ""
    le_role: int | None = None
    class_of_device: int | None = None
    simple_pairing_hash_c: bytes = b""
    simple_pairing_randomizer_r: bytes = b""
    security_manager_tk_value: bytes = b""
    security_manager_out_of_band_flags: bytes = b""
    slave_connection_interval_range: bytes = b""
    secure_connections_confirmation: bytes = b""
    secure_connections_random: bytes = b""
    channel_map_update_indication: bytes = b""
    pb_adv: bytes = b""
    resolvable_set_identifier: bytes = b""


@dataclass
class DeviceAdvertiserData:  # pylint: disable=too-many-instance-attributes
    """Parsed advertiser data from device discovery."""

    raw_data: bytes
    local_name: str = ""
    manufacturer_data: dict[int, bytes] = field(default_factory=lambda: cast(dict[int, bytes], {}))
    service_uuids: list[str] = field(default_factory=lambda: cast(list[str], []))
    tx_power: int | None = None
    rssi: int | None = None
    flags: int | None = None

    extended_payload: bytes = b""
    auxiliary_packets: list[BLEAdvertisingPDU] = field(default_factory=lambda: cast(list[BLEAdvertisingPDU], []))
    periodic_advertising_data: bytes = b""
    broadcast_code: bytes = b""

    @property
    def is_extended_advertising(self) -> bool:
        """Check if this advertisement uses extended advertising."""
        return bool(self.extended_payload) or bool(self.auxiliary_packets)

    @property
    def total_payload_size(self) -> int:
        """Get total payload size including extended data."""
        base_size = len(self.raw_data)
        if self.extended_payload:
            base_size += len(self.extended_payload)
        for aux_packet in self.auxiliary_packets:
            base_size += len(aux_packet.payload)
        return base_size

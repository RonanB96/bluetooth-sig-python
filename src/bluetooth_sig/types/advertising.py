"""BLE Advertising data types and parsing utilities."""

from __future__ import annotations

from enum import IntEnum, IntFlag
from typing import TYPE_CHECKING

import msgspec

if TYPE_CHECKING:
    from bluetooth_sig.types.appearance import AppearanceData
    from bluetooth_sig.types.class_of_device import ClassOfDeviceInfo


class ADTypeInfo(msgspec.Struct, frozen=True, kw_only=True):
    """AD Type information from Bluetooth SIG spec.

    Attributes:
        value: The AD type value (e.g., 0x01 for Flags)
        name: Human-readable name from the specification
        reference: Optional specification reference
    """

    value: int
    name: str
    reference: str | None = None


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


class PDUConstants:
    """BLE PDU parsing constants for sizes and offsets.

    Following best practices, this uses a class for related
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


class BLEAdvertisingFlags(IntFlag):
    """BLE Advertising Flags as defined in Bluetooth Core Specification Supplement.

    These flags indicate the discoverable mode and capabilities of the advertising device.
    """

    LE_LIMITED_DISCOVERABLE_MODE = 0x01
    LE_GENERAL_DISCOVERABLE_MODE = 0x02
    BR_EDR_NOT_SUPPORTED = 0x04
    SIMULTANEOUS_LE_BR_EDR_CONTROLLER = 0x08
    SIMULTANEOUS_LE_BR_EDR_HOST = 0x10
    RESERVED_BIT_5 = 0x20
    RESERVED_BIT_6 = 0x40
    RESERVED_BIT_7 = 0x80


class BLEExtendedHeader(msgspec.Struct, kw_only=True):
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


class BLEAdvertisingPDU(msgspec.Struct, kw_only=True):
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


class ParsedADStructures(msgspec.Struct, kw_only=True):
    """Parsed Advertising Data structures from advertisement payload."""

    manufacturer_data: dict[int, bytes] = msgspec.field(default_factory=dict)
    service_uuids: list[str] = msgspec.field(default_factory=list)
    local_name: str = ""
    tx_power: int = 0
    flags: BLEAdvertisingFlags = BLEAdvertisingFlags(0)
    appearance: AppearanceData | None = None
    service_data: dict[str, bytes] = msgspec.field(default_factory=dict)
    solicited_service_uuids: list[str] = msgspec.field(default_factory=list)
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
    public_target_address: list[str] = msgspec.field(default_factory=list)
    random_target_address: list[str] = msgspec.field(default_factory=list)
    advertising_interval: int | None = None
    advertising_interval_long: int | None = None
    le_bluetooth_device_address: str = ""
    le_role: int | None = None
    class_of_device: int | None = None
    class_of_device_info: ClassOfDeviceInfo | None = None
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


class DeviceAdvertiserData(msgspec.Struct, kw_only=True):
    """Parsed advertiser data from device discovery."""

    raw_data: bytes
    parsed_structures: ParsedADStructures = msgspec.field(default_factory=ParsedADStructures)

    # Frequently accessed fields (for backward compatibility and convenience)
    local_name: str = ""
    manufacturer_data: dict[int, bytes] = msgspec.field(default_factory=dict)
    service_uuids: list[str] = msgspec.field(default_factory=list)
    tx_power: int | None = None
    rssi: int | None = None
    flags: BLEAdvertisingFlags | None = None
    appearance: AppearanceData | None = None

    # Extended advertising specific fields
    extended_payload: bytes = b""
    auxiliary_packets: list[BLEAdvertisingPDU] = msgspec.field(default_factory=list)
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

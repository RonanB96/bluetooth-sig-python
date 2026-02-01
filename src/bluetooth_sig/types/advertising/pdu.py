"""BLE Advertising PDU types and header structures.

Core PDU-level definitions following Bluetooth Core Spec Vol 6, Part B.
"""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from bluetooth_sig.types.advertising.extended import (
    AdvertisingDataInfo,
    AuxiliaryPointer,
    CTEInfo,
    SyncInfo,
)


class PDUType(IntEnum):
    """BLE Advertising PDU Types (Core Spec Vol 6, Part B, Section 2.3)."""

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


class PDUHeaderFlags(IntFlag):
    """BLE PDU header bit masks for parsing operations.

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


class PDULayout:
    """BLE PDU structure size and offset constants.

    Defines the sizes and offsets of fields within BLE PDU structures
    following Bluetooth Core Spec Vol 6, Part B.
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


class ExtendedHeaderFlags(IntEnum):
    """Extended advertising header field presence flags (BLE 5.0+).

    Each flag indicates whether a corresponding field is present
    in the extended advertising header.
    """

    ADV_ADDR = 0x01
    TARGET_ADDR = 0x02
    CTE_INFO = 0x04
    ADV_DATA_INFO = 0x08
    AUX_PTR = 0x10
    SYNC_INFO = 0x20
    TX_POWER = 0x40
    ACAD = 0x80


class BLEExtendedHeader(msgspec.Struct, kw_only=True):
    """Extended Advertising Header fields (BLE 5.0+)."""

    extended_header_length: int = 0
    adv_mode: int = 0

    extended_advertiser_address: str = ""  # MAC address XX:XX:XX:XX:XX:XX
    extended_target_address: str = ""  # MAC address XX:XX:XX:XX:XX:XX
    cte_info: CTEInfo | None = None
    advertising_data_info: AdvertisingDataInfo | None = None
    auxiliary_pointer: AuxiliaryPointer | None = None
    sync_info: SyncInfo | None = None
    tx_power: int | None = None
    additional_controller_advertising_data: bytes = b""

    @property
    def has_extended_advertiser_address(self) -> bool:
        """Check if extended advertiser address is present."""
        return bool(self.adv_mode & ExtendedHeaderFlags.ADV_ADDR)

    @property
    def has_extended_target_address(self) -> bool:
        """Check if extended target address is present."""
        return bool(self.adv_mode & ExtendedHeaderFlags.TARGET_ADDR)

    @property
    def has_cte_info(self) -> bool:
        """Check if CTE info is present."""
        return bool(self.adv_mode & ExtendedHeaderFlags.CTE_INFO)

    @property
    def has_advertising_data_info(self) -> bool:
        """Check if advertising data info is present."""
        return bool(self.adv_mode & ExtendedHeaderFlags.ADV_DATA_INFO)

    @property
    def has_auxiliary_pointer(self) -> bool:
        """Check if auxiliary pointer is present."""
        return bool(self.adv_mode & ExtendedHeaderFlags.AUX_PTR)

    @property
    def has_sync_info(self) -> bool:
        """Check if sync info is present."""
        return bool(self.adv_mode & ExtendedHeaderFlags.SYNC_INFO)

    @property
    def has_tx_power(self) -> bool:
        """Check if TX power is present."""
        return bool(self.adv_mode & ExtendedHeaderFlags.TX_POWER)

    @property
    def has_additional_controller_data(self) -> bool:
        """Check if additional controller advertising data is present."""
        return bool(self.adv_mode & ExtendedHeaderFlags.ACAD)


class BLEAdvertisingPDU(msgspec.Struct, kw_only=True):
    """BLE Advertising PDU structure."""

    pdu_type: PDUType
    tx_add: bool
    rx_add: bool
    length: int
    advertiser_address: str = ""  # MAC address XX:XX:XX:XX:XX:XX
    target_address: str = ""  # MAC address XX:XX:XX:XX:XX:XX
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

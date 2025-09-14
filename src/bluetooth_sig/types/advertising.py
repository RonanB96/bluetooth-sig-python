"""BLE Advertising data types and parsing utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


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
    """BLE Advertisement Data Types (AD Types) as defined in Bluetooth Core Specification."""

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
class BLEExtendedHeader:
    """Extended Advertising Header fields (BLE 5.0+)."""

    # pylint: disable=too-many-instance-attributes

    extended_header_length: int = 0
    adv_mode: int = 0  # Advertising Mode (bit field)

    # Optional extended header fields
    extended_advertiser_address: bytes | None = None
    extended_target_address: bytes | None = None
    cte_info: bytes | None = None
    advertising_data_info: bytes | None = None
    auxiliary_pointer: bytes | None = None
    sync_info: bytes | None = None
    tx_power: int | None = None
    additional_controller_advertising_data: bytes | None = None

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
class BLEAdvertisingPDU:
    """BLE Advertising PDU structure."""

    # pylint: disable=too-many-instance-attributes

    pdu_type: int
    tx_add: bool  # TX Address type (0=public, 1=random)
    rx_add: bool  # RX Address type (0=public, 1=random)
    length: int
    advertiser_address: bytes | None = None
    target_address: bytes | None = None
    payload: bytes = b""
    extended_header: BLEExtendedHeader | None = None

    @property
    def is_extended_advertising(self) -> bool:
        """Check if this is an extended advertising PDU."""
        try:
            return PDUType(self.pdu_type).is_extended_advertising
        except ValueError:
            return False

    @property
    def is_legacy_advertising(self) -> bool:
        """Check if this is a legacy advertising PDU."""
        try:
            return PDUType(self.pdu_type).is_legacy_advertising
        except ValueError:
            return False

    @property
    def pdu_name(self) -> str:
        """Get human-readable PDU type name."""
        try:
            return PDUType(self.pdu_type).name
        except ValueError:
            return f"Unknown (0x{self.pdu_type:02X})"


@dataclass
class ParsedADStructures:
    """Parsed Advertising Data structures from advertisement payload."""

    # pylint: disable=too-many-instance-attributes

    manufacturer_data: dict[int, bytes] = field(default_factory=dict)
    service_uuids: list[str] = field(default_factory=list)
    local_name: str = ""
    tx_power: int | None = None
    flags: int | None = None
    appearance: int | None = None
    service_data: dict[str, bytes] = field(default_factory=dict)
    solicited_service_uuids: list[str] = field(default_factory=list)
    uri: str | None = None
    indoor_positioning: bytes | None = None
    transport_discovery_data: bytes | None = None
    le_supported_features: bytes | None = None
    encrypted_advertising_data: bytes | None = None
    periodic_advertising_response_timing: bytes | None = None
    electronic_shelf_label: bytes | None = None
    three_d_information: bytes | None = None
    broadcast_name: str | None = None
    broadcast_code: bytes | None = None
    biginfo: bytes | None = None
    mesh_message: bytes | None = None
    mesh_beacon: bytes | None = None
    public_target_address: list[str] = field(default_factory=list)
    random_target_address: list[str] = field(default_factory=list)
    advertising_interval: int | None = None
    advertising_interval_long: int | None = None
    le_bluetooth_device_address: str | None = None
    le_role: int | None = None
    class_of_device: int | None = None
    simple_pairing_hash_c: bytes | None = None
    simple_pairing_randomizer_r: bytes | None = None
    security_manager_tk_value: bytes | None = None
    security_manager_out_of_band_flags: bytes | None = None
    slave_connection_interval_range: bytes | None = None
    secure_connections_confirmation: bytes | None = None
    secure_connections_random: bytes | None = None
    channel_map_update_indication: bytes | None = None
    pb_adv: bytes | None = None
    resolvable_set_identifier: bytes | None = None


@dataclass
class DeviceAdvertiserData:
    """Parsed advertiser data from device discovery."""

    # pylint: disable=too-many-instance-attributes

    raw_data: bytes
    local_name: str = ""
    manufacturer_data: dict[int, bytes] = field(default_factory=dict)
    service_uuids: list[str] = field(default_factory=list)
    tx_power: int | None = None
    rssi: int | None = None
    flags: int | None = None

    # Extended advertising fields
    extended_payload: bytes | None = None
    auxiliary_packets: list[BLEAdvertisingPDU] = field(default_factory=list)
    periodic_advertising_data: bytes | None = None
    broadcast_code: bytes | None = None

    @property
    def is_extended_advertising(self) -> bool:
        """Check if this advertisement uses extended advertising."""
        return self.extended_payload is not None or bool(self.auxiliary_packets)

    @property
    def total_payload_size(self) -> int:
        """Get total payload size including extended data."""
        base_size = len(self.raw_data)
        if self.extended_payload:
            base_size += len(self.extended_payload)
        for aux_packet in self.auxiliary_packets:
            base_size += len(aux_packet.payload)
        return base_size

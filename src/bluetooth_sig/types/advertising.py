"""BLE Advertising data types and parsing utilities.

Organization:
    1. Core PDU Types and Enums - Low-level PDU structure definitions
    2. Advertising Data Type Registry - AD Type metadata
    3. Advertising Flags - Device discovery and capabilities flags
    4. PDU and Header Structures - Structured PDU representations
    5. Parsed Advertising Data - High-level parsed advertisement content
"""

from __future__ import annotations

from enum import IntEnum, IntFlag
from typing import Any

import msgspec

from bluetooth_sig.types.appearance import AppearanceData
from bluetooth_sig.types.company import ManufacturerData
from bluetooth_sig.types.registry.class_of_device import ClassOfDeviceInfo
from bluetooth_sig.types.uri import URIData
from bluetooth_sig.types.uuid import BluetoothUUID


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


class BLEAdvertisingFlags(IntFlag):
    """BLE Advertising Flags (Core Spec Supplement, Part A, Section 1.3).

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


class CTEType(IntEnum):
    """Constant Tone Extension (CTE) Types (Core Spec Vol 6, Part B, Section 2.5)."""

    AOA = 0x00  # Angle of Arrival
    AOD_1US = 0x01  # Angle of Departure with 1μs slots
    AOD_2US = 0x02  # Angle of Departure with 2μs slots


class CTEInfo(msgspec.Struct, kw_only=True):
    """Constant Tone Extension (CTE) information (BLE 5.1+ Direction Finding).

    Attributes:
        cte_time: CTE length in 8μs units (0-19, representing 16-160μs)
        cte_type: Type of CTE (AoA, AoD 1μs, or AoD 2μs)
    """

    cte_time: int
    cte_type: CTEType


class AdvertisingDataInfo(msgspec.Struct, kw_only=True):
    """Advertising Data Info (ADI) field (BLE 5.0+).

    Attributes:
        advertising_data_id: Advertising Data ID (DID) - 12 bits
        advertising_set_id: Advertising Set ID (SID) - 4 bits
    """

    advertising_data_id: int  # 12-bit DID (0-4095)
    advertising_set_id: int  # 4-bit SID (0-15)


class PHYType(IntEnum):
    """PHY types for auxiliary channel (Core Spec Vol 6, Part B, Section 2.3.4.6)."""

    LE_1M = 0x00
    LE_2M = 0x01
    LE_CODED = 0x02


class AuxiliaryPointer(msgspec.Struct, kw_only=True):
    """Auxiliary Pointer for chaining extended advertising packets (BLE 5.0+).

    Attributes:
        channel_index: Advertising channel index (0-39)
        ca: Clock accuracy (0=51-500ppm, 1=0-50ppm)
        offset_units: Units for aux_offset (0=30μs, 1=300μs)
        aux_offset: Time offset to auxiliary packet (13 bits)
        aux_phy: PHY used for auxiliary packet
    """

    channel_index: int  # 0-39
    ca: bool
    offset_units: int  # 0 or 1
    aux_offset: int  # 13-bit value
    aux_phy: PHYType


class SyncInfo(msgspec.Struct, kw_only=True):
    """Synchronization Info for Periodic Advertising (BLE 5.0+).

    Attributes:
        sync_packet_offset: Offset to first periodic advertising packet (13 bits, 30μs units)
        offset_units: Units for sync_packet_offset (0=30μs, 1=300μs)
        interval: Periodic advertising interval (1.25ms units, range: 7.5ms-81.91875s)
        channel_map: Channel map for periodic advertising (37 bits)
        sleep_clock_accuracy: Sleep clock accuracy (0-7, represents ppm ranges)
        advertising_address: Advertiser address (6 bytes)
        advertising_address_type: 0=Public, 1=Random
        sync_counter: Synchronization counter for packet identification
    """

    sync_packet_offset: int  # 13 bits
    offset_units: int  # 0 or 1
    interval: int  # Periodic advertising interval in 1.25ms units
    channel_map: int  # 37-bit channel map
    sleep_clock_accuracy: int  # 0-7 (ppm ranges)
    advertising_address: str  # MAC address
    advertising_address_type: int  # 0 or 1
    sync_counter: int  # Packet counter


class ConnectionIntervalRange(msgspec.Struct, kw_only=True):
    """Peripheral preferred connection interval range (Core Spec Supplement, Part A, Section 1.9).

    Attributes:
        min_interval: Minimum connection interval in 1.25ms units
        max_interval: Maximum connection interval in 1.25ms units
        min_interval_ms: Minimum connection interval in milliseconds
        max_interval_ms: Maximum connection interval in milliseconds
    """

    INTERVAL_UNIT_MS: float = 1.25  # Connection interval unit in milliseconds

    min_interval: int  # In 1.25ms units
    max_interval: int  # In 1.25ms units

    @property
    def min_interval_ms(self) -> float:
        """Get minimum interval in milliseconds."""
        return self.min_interval * self.INTERVAL_UNIT_MS

    @property
    def max_interval_ms(self) -> float:
        """Get maximum interval in milliseconds."""
        return self.max_interval * self.INTERVAL_UNIT_MS


class LEFeatureBits(IntFlag):
    """LE Supported Features bit definitions (Core Spec Vol 6, Part B, Section 4.6).

    Byte 0 features (bits 0-7).
    """

    # Byte 0 features
    LE_ENCRYPTION = 0x0001
    CONNECTION_PARAMETERS_REQUEST = 0x0002
    EXTENDED_REJECT_INDICATION = 0x0004
    PERIPHERAL_INITIATED_FEATURES_EXCHANGE = 0x0008
    LE_PING = 0x0010
    LE_DATA_PACKET_LENGTH_EXTENSION = 0x0020
    LL_PRIVACY = 0x0040
    EXTENDED_SCANNER_FILTER_POLICIES = 0x0080

    # Byte 1 features (bits 8-15)
    LE_2M_PHY = 0x0100
    STABLE_MODULATION_INDEX_TX = 0x0200
    STABLE_MODULATION_INDEX_RX = 0x0400
    LE_CODED_PHY = 0x0800
    LE_EXTENDED_ADVERTISING = 0x1000
    LE_PERIODIC_ADVERTISING = 0x2000
    CHANNEL_SELECTION_ALGORITHM_2 = 0x4000
    LE_POWER_CLASS_1 = 0x8000

    # Byte 2 features (bits 16-23)
    MIN_NUMBER_OF_USED_CHANNELS = 0x010000
    CONNECTION_CTE_REQUEST = 0x020000
    CONNECTION_CTE_RESPONSE = 0x040000
    CONNECTIONLESS_CTE_TX = 0x080000
    CONNECTIONLESS_CTE_RX = 0x100000
    ANTENNA_SWITCHING_TX = 0x200000
    ANTENNA_SWITCHING_RX = 0x400000
    RECEIVING_CTE = 0x800000


class LEFeatures(msgspec.Struct, kw_only=True):  # pylint: disable=too-many-public-methods  # One property per LE feature bit
    """LE Supported Features bit field (Core Spec Vol 6, Part B, Section 4.6).

    Attributes:
        raw_value: Raw feature bit field bytes (up to 8 bytes)
    """

    raw_value: bytes

    def _get_features_int(self) -> int:
        """Convert raw bytes to integer for bit checking."""
        return int.from_bytes(self.raw_value, byteorder="little") if self.raw_value else 0

    def _has_feature(self, feature: LEFeatureBits) -> bool:
        """Check if a specific feature bit is set."""
        return bool(self._get_features_int() & feature)

    @property
    def le_encryption(self) -> bool:
        """LE Encryption supported."""
        return self._has_feature(LEFeatureBits.LE_ENCRYPTION)

    @property
    def connection_parameters_request(self) -> bool:
        """Connection Parameters Request Procedure."""
        return self._has_feature(LEFeatureBits.CONNECTION_PARAMETERS_REQUEST)

    @property
    def extended_reject_indication(self) -> bool:
        """Extended Reject Indication."""
        return self._has_feature(LEFeatureBits.EXTENDED_REJECT_INDICATION)

    @property
    def peripheral_initiated_features_exchange(self) -> bool:
        """Peripheral-initiated Features Exchange."""
        return self._has_feature(LEFeatureBits.PERIPHERAL_INITIATED_FEATURES_EXCHANGE)

    @property
    def le_ping(self) -> bool:
        """LE Ping."""
        return self._has_feature(LEFeatureBits.LE_PING)

    @property
    def le_data_packet_length_extension(self) -> bool:
        """LE Data Packet Length Extension."""
        return self._has_feature(LEFeatureBits.LE_DATA_PACKET_LENGTH_EXTENSION)

    @property
    def ll_privacy(self) -> bool:
        """LL Privacy."""
        return self._has_feature(LEFeatureBits.LL_PRIVACY)

    @property
    def extended_scanner_filter_policies(self) -> bool:
        """Extended Scanner Filter Policies."""
        return self._has_feature(LEFeatureBits.EXTENDED_SCANNER_FILTER_POLICIES)

    @property
    def le_2m_phy(self) -> bool:
        """LE 2M PHY."""
        return self._has_feature(LEFeatureBits.LE_2M_PHY)

    @property
    def stable_modulation_index_tx(self) -> bool:
        """Stable Modulation Index - Transmitter."""
        return self._has_feature(LEFeatureBits.STABLE_MODULATION_INDEX_TX)

    @property
    def stable_modulation_index_rx(self) -> bool:
        """Stable Modulation Index - Receiver."""
        return self._has_feature(LEFeatureBits.STABLE_MODULATION_INDEX_RX)

    @property
    def le_coded_phy(self) -> bool:
        """LE Coded PHY."""
        return self._has_feature(LEFeatureBits.LE_CODED_PHY)

    @property
    def le_extended_advertising(self) -> bool:
        """LE Extended Advertising."""
        return self._has_feature(LEFeatureBits.LE_EXTENDED_ADVERTISING)

    @property
    def le_periodic_advertising(self) -> bool:
        """LE Periodic Advertising."""
        return self._has_feature(LEFeatureBits.LE_PERIODIC_ADVERTISING)

    @property
    def channel_selection_algorithm_2(self) -> bool:
        """Channel Selection Algorithm #2."""
        return self._has_feature(LEFeatureBits.CHANNEL_SELECTION_ALGORITHM_2)

    @property
    def le_power_class_1(self) -> bool:
        """LE Power Class 1."""
        return self._has_feature(LEFeatureBits.LE_POWER_CLASS_1)

    @property
    def min_number_of_used_channels(self) -> bool:
        """Minimum Number of Used Channels Procedure."""
        return self._has_feature(LEFeatureBits.MIN_NUMBER_OF_USED_CHANNELS)

    @property
    def connection_cte_request(self) -> bool:
        """Connection CTE Request."""
        return self._has_feature(LEFeatureBits.CONNECTION_CTE_REQUEST)

    @property
    def connection_cte_response(self) -> bool:
        """Connection CTE Response."""
        return self._has_feature(LEFeatureBits.CONNECTION_CTE_RESPONSE)

    @property
    def connectionless_cte_tx(self) -> bool:
        """Connectionless CTE Transmitter."""
        return self._has_feature(LEFeatureBits.CONNECTIONLESS_CTE_TX)

    @property
    def connectionless_cte_rx(self) -> bool:
        """Connectionless CTE Receiver."""
        return self._has_feature(LEFeatureBits.CONNECTIONLESS_CTE_RX)

    @property
    def antenna_switching_tx(self) -> bool:
        """Antenna Switching During CTE Transmission."""
        return self._has_feature(LEFeatureBits.ANTENNA_SWITCHING_TX)

    @property
    def antenna_switching_rx(self) -> bool:
        """Antenna Switching During CTE Reception."""
        return self._has_feature(LEFeatureBits.ANTENNA_SWITCHING_RX)

    @property
    def receiving_cte(self) -> bool:
        """Receiving Constant Tone Extensions."""
        return self._has_feature(LEFeatureBits.RECEIVING_CTE)


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


class CoreAdvertisingData(msgspec.Struct, kw_only=True):
    """Core advertising data - device identification and services.

    Attributes:
        manufacturer_data: Manufacturer-specific data keyed by company ID.
                          Each entry contains resolved company info and payload bytes.
        service_uuids: List of advertised service UUIDs
        service_data: Service-specific data keyed by service UUID
        solicited_service_uuids: List of service UUIDs the device is seeking
        local_name: Device's local name (complete or shortened)
        uri_data: Parsed URI with scheme info from UriSchemesRegistry
    """

    manufacturer_data: dict[int, ManufacturerData] = msgspec.field(default_factory=dict)
    service_uuids: list[BluetoothUUID] = msgspec.field(default_factory=list)
    service_data: dict[BluetoothUUID, bytes] = msgspec.field(default_factory=dict)
    solicited_service_uuids: list[BluetoothUUID] = msgspec.field(default_factory=list)
    local_name: str = ""
    uri_data: URIData | None = None


class DeviceProperties(msgspec.Struct, kw_only=True):
    """Device capability and appearance properties.

    Attributes:
        flags: BLE advertising flags (discoverable mode, capabilities)
        appearance: Device appearance category and subcategory
        tx_power: Transmission power level in dBm
        le_role: LE role (peripheral, central, etc.)
        le_supported_features: LE supported features with property accessors
        class_of_device: Classic Bluetooth Class of Device value
        class_of_device_info: Parsed Class of Device information
    """

    flags: BLEAdvertisingFlags = BLEAdvertisingFlags(0)
    appearance: AppearanceData | None = None
    tx_power: int = 0
    le_role: int | None = None
    le_supported_features: LEFeatures | None = None
    class_of_device: ClassOfDeviceInfo | None = None


class DirectedAdvertisingData(msgspec.Struct, kw_only=True):
    """Directed advertising and timing parameters.

    These AD types specify target devices and advertising timing.

    Attributes:
        public_target_address: List of public target addresses (AD 0x17)
        random_target_address: List of random target addresses (AD 0x18)
        le_bluetooth_device_address: LE Bluetooth device address (AD 0x1B)
        advertising_interval: Advertising interval in 0.625ms units (AD 0x1A)
        advertising_interval_long: Long advertising interval (AD 0x2F)
        peripheral_connection_interval_range: Preferred connection interval with min/max (AD 0x12)
    """

    public_target_address: list[str] = msgspec.field(default_factory=list)
    random_target_address: list[str] = msgspec.field(default_factory=list)
    le_bluetooth_device_address: str = ""
    advertising_interval: int | None = None
    advertising_interval_long: int | None = None
    peripheral_connection_interval_range: ConnectionIntervalRange | None = None


class OOBSecurityData(msgspec.Struct, kw_only=True):
    """Out-of-Band (OOB) security data advertised for pairing.

    These AD types provide security material for OOB pairing mechanisms.

    Attributes:
        simple_pairing_hash_c: Simple Pairing Hash C-192/C-256 (AD 0x0E, 0x1D)
        simple_pairing_randomizer_r: Simple Pairing Randomizer R-192/R-256 (AD 0x0F, 0x1E)
        secure_connections_confirmation: LE SC Confirmation Value (AD 0x22)
        secure_connections_random: LE SC Random Value (AD 0x23)
        security_manager_tk_value: Security Manager TK Value (AD 0x10)
        security_manager_oob_flags: SM Out of Band Flags (AD 0x11)
    """

    simple_pairing_hash_c: bytes = b""
    simple_pairing_randomizer_r: bytes = b""
    secure_connections_confirmation: bytes = b""
    secure_connections_random: bytes = b""
    security_manager_tk_value: bytes = b""
    security_manager_oob_flags: bytes = b""


class LocationAndSensingData(msgspec.Struct, kw_only=True):
    """Location, positioning, and sensing related data.

    Attributes:
        indoor_positioning: Indoor positioning data
        three_d_information: 3D information data
        transport_discovery_data: Transport Discovery Data
        channel_map_update_indication: Channel Map Update Indication
    """

    indoor_positioning: bytes = b""
    three_d_information: bytes = b""
    transport_discovery_data: bytes = b""
    channel_map_update_indication: bytes = b""


class MeshAndBroadcastData(msgspec.Struct, kw_only=True):
    """Bluetooth Mesh and audio broadcast related data.

    Attributes:
        mesh_message: Mesh Message
        mesh_beacon: Mesh Beacon
        pb_adv: Provisioning Bearer over advertising
        broadcast_name: Broadcast name
        broadcast_code: Broadcast Code for encrypted audio
        biginfo: BIG Info for Broadcast Isochronous Groups
        periodic_advertising_response_timing: Periodic Advertising Response Timing Info
        electronic_shelf_label: Electronic Shelf Label data
    """

    mesh_message: bytes = b""
    mesh_beacon: bytes = b""
    pb_adv: bytes = b""
    broadcast_name: str = ""
    broadcast_code: bytes = b""
    biginfo: bytes = b""
    periodic_advertising_response_timing: bytes = b""
    electronic_shelf_label: bytes = b""


class SecurityData(msgspec.Struct, kw_only=True):
    """Security and encryption related advertising data.

    Attributes:
        encrypted_advertising_data: Encrypted Advertising Data
        resolvable_set_identifier: Resolvable Set Identifier
    """

    encrypted_advertising_data: bytes = b""
    resolvable_set_identifier: bytes = b""


class ExtendedAdvertisingData(msgspec.Struct, kw_only=True):
    """Extended advertising PDU-level metadata (BLE 5.0+).

    This contains PDU-level information specific to extended advertising,
    NOT AD types (which go in AdvertisingDataStructures).

    Attributes:
        extended_payload: Raw extended advertising payload bytes
        auxiliary_packets: Chained AUX_ADV_IND packets via AuxPtr
        periodic_advertising_data: Data from periodic advertising train
    """

    extended_payload: bytes = b""
    auxiliary_packets: list[BLEAdvertisingPDU] = msgspec.field(default_factory=list)
    periodic_advertising_data: bytes = b""


class AdvertisingDataStructures(msgspec.Struct, kw_only=True):
    """Complete parsed advertising data structures organized by category.

    Contains all AD Types parsed from advertising PDUs (both legacy and extended).
    These are payload content, not PDU-level metadata.

    Attributes:
        core: Device identification and services (manufacturer data, UUIDs, name)
        properties: Device capabilities (flags, appearance, tx_power, features)
        directed: Directed advertising parameters (target addresses, intervals)
        oob_security: Out-of-Band security data for pairing
        location: Location and sensing data
        mesh: Mesh network and broadcast audio data
        security: Encrypted advertising and privacy data
    """

    core: CoreAdvertisingData = msgspec.field(default_factory=CoreAdvertisingData)
    properties: DeviceProperties = msgspec.field(default_factory=DeviceProperties)
    directed: DirectedAdvertisingData = msgspec.field(default_factory=DirectedAdvertisingData)
    oob_security: OOBSecurityData = msgspec.field(default_factory=OOBSecurityData)
    location: LocationAndSensingData = msgspec.field(default_factory=LocationAndSensingData)
    mesh: MeshAndBroadcastData = msgspec.field(default_factory=MeshAndBroadcastData)
    security: SecurityData = msgspec.field(default_factory=SecurityData)


class AdvertisingData(msgspec.Struct, kw_only=True):
    """Complete BLE advertising data with device information and metadata.

    Attributes:
        raw_data: Raw bytes from the advertising packet
        ad_structures: Parsed AD structures organized by category
        extended: Extended advertising data (BLE 5.0+)
        rssi: Received signal strength indicator in dBm
    """

    raw_data: bytes
    ad_structures: AdvertisingDataStructures = msgspec.field(default_factory=AdvertisingDataStructures)
    extended: ExtendedAdvertisingData = msgspec.field(default_factory=ExtendedAdvertisingData)
    rssi: int | None = None

    @property
    def is_extended_advertising(self) -> bool:
        """Check if this advertisement uses extended advertising."""
        return bool(self.extended.extended_payload) or bool(self.extended.auxiliary_packets)

    @property
    def total_payload_size(self) -> int:
        """Get total payload size including extended data."""
        base_size = len(self.raw_data)
        if self.extended.extended_payload:
            base_size += len(self.extended.extended_payload)
        for aux_packet in self.extended.auxiliary_packets:
            base_size += len(aux_packet.payload)
        return base_size


class AdvertisementData(msgspec.Struct, kw_only=True):
    """Complete parsed advertisement with PDU structures and interpreted data.

    This is the unified result from Device.update_advertisement(), containing
    both low-level AD structures and high-level vendor-specific interpretation.

    The interpreted_data field is typed as Any to maintain msgspec.Struct compatibility
    while supporting generic vendor-specific result types at runtime.

    Attributes:
        ad_structures: Parsed AD structures (manufacturer_data, service_data, etc.)
        interpreted_data: Vendor-specific typed result (e.g., sensor readings), or None
        interpreter_name: Name of the interpreter used (e.g., "BTHome", "Xiaomi"), or None
        rssi: Received signal strength indicator in dBm

    Example:
        # Using connection manager (recommended)
        ad_data = BleakConnectionManager.convert_advertisement(bleak_advertisement)
        result = device.update_advertisement(ad_data)

        # Access low-level AD structures
        print(result.ad_structures.core.manufacturer_data)  # {0x0499: b'...'}
        print(result.ad_structures.properties.flags)

        # Access vendor-specific interpreted data
        if result.interpreted_data:
            print(f"Interpreter: {result.interpreter_name}")
            print(f"Temperature: {result.interpreted_data.temperature}")

    """

    ad_structures: AdvertisingDataStructures = msgspec.field(default_factory=AdvertisingDataStructures)
    interpreted_data: Any = None
    interpreter_name: str | None = None
    rssi: int | None = None

    @property
    def manufacturer_data(self) -> dict[int, ManufacturerData]:
        """Convenience accessor for manufacturer data (company_id → ManufacturerData)."""
        return self.ad_structures.core.manufacturer_data

    @property
    def service_data(self) -> dict[BluetoothUUID, bytes]:
        """Convenience accessor for service data (UUID → payload)."""
        return self.ad_structures.core.service_data

    @property
    def local_name(self) -> str:
        """Convenience accessor for device local name."""
        return self.ad_structures.core.local_name

    @property
    def has_interpretation(self) -> bool:
        """Check if vendor-specific interpretation was applied."""
        return self.interpreted_data is not None

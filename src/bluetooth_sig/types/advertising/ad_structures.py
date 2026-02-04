"""Parsed AD structure categories.

Organized by Bluetooth Core Specification Supplement AD type categories.
"""

from __future__ import annotations

import msgspec

from bluetooth_sig.types.advertising.features import LEFeatures
from bluetooth_sig.types.advertising.flags import BLEAdvertisingFlags
from bluetooth_sig.types.advertising.pdu import BLEAdvertisingPDU
from bluetooth_sig.types.appearance import AppearanceData
from bluetooth_sig.types.company import ManufacturerData
from bluetooth_sig.types.mesh import (
    MeshMessage,
    ProvisioningBearerData,
    SecureNetworkBeacon,
    UnprovisionedDeviceBeacon,
)
from bluetooth_sig.types.registry.class_of_device import ClassOfDeviceInfo
from bluetooth_sig.types.uri import URIData
from bluetooth_sig.types.uuid import BluetoothUUID


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
        mesh_message: Parsed Mesh Network PDU message
        secure_network_beacon: Parsed Secure Network Beacon (provisioned nodes)
        unprovisioned_device_beacon: Parsed Unprovisioned Device Beacon
        provisioning_bearer: Parsed Provisioning Bearer (PB-ADV) data
        broadcast_name: Broadcast name for LE Audio
        broadcast_code: Broadcast Code for encrypted audio
        biginfo: BIG Info for Broadcast Isochronous Groups
        periodic_advertising_response_timing: Periodic Advertising Response Timing Info
        electronic_shelf_label: Electronic Shelf Label data

    """

    mesh_message: MeshMessage | None = None
    secure_network_beacon: SecureNetworkBeacon | None = None
    unprovisioned_device_beacon: UnprovisionedDeviceBeacon | None = None
    provisioning_bearer: ProvisioningBearerData | None = None
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

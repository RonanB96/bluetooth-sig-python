"""Bluetooth Mesh protocol types per Bluetooth Mesh Profile Specification.

This module contains types for Bluetooth Mesh protocol structures including
beacon types, provisioning PDUs, and mesh network data.

Reference: Bluetooth Mesh Profile Specification v1.1
"""

from __future__ import annotations

import secrets
import struct
from enum import IntEnum, IntFlag

import msgspec

# =============================================================================
# Bluetooth Mesh Protocol Sizes (bytes)
# =============================================================================
NETWORK_ID_LENGTH = 8
NETWORK_KEY_LENGTH = 16
DEVICE_UUID_LENGTH = 16
AUTHENTICATION_VALUE_LENGTH = 8
OOB_INFO_LENGTH = 2
URI_HASH_LENGTH = 4
UNPROVISIONED_BEACON_MIN_LENGTH = DEVICE_UUID_LENGTH + OOB_INFO_LENGTH
UNPROVISIONED_BEACON_WITH_HASH_LENGTH = UNPROVISIONED_BEACON_MIN_LENGTH + URI_HASH_LENGTH

# Network MIC lengths per Bluetooth Mesh Profile 3.4.3
ACCESS_MESSAGE_MIC_LENGTH = 4
CONTROL_MESSAGE_MIC_LENGTH = 8

# Mesh Provisioning algorithm constants
ALGORITHM_FIPS_P256 = 0x0001
PUBLIC_KEY_TYPE_NONE = 0x00
STATIC_OOB_TYPE_NONE = 0x00

# =============================================================================
# Enums and Flags
# =============================================================================


class SecureNetworkBeaconFlags(IntFlag):
    """Secure Network Beacon flags per Bluetooth Mesh Profile 3.10.3.

    These flags are combined in the beacon's flags byte.
    """

    NONE = 0x00
    KEY_REFRESH = 0x01
    IV_UPDATE = 0x02


class MeshBeaconType(IntEnum):
    """Mesh beacon types per Bluetooth Mesh Profile 3.10.

    These identify the type of mesh beacon being broadcast.
    """

    UNPROVISIONED_DEVICE = 0x00
    SECURE_NETWORK = 0x01


class ProvisioningPDUType(IntEnum):
    """Mesh Provisioning PDU types per Bluetooth Mesh Profile 5.4.

    These identify the provisioning protocol message type.
    """

    INVITE = 0x00
    CAPABILITIES = 0x01
    START = 0x02
    PUBLIC_KEY = 0x03
    INPUT_COMPLETE = 0x04
    CONFIRMATION = 0x05
    RANDOM = 0x06
    DATA = 0x07
    COMPLETE = 0x08
    FAILED = 0x09


class MeshCapabilities(msgspec.Struct, frozen=True, kw_only=True):
    """Mesh Provisioning Capabilities per Bluetooth Mesh Profile 5.4.1.2.

    This structure describes the device's provisioning capabilities
    and is sent in response to a Provisioning Invite PDU.

    Attributes:
        num_elements: Number of elements supported by the device
        algorithms: Supported provisioning algorithms (bitmask)
        public_key_type: Supported public key types
        static_oob_type: Supported static OOB types
        output_oob_size: Maximum size of Output OOB
        output_oob_action: Supported Output OOB actions
        input_oob_size: Maximum size of Input OOB
        input_oob_action: Supported Input OOB actions

    """

    num_elements: int = 1
    algorithms: int = ALGORITHM_FIPS_P256
    public_key_type: int = PUBLIC_KEY_TYPE_NONE
    static_oob_type: int = STATIC_OOB_TYPE_NONE
    output_oob_size: int = 0
    output_oob_action: int = 0
    input_oob_size: int = 0
    input_oob_action: int = 0

    def encode(self) -> bytearray:
        """Encode capabilities to provisioning PDU format."""
        return bytearray(
            struct.pack(
                "<BBHBBBBBB",
                ProvisioningPDUType.CAPABILITIES,
                self.num_elements,
                self.algorithms,
                self.public_key_type,
                self.static_oob_type,
                self.output_oob_size,
                self.output_oob_action,
                self.input_oob_size,
                self.input_oob_action,
            )
        )


class SecureNetworkBeacon(msgspec.Struct, frozen=True, kw_only=True):
    """Mesh Secure Network Beacon per Bluetooth Mesh Profile 3.10.3.

    This beacon is broadcast by provisioned nodes to announce
    network presence and IV index.

    Attributes:
        network_id: 8-byte Network ID derived from network key
        iv_index: Current IV Index
        key_refresh_flag: Key Refresh Flag
        iv_update_flag: IV Update Flag
        authentication_value: 8-byte authentication value

    """

    network_id: bytes  # 8 bytes, derived from network key
    iv_index: int = 0
    key_refresh_flag: bool = False
    iv_update_flag: bool = False
    authentication_value: bytes = b""  # 8 bytes when parsed

    def encode(self) -> bytearray:
        """Encode to beacon format.

        Returns:
            Encoded beacon bytes

        Raises:
            ValueError: If network_id is not 8 bytes

        """
        if len(self.network_id) != NETWORK_ID_LENGTH:
            msg = f"network_id must be {NETWORK_ID_LENGTH} bytes, got {len(self.network_id)}"
            raise ValueError(msg)

        flags = SecureNetworkBeaconFlags.NONE
        if self.key_refresh_flag:
            flags |= SecureNetworkBeaconFlags.KEY_REFRESH
        if self.iv_update_flag:
            flags |= SecureNetworkBeaconFlags.IV_UPDATE

        # Use provided auth value or generate random for encoding
        auth_value = (
            self.authentication_value
            if len(self.authentication_value) == AUTHENTICATION_VALUE_LENGTH
            else secrets.token_bytes(AUTHENTICATION_VALUE_LENGTH)
        )

        return bytearray(
            struct.pack(
                "<BB8sI8s",
                MeshBeaconType.SECURE_NETWORK,
                flags,
                self.network_id,
                self.iv_index,
                auth_value,
            )
        )

    @classmethod
    def decode(cls, data: bytes | bytearray) -> SecureNetworkBeacon:
        """Decode from beacon bytes.

        Args:
            data: Raw beacon bytes (without beacon type byte)

        Returns:
            Parsed SecureNetworkBeacon

        Raises:
            ValueError: If data is too short

        """
        min_length = 1 + NETWORK_ID_LENGTH + 4 + AUTHENTICATION_VALUE_LENGTH  # flags + netid + iv + auth
        if len(data) < min_length:
            msg = f"Expected at least {min_length} bytes, got {len(data)}"
            raise ValueError(msg)

        flags = SecureNetworkBeaconFlags(data[0])
        network_id = bytes(data[1:9])
        iv_index = struct.unpack("<I", data[9:13])[0]
        auth_value = bytes(data[13:21])

        return cls(
            network_id=network_id,
            iv_index=iv_index,
            key_refresh_flag=bool(flags & SecureNetworkBeaconFlags.KEY_REFRESH),
            iv_update_flag=bool(flags & SecureNetworkBeaconFlags.IV_UPDATE),
            authentication_value=auth_value,
        )


class UnprovisionedDeviceBeacon(msgspec.Struct, frozen=True, kw_only=True):
    """Mesh Unprovisioned Device Beacon per Bluetooth Mesh Profile 3.10.2.

    This beacon is broadcast by unprovisioned devices to announce
    their presence and provisioning capabilities.

    Attributes:
        device_uuid: 16-byte device UUID
        oob_info: OOB information flags
        uri_hash: Optional 4-byte URI hash

    """

    device_uuid: bytes  # 16 bytes
    oob_info: int = 0x0000
    uri_hash: bytes | None = None  # 4 bytes, optional

    def encode(self) -> bytearray:
        """Encode to beacon format.

        Returns:
            Encoded beacon bytes

        Raises:
            ValueError: If device_uuid is not 16 bytes

        """
        if len(self.device_uuid) != DEVICE_UUID_LENGTH:
            msg = f"device_uuid must be {DEVICE_UUID_LENGTH} bytes, got {len(self.device_uuid)}"
            raise ValueError(msg)

        result = bytearray(
            struct.pack(
                "<B16sH",
                MeshBeaconType.UNPROVISIONED_DEVICE,
                self.device_uuid,
                self.oob_info,
            )
        )

        if self.uri_hash is not None:
            result.extend(self.uri_hash[:4])

        return result

    @classmethod
    def decode(cls, data: bytes | bytearray) -> UnprovisionedDeviceBeacon:
        """Decode from beacon bytes.

        Args:
            data: Raw beacon bytes (without beacon type byte)

        Returns:
            Parsed UnprovisionedDeviceBeacon

        Raises:
            ValueError: If data is too short

        """
        if len(data) < UNPROVISIONED_BEACON_MIN_LENGTH:
            msg = f"Expected at least {UNPROVISIONED_BEACON_MIN_LENGTH} bytes, got {len(data)}"
            raise ValueError(msg)

        device_uuid = bytes(data[0:DEVICE_UUID_LENGTH])
        oob_info = struct.unpack("<H", data[DEVICE_UUID_LENGTH:UNPROVISIONED_BEACON_MIN_LENGTH])[0]
        uri_hash = (
            bytes(data[UNPROVISIONED_BEACON_MIN_LENGTH:UNPROVISIONED_BEACON_WITH_HASH_LENGTH])
            if len(data) >= UNPROVISIONED_BEACON_WITH_HASH_LENGTH
            else None
        )

        return cls(
            device_uuid=device_uuid,
            oob_info=oob_info,
            uri_hash=uri_hash,
        )


# MeshMessage constants
MESH_MESSAGE_MIN_LENGTH = 9  # ivi/nid (1) + ctl/ttl (1) + seq (3) + src (2) + dst (2)
MESH_MESSAGE_IVI_MASK = 0x80
MESH_MESSAGE_NID_MASK = 0x7F
MESH_MESSAGE_CTL_MASK = 0x80
MESH_MESSAGE_TTL_MASK = 0x7F


class MeshMessage(msgspec.Struct, frozen=True, kw_only=True):
    """Mesh Network PDU message per Bluetooth Mesh Profile 3.4.

    Attributes:
        ivi: IV Index least significant bit
        nid: Network ID (7 bits)
        ctl: Control message flag
        ttl: Time To Live
        seq: Sequence number (24 bits)
        src: Source address
        dst: Destination address
        transport_pdu: Encrypted transport PDU
        net_mic: Network MIC (32 or 64 bits)

    """

    ivi: int = 0
    nid: int = 0
    ctl: bool = False
    ttl: int = 0
    seq: int = 0
    src: int = 0
    dst: int = 0
    transport_pdu: bytes = b""
    net_mic: bytes = b""

    @classmethod
    def decode(cls, data: bytes | bytearray) -> MeshMessage:
        """Decode from Network PDU bytes.

        Args:
            data: Raw Network PDU bytes

        Returns:
            Parsed MeshMessage

        Raises:
            ValueError: If data is too short

        """
        if len(data) < MESH_MESSAGE_MIN_LENGTH:
            msg = f"Expected at least {MESH_MESSAGE_MIN_LENGTH} bytes, got {len(data)}"
            raise ValueError(msg)

        # First byte: IVI (1 bit) + NID (7 bits)
        ivi = (data[0] & MESH_MESSAGE_IVI_MASK) >> 7
        nid = data[0] & MESH_MESSAGE_NID_MASK

        # Second byte: CTL (1 bit) + TTL (7 bits)
        ctl = bool(data[1] & MESH_MESSAGE_CTL_MASK)
        ttl = data[1] & MESH_MESSAGE_TTL_MASK

        # SEQ: 3 bytes big-endian
        seq = (data[2] << 16) | (data[3] << 8) | data[4]

        # SRC: 2 bytes big-endian
        src = (data[5] << 8) | data[6]

        # DST: 2 bytes big-endian
        dst = (data[7] << 8) | data[8]

        # Rest is transport PDU + NetMIC
        # NetMIC length depends on message type per Bluetooth Mesh Profile 3.4.3
        mic_length = CONTROL_MESSAGE_MIC_LENGTH if ctl else ACCESS_MESSAGE_MIC_LENGTH
        transport_pdu = bytes(data[9:-mic_length]) if len(data) > MESH_MESSAGE_MIN_LENGTH + mic_length else b""
        net_mic = bytes(data[-mic_length:]) if len(data) >= MESH_MESSAGE_MIN_LENGTH + mic_length else b""

        return cls(
            ivi=ivi,
            nid=nid,
            ctl=ctl,
            ttl=ttl,
            seq=seq,
            src=src,
            dst=dst,
            transport_pdu=transport_pdu,
            net_mic=net_mic,
        )


# ProvisioningBearerData constants
PB_ADV_MIN_LENGTH = 6  # link_id (4) + transaction (1) + pdu_type (1)


class ProvisioningBearerData(msgspec.Struct, frozen=True, kw_only=True):
    """Provisioning Bearer (PB-ADV) data per Bluetooth Mesh Profile 5.3.

    Attributes:
        link_id: Link identifier (32 bits)
        transaction_number: Transaction number
        pdu_type: Provisioning PDU type
        pdu_data: Raw PDU payload

    """

    link_id: int = 0
    transaction_number: int = 0
    pdu_type: ProvisioningPDUType = ProvisioningPDUType.INVITE
    pdu_data: bytes = b""

    @classmethod
    def decode(cls, data: bytes | bytearray) -> ProvisioningBearerData:
        """Decode from PB-ADV bytes.

        Args:
            data: Raw PB-ADV bytes

        Returns:
            Parsed ProvisioningBearerData

        Raises:
            ValueError: If data is too short

        """
        if len(data) < PB_ADV_MIN_LENGTH:
            msg = f"Expected at least {PB_ADV_MIN_LENGTH} bytes, got {len(data)}"
            raise ValueError(msg)

        # Link ID: 4 bytes big-endian
        link_id = struct.unpack(">I", data[0:4])[0]

        # Transaction number: 1 byte
        transaction_number = data[4]

        # PDU type: 1 byte
        try:
            pdu_type = ProvisioningPDUType(data[5])
        except ValueError:
            pdu_type = ProvisioningPDUType.INVITE  # Default for unknown types

        # Rest is PDU data
        pdu_data = bytes(data[6:]) if len(data) > PB_ADV_MIN_LENGTH else b""

        return cls(
            link_id=link_id,
            transaction_number=transaction_number,
            pdu_type=pdu_type,
            pdu_data=pdu_data,
        )


__all__ = [
    # Constants
    "ACCESS_MESSAGE_MIC_LENGTH",
    "ALGORITHM_FIPS_P256",
    "AUTHENTICATION_VALUE_LENGTH",
    "CONTROL_MESSAGE_MIC_LENGTH",
    "DEVICE_UUID_LENGTH",
    "MESH_MESSAGE_CTL_MASK",
    "MESH_MESSAGE_IVI_MASK",
    "MESH_MESSAGE_MIN_LENGTH",
    "MESH_MESSAGE_NID_MASK",
    "MESH_MESSAGE_TTL_MASK",
    "NETWORK_ID_LENGTH",
    "NETWORK_KEY_LENGTH",
    "OOB_INFO_LENGTH",
    "PB_ADV_MIN_LENGTH",
    "PUBLIC_KEY_TYPE_NONE",
    "STATIC_OOB_TYPE_NONE",
    "UNPROVISIONED_BEACON_MIN_LENGTH",
    "UNPROVISIONED_BEACON_WITH_HASH_LENGTH",
    "URI_HASH_LENGTH",
    # Enums
    "MeshBeaconType",
    "ProvisioningPDUType",
    "SecureNetworkBeaconFlags",
    # Structs
    "MeshCapabilities",
    "MeshMessage",
    "ProvisioningBearerData",
    "SecureNetworkBeacon",
    "UnprovisionedDeviceBeacon",
]

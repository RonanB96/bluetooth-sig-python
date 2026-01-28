"""Typed state classes for payload interpretation.

State management is the caller's responsibility (connection manager, device tracker).
The interpreter receives state, uses it, and returns updated values.
The caller decides when/how to persist.

Based on Bluetooth SIG Core Specification Supplement for advertising data patterns
and real-world implementations (BTHome, Xiaomi MiBeacon, RuuviTag).
"""

from __future__ import annotations

import msgspec


class EncryptionState(msgspec.Struct, kw_only=True, frozen=False):
    """Encryption-related state for a device.

    Caller is responsible for persisting and updating this state.
    Interpreter reads current values and returns new values.

    Attributes:
        bindkey: 16-byte AES-CCM key for decryption (pre-shared).
        bindkey_verified: Whether bindkey has successfully decrypted a payload.
        encryption_counter: Monotonically increasing counter for replay protection.
            BTHome/Xiaomi use 4-byte counter in advertisement payload.
        decryption_failed: Whether last decryption attempt failed.

    """

    bindkey: bytes | None = None
    bindkey_verified: bool = False
    encryption_counter: int = 0
    decryption_failed: bool = False


class PacketState(msgspec.Struct, kw_only=True, frozen=False):
    """Packet tracking state for duplicate/replay detection.

    Caller is responsible for persisting and updating this state.

    Attributes:
        packet_id: Last seen packet ID (for BTHome v2 duplicate filtering).
        last_seen_timestamp: Timestamp of last valid advertisement (Unix epoch seconds).
        last_service_data_hash: Hash of last service data payload (for same-payload detection).

    """

    packet_id: int | None = None
    last_seen_timestamp: float = 0.0
    last_service_data_hash: int | None = None


class DeviceAdvertisingState(msgspec.Struct, kw_only=True, frozen=False):
    """Complete advertising state for a device.

    Managed by caller (connection manager, device tracker).
    Passed to interpreter, interpreter returns InterpretationResult with any updates.

    Attributes:
        address: Device MAC address or platform identifier.
        encryption: Encryption-related state.
        packets: Packet tracking state.
        device_type: Detected device type from payload (e.g., "BTHome sensor").
        protocol_version: Detected protocol version (e.g., "v2", "MiBeacon v5").
        is_sleepy_device: Whether device uses irregular advertising intervals.

    """

    address: str = ""
    encryption: EncryptionState = msgspec.field(default_factory=EncryptionState)
    packets: PacketState = msgspec.field(default_factory=PacketState)
    device_type: str | None = None
    protocol_version: str | None = None
    is_sleepy_device: bool = False

"""Result types for payload interpretation.

Provides strongly-typed result objects that interpreters return after
processing advertising payloads. Results include parsed data, status,
and any state updates that should be applied by the caller.
"""

from __future__ import annotations

from enum import Enum
from typing import Generic, TypeVar

import msgspec

from bluetooth_sig.advertising.state import DeviceAdvertisingState

T = TypeVar("T")


class InterpretationStatus(Enum):
    """Status of payload interpretation.

    Attributes:
        SUCCESS: Payload successfully parsed.
        ENCRYPTION_REQUIRED: Payload is encrypted but no bindkey available.
        DECRYPTION_FAILED: Decryption failed (wrong bindkey or corrupted data).
        REPLAY_DETECTED: Encryption counter not increasing (replay attack).
        DUPLICATE_PACKET: Same packet_id as previous (duplicate advertisement).
        PARSE_ERROR: Payload is malformed or unsupported format.
        UNSUPPORTED_VERSION: Unknown protocol version in payload.

    """

    SUCCESS = "success"
    ENCRYPTION_REQUIRED = "encryption_required"
    DECRYPTION_FAILED = "decryption_failed"
    REPLAY_DETECTED = "replay_detected"
    DUPLICATE_PACKET = "duplicate_packet"
    PARSE_ERROR = "parse_error"
    UNSUPPORTED_VERSION = "unsupported_version"


class InterpretationResult(msgspec.Struct, Generic[T], kw_only=True):
    """Result from payload interpretation.

    Contains parsed data, updated state, and status information.
    Caller decides how to handle each status and whether to update state.

    Type Parameters:
        T: The type of parsed data (e.g., SensorReading, BTHomeData).

    Attributes:
        status: Interpretation status code.
        data: Parsed data (None if status != SUCCESS).
        updated_encryption_counter: New counter value if changed.
        updated_packet_id: New packet ID if changed.
        updated_bindkey_verified: New verification status if changed.
        updated_device_type: Detected device type if changed.
        updated_protocol_version: Detected protocol version if changed.
        updated_is_sleepy_device: Whether device is sleepy if detected.
        error_message: Human-readable error description.
        warnings: Non-fatal issues encountered during parsing.

    Example:
        result = interpreter.interpret(service_data, manufacturer_data, ...)
        if result.status == InterpretationStatus.SUCCESS:
            process_data(result.data)
            result.apply_to_state(device_state)
        elif result.status == InterpretationStatus.ENCRYPTION_REQUIRED:
            prompt_for_bindkey()

    """

    status: InterpretationStatus = InterpretationStatus.SUCCESS
    data: T | None = None

    # State updates (only fields that changed are set; None means no change)
    updated_encryption_counter: int | None = None
    updated_packet_id: int | None = None
    updated_bindkey_verified: bool | None = None
    updated_device_type: str | None = None
    updated_protocol_version: str | None = None
    updated_is_sleepy_device: bool | None = None

    # Error and warning information
    error_message: str | None = None
    warnings: list[str] = msgspec.field(default_factory=list)

    def apply_to_state(self, state: DeviceAdvertisingState) -> DeviceAdvertisingState:
        """Apply updates to state (convenience method).

        Modifies the state in-place with any updated values from this result.
        Only fields that have updated values (not None) are applied.

        Args:
            state: The advertising state to update.

        Returns:
            The same state object (for chaining).

        """
        if self.updated_encryption_counter is not None:
            state.encryption.encryption_counter = self.updated_encryption_counter
        if self.updated_packet_id is not None:
            state.packets.packet_id = self.updated_packet_id
        if self.updated_bindkey_verified is not None:
            state.encryption.bindkey_verified = self.updated_bindkey_verified
        if self.updated_device_type is not None:
            state.device_type = self.updated_device_type
        if self.updated_protocol_version is not None:
            state.protocol_version = self.updated_protocol_version
        if self.updated_is_sleepy_device is not None:
            state.is_sleepy_device = self.updated_is_sleepy_device
        return state

    @property
    def is_success(self) -> bool:
        """Check if interpretation was successful."""
        return self.status == InterpretationStatus.SUCCESS

    @property
    def is_error(self) -> bool:
        """Check if interpretation failed with an error."""
        return self.status not in (
            InterpretationStatus.SUCCESS,
            InterpretationStatus.DUPLICATE_PACKET,
        )

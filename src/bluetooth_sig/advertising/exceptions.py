"""Advertising exceptions for the Bluetooth SIG library.

Provides exception types for advertising-related errors, following the same
patterns as GATT exceptions for API consistency.

Exception Hierarchy:
    AdvertisingError (base)
    ├── AdvertisingParseError - General parse failures
    │   ├── EncryptionRequiredError - Payload encrypted, no bindkey
    │   ├── DecryptionFailedError - Decryption failed
    │   └── UnsupportedVersionError - Unknown protocol version
    ├── ReplayDetectedError - Counter not increasing
    └── DuplicatePacketError - Same packet_id as previous
"""

from __future__ import annotations

from bluetooth_sig.gatt.exceptions import BluetoothSIGError


class AdvertisingError(BluetoothSIGError):
    """Base exception for all advertising-related errors."""


class AdvertisingParseError(AdvertisingError):
    """Exception raised when advertising payload parsing fails.

    Attributes:
        message: Human-readable error message.
        raw_data: The raw advertising data that failed to parse.
        interpreter_name: Name of the interpreter that raised the error.
        field: Specific field that caused the error (if applicable).

    """

    def __init__(
        self,
        message: str,
        raw_data: bytes = b"",
        interpreter_name: str = "",
        field: str | None = None,
    ) -> None:
        """Initialise AdvertisingParseError.

        Args:
            message: Human-readable error message.
            raw_data: The raw advertising data that failed to parse.
            interpreter_name: Name of the interpreter that raised the error.
            field: Specific field that caused the error (if applicable).

        """
        self.raw_data = raw_data
        self.interpreter_name = interpreter_name
        self.field = field

        # Build detailed message
        parts = [message]
        if interpreter_name:
            parts.insert(0, f"[{interpreter_name}]")
        if field:
            parts.append(f"(field: {field})")
        if raw_data:
            max_hex_bytes = 32
            hex_data = raw_data.hex() if len(raw_data) <= max_hex_bytes else f"{raw_data[:max_hex_bytes].hex()}..."
            parts.append(f"[data: {hex_data}]")

        super().__init__(" ".join(parts))


class EncryptionRequiredError(AdvertisingParseError):
    """Exception raised when payload is encrypted but no bindkey is available.

    This exception indicates the payload contains encrypted data that
    requires a bindkey for decryption. The caller should:
    1. Prompt the user to provide a bindkey
    2. Store the bindkey in DeviceAdvertisingState.encryption.bindkey
    3. Retry interpretation

    Attributes:
        mac_address: Device MAC address needing a bindkey.

    """

    def __init__(
        self,
        mac_address: str,
        raw_data: bytes = b"",
        interpreter_name: str = "",
    ) -> None:
        """Initialise EncryptionRequiredError.

        Args:
            mac_address: Device MAC address needing a bindkey.
            raw_data: The raw encrypted advertising data.
            interpreter_name: Name of the interpreter that raised the error.

        """
        self.mac_address = mac_address
        message = f"Encryption required for device {mac_address}"
        super().__init__(
            message=message,
            raw_data=raw_data,
            interpreter_name=interpreter_name,
        )


class DecryptionFailedError(AdvertisingParseError):
    """Exception raised when decryption fails.

    This typically indicates:
    - Wrong bindkey
    - Corrupted data
    - Incorrect nonce construction

    Attributes:
        mac_address: Device MAC address.
        reason: Specific reason for decryption failure.

    """

    def __init__(
        self,
        mac_address: str,
        reason: str = "decryption failed",
        raw_data: bytes = b"",
        interpreter_name: str = "",
    ) -> None:
        """Initialise DecryptionFailedError.

        Args:
            mac_address: Device MAC address.
            reason: Specific reason for decryption failure.
            raw_data: The raw encrypted advertising data.
            interpreter_name: Name of the interpreter that raised the error.

        """
        self.mac_address = mac_address
        self.reason = reason
        message = f"Decryption failed for device {mac_address}: {reason}"
        super().__init__(
            message=message,
            raw_data=raw_data,
            interpreter_name=interpreter_name,
        )


class UnsupportedVersionError(AdvertisingParseError):
    """Exception raised when protocol version is not supported.

    Attributes:
        version: The unsupported version identifier.
        supported_versions: List of supported version identifiers.

    """

    def __init__(
        self,
        version: str | int,
        supported_versions: list[str | int] | None = None,
        raw_data: bytes = b"",
        interpreter_name: str = "",
    ) -> None:
        """Initialise UnsupportedVersionError.

        Args:
            version: The unsupported version identifier.
            supported_versions: List of supported version identifiers.
            raw_data: The raw advertising data.
            interpreter_name: Name of the interpreter that raised the error.

        """
        self.version = version
        self.supported_versions = supported_versions or []
        supported_str = ", ".join(str(v) for v in self.supported_versions) if self.supported_versions else "unknown"
        message = f"Unsupported protocol version {version} (supported: {supported_str})"
        super().__init__(
            message=message,
            raw_data=raw_data,
            interpreter_name=interpreter_name,
        )


class ReplayDetectedError(AdvertisingError):
    """Exception raised when a replay attack is detected.

    This occurs when the encryption counter is not increasing,
    indicating a potential replay attack.

    Note: Per Bluetooth Core Specification, replay protection is typically
    handled at Controller/Link Layer level. This exception is provided
    for vendor protocols that implement their own replay detection.

    Attributes:
        mac_address: Device MAC address.
        received_counter: Counter value received in the packet.
        expected_counter: Minimum expected counter value.

    """

    def __init__(
        self,
        mac_address: str,
        received_counter: int,
        expected_counter: int,
    ) -> None:
        """Initialise ReplayDetectedError.

        Args:
            mac_address: Device MAC address.
            received_counter: Counter value received in the packet.
            expected_counter: Minimum expected counter value.

        """
        self.mac_address = mac_address
        self.received_counter = received_counter
        self.expected_counter = expected_counter
        message = (
            f"Replay detected for device {mac_address}: "
            f"received counter {received_counter}, expected >= {expected_counter}"
        )
        super().__init__(message)


class DuplicatePacketError(AdvertisingError):
    """Exception raised when a duplicate packet is detected.

    This occurs when the same packet_id is received twice, indicating
    the same advertisement was received multiple times. This is typically
    not an error but may be useful for deduplication.

    Attributes:
        mac_address: Device MAC address.
        packet_id: The duplicate packet ID.

    """

    def __init__(
        self,
        mac_address: str,
        packet_id: int,
    ) -> None:
        """Initialise DuplicatePacketError.

        Args:
            mac_address: Device MAC address.
            packet_id: The duplicate packet ID.

        """
        self.mac_address = mac_address
        self.packet_id = packet_id
        message = f"Duplicate packet {packet_id} from device {mac_address}"
        super().__init__(message)

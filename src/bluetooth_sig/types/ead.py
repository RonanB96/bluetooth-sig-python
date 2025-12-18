"""Type definitions for BLE Encrypted Advertising Data (EAD).

This module defines data structures for Encrypted Advertising Data
per Bluetooth Core Spec Supplement Section 1.23.

EAD Format::

    [Randomizer (5 bytes)][Encrypted Payload (variable)][MIC (4 bytes)]

The Randomizer provides uniqueness for each advertisement. The MIC
(Message Integrity Check) is a 4-byte authentication tag produced by
AES-CCM encryption.

Cryptographic parameters per Bluetooth Core Spec Supplement:
    - Session Key: 16-byte AES-128 key
    - IV: 8-byte initialization vector
    - Nonce: 13 bytes (Randomizer + Device Address + Padding)
    - MIC: 4-byte authentication tag
"""

from __future__ import annotations

from enum import Enum, auto

import msgspec
from typing_extensions import Self


class EADError(Enum):
    """Error types for EAD decryption failures.

    Attributes:
        INVALID_KEY: Decryption failed due to incorrect key (MIC mismatch)
        REPLAY_DETECTED: Advertisement counter indicates replay attack
        CORRUPTED_DATA: Data format invalid or too short
        NO_KEY_AVAILABLE: No encryption key configured for this device
        INSUFFICIENT_DATA: EAD payload too short to contain required fields
    """

    INVALID_KEY = auto()
    REPLAY_DETECTED = auto()
    CORRUPTED_DATA = auto()
    NO_KEY_AVAILABLE = auto()
    INSUFFICIENT_DATA = auto()


# EAD format constants per Bluetooth Core Spec Supplement Section 1.23
EAD_RANDOMIZER_SIZE: int = 5  # 5-byte randomizer for nonce
EAD_MIC_SIZE: int = 4  # 4-byte Message Integrity Check (tag)
EAD_MIN_SIZE: int = EAD_RANDOMIZER_SIZE + EAD_MIC_SIZE  # 9 bytes minimum

# EAD cryptographic constants per Bluetooth Core Spec Supplement
EAD_SESSION_KEY_SIZE: int = 16  # 128-bit AES session key
EAD_IV_SIZE: int = 8  # 8-byte initialization vector
EAD_NONCE_SIZE: int = 13  # Randomizer(5) + Address(6) + Padding(2)
EAD_ADDRESS_SIZE: int = 6  # BLE device address size


class EncryptedAdvertisingData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed BLE Encrypted Advertising Data structure.

    Represents the three components of an EAD advertisement as defined
    in Bluetooth Core Spec Supplement Section 1.23.

    Attributes:
        randomizer: 5-byte randomizer for nonce construction
        encrypted_payload: Variable-length encrypted data
        mic: 4-byte Message Integrity Check (authentication tag)

    Example:
        >>> raw = bytes.fromhex("0102030405aabbccdd11223344")
        >>> ead = EncryptedAdvertisingData.from_bytes(raw)
        >>> print(ead.randomizer.hex())
        '0102030405'
        >>> print(ead.mic.hex())
        '11223344'
    """

    randomizer: bytes
    encrypted_payload: bytes
    mic: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        """Parse raw EAD bytes into structured components.

        Args:
            data: Raw EAD advertisement data (minimum 9 bytes:
                  5-byte randomizer + at least 0-byte payload + 4-byte MIC)

        Returns:
            Parsed EncryptedAdvertisingData structure

        Raises:
            ValueError: If data is shorter than minimum EAD size (9 bytes)

        Example:
            >>> raw = bytes.fromhex("0102030405aabbccdd11223344")
            >>> ead = EncryptedAdvertisingData.from_bytes(raw)
            >>> len(ead.encrypted_payload)
            4
        """
        if len(data) < EAD_MIN_SIZE:
            msg = f"EAD data must be at least {EAD_MIN_SIZE} bytes (randomizer + MIC), got {len(data)} bytes"
            raise ValueError(msg)

        return cls(
            randomizer=data[:EAD_RANDOMIZER_SIZE],
            encrypted_payload=data[EAD_RANDOMIZER_SIZE:-EAD_MIC_SIZE],
            mic=data[-EAD_MIC_SIZE:],
        )


class EADDecryptResult(msgspec.Struct, frozen=True, kw_only=True):
    """Result of an EAD decryption attempt.

    Provides structured feedback on decryption success or failure,
    including specific error types for appropriate handling.

    Attributes:
        success: Whether decryption succeeded
        plaintext: Decrypted data if successful, None otherwise
        error: Human-readable error message if failed
        error_type: Structured error type for programmatic handling

    Example - successful decryption:
        >>> result = EADDecryptResult(success=True, plaintext=b"sensor_data")
        >>> if result.success:
        ...     process_data(result.plaintext)

    Example - failed decryption:
        >>> result = EADDecryptResult(
        ...     success=False,
        ...     plaintext=None,
        ...     error="MIC verification failed",
        ...     error_type=EADError.INVALID_KEY,
        ... )
        >>> if result.error_type == EADError.INVALID_KEY:
        ...     request_new_key()
    """

    success: bool
    plaintext: bytes | None = None
    error: str | None = None
    error_type: EADError | None = None


class EADKeyMaterial(msgspec.Struct, frozen=True, kw_only=True):
    """Key material for BLE Encrypted Advertising Data (EAD).

    Per Bluetooth Core Spec Supplement Section 1.23, EAD encryption
    requires a 16-byte session key and 8-byte initialization vector.

    Validation is performed at construction time - invalid key sizes
    will raise ValueError.

    Attributes:
        session_key: 16-byte AES-128 session key for encryption/decryption
        iv: 8-byte initialization vector (combined with randomizer for nonce)

    Example:
        >>> key_material = EADKeyMaterial(
        ...     session_key=bytes.fromhex("0123456789abcdef0123456789abcdef"),
        ...     iv=bytes.fromhex("0102030405060708"),
        ... )

    Raises:
        ValueError: If session_key is not 16 bytes or iv is not 8 bytes
    """

    session_key: bytes
    iv: bytes

    def __post_init__(self) -> None:
        """Validate key material sizes per Bluetooth Core Spec."""
        if len(self.session_key) != EAD_SESSION_KEY_SIZE:
            msg = f"EAD session key must be {EAD_SESSION_KEY_SIZE} bytes, got {len(self.session_key)}"
            raise ValueError(msg)
        if len(self.iv) != EAD_IV_SIZE:
            msg = f"EAD IV must be {EAD_IV_SIZE} bytes, got {len(self.iv)}"
            raise ValueError(msg)

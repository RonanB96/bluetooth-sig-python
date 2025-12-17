"""Pure decryption functions for BLE Encrypted Advertising Data (EAD).

This module provides framework-agnostic decryption functions for EAD
per Bluetooth Core Spec Supplement Section 1.23.

The decryption uses AES-CCM with:
- 128-bit (16-byte) session key
- 13-byte nonce (5-byte randomizer + 6-byte device address + 2-byte padding)
- 4-byte MIC (authentication tag)

Requires the 'cryptography' package: pip install bluetooth-sig[ead]
"""

from __future__ import annotations

import logging

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESCCM

from bluetooth_sig.advertising.encryption import EADKeyProvider
from bluetooth_sig.types.ead import (
    EAD_MIN_SIZE,
    EAD_RANDOMIZER_SIZE,
    EADDecryptResult,
    EADError,
    EncryptedAdvertisingData,
)

logger = logging.getLogger(__name__)

# EAD cryptographic constants per Bluetooth Core Spec Supplement
EAD_KEY_SIZE: int = 16  # 128-bit AES key
EAD_NONCE_SIZE: int = 13  # Randomizer(5) + Address(6) + Padding(2)
EAD_MIC_SIZE: int = 4  # 4-byte authentication tag
EAD_ADDRESS_SIZE: int = 6  # BLE device address size


def _get_aesccm_cipher(session_key: bytes) -> AESCCM:
    """Create an AESCCM cipher instance.

    Args:
        session_key: 16-byte AES-128 session key

    Returns:
        AESCCM cipher instance configured for EAD (4-byte tag)

    Raises:
        ValueError: If session_key is not 16 bytes
    """
    if len(session_key) != EAD_KEY_SIZE:
        msg = f"Session key must be {EAD_KEY_SIZE} bytes, got {len(session_key)}"
        raise ValueError(msg)

    return AESCCM(session_key, tag_length=EAD_MIC_SIZE)


def build_ead_nonce(
    randomizer: bytes,
    device_address: bytes,
) -> bytes:
    """Build the 13-byte nonce for EAD decryption.

    The nonce is constructed as:
        Randomizer[5] + DeviceAddress[6] + Padding[2]

    Args:
        randomizer: 5-byte randomizer from EAD advertisement
        device_address: 6-byte BLE device address (little-endian)

    Returns:
        13-byte nonce for AES-CCM decryption

    Raises:
        ValueError: If randomizer is not 5 bytes or address is not 6 bytes

    Example:
        >>> randomizer = bytes.fromhex("0102030405")
        >>> address = bytes.fromhex("aabbccddeeff")
        >>> nonce = build_ead_nonce(randomizer, address)
        >>> len(nonce)
        13
    """
    if len(randomizer) != EAD_RANDOMIZER_SIZE:
        msg = f"Randomizer must be {EAD_RANDOMIZER_SIZE} bytes, got {len(randomizer)}"
        raise ValueError(msg)

    if len(device_address) != EAD_ADDRESS_SIZE:
        msg = f"Device address must be {EAD_ADDRESS_SIZE} bytes, got {len(device_address)}"
        raise ValueError(msg)

    # Nonce: Randomizer(5) + Address(6) + Padding(2)
    padding = b"\x00\x00"
    return randomizer + device_address + padding


def mac_address_to_bytes(mac_address: str) -> bytes:
    """Convert a MAC address string to 6 bytes.

    Args:
        mac_address: MAC address string (e.g., "AA:BB:CC:DD:EE:FF")

    Returns:
        6-byte representation of the MAC address

    Raises:
        ValueError: If MAC address format is invalid

    Example:
        >>> mac_address_to_bytes("AA:BB:CC:DD:EE:FF").hex()
        'aabbccddeeff'
    """
    # Remove colons/dashes and convert to bytes
    cleaned = mac_address.replace(":", "").replace("-", "")
    if len(cleaned) != 12:
        msg = f"Invalid MAC address format: {mac_address}"
        raise ValueError(msg)

    try:
        return bytes.fromhex(cleaned)
    except ValueError as err:
        msg = f"Invalid MAC address hex characters: {mac_address}"
        raise ValueError(msg) from err


def decrypt_ead(  # pylint: disable=too-many-return-statements
    encrypted_data: EncryptedAdvertisingData,
    session_key: bytes,
    device_address: bytes,
    associated_data: bytes | None = None,
) -> EADDecryptResult:
    """Decrypt BLE Encrypted Advertising Data.

    Performs AES-CCM decryption per Bluetooth Core Spec Supplement Section 1.23.
    This function never raises exceptions on decryption failure; instead,
    it returns a result with appropriate error information.

    Args:
        encrypted_data: Parsed EAD structure containing randomizer,
                       encrypted payload, and MIC
        session_key: 16-byte AES-128 session key
        device_address: 6-byte BLE device address (little-endian bytes)
        associated_data: Optional additional authenticated data (AAD).
                        Must match the AAD used during encryption.

    Returns:
        EADDecryptResult with success status and plaintext or error details

    Example:
        >>> ead = EncryptedAdvertisingData.from_bytes(raw_advertisement)
        >>> result = decrypt_ead(ead, session_key, device_address)
        >>> if result.success:
        ...     process_sensor_data(result.plaintext)
        ... elif result.error_type == EADError.INVALID_KEY:
        ...     logger.warning("Incorrect encryption key for device")
    """
    # Validate session key
    if len(session_key) != EAD_KEY_SIZE:
        return EADDecryptResult(
            success=False,
            error=f"Session key must be {EAD_KEY_SIZE} bytes, got {len(session_key)}",
            error_type=EADError.CORRUPTED_DATA,
        )

    # Validate device address
    if len(device_address) != EAD_ADDRESS_SIZE:
        return EADDecryptResult(
            success=False,
            error=f"Device address must be {EAD_ADDRESS_SIZE} bytes, got {len(device_address)}",
            error_type=EADError.CORRUPTED_DATA,
        )

    try:
        # Build nonce and cipher
        nonce = build_ead_nonce(encrypted_data.randomizer, device_address)
        cipher = _get_aesccm_cipher(session_key)

        # AES-CCM expects ciphertext with MIC appended
        ciphertext_with_mic = encrypted_data.encrypted_payload + encrypted_data.mic

        # Decrypt and verify
        plaintext = cipher.decrypt(nonce, ciphertext_with_mic, associated_data)

        return EADDecryptResult(success=True, plaintext=plaintext)

    except InvalidTag:
        # MIC verification failed - wrong key or corrupted data
        logger.debug("EAD decryption failed: MIC verification failed")
        return EADDecryptResult(
            success=False,
            error="MIC verification failed - incorrect key or corrupted data",
            error_type=EADError.INVALID_KEY,
        )
    except ValueError as err:
        # Invalid parameters
        logger.debug("EAD decryption failed: %s", err)
        return EADDecryptResult(
            success=False,
            error=str(err),
            error_type=EADError.CORRUPTED_DATA,
        )


def decrypt_ead_from_raw(
    raw_ead_data: bytes,
    session_key: bytes,
    mac_address: str,
    associated_data: bytes | None = None,
) -> EADDecryptResult:
    """Convenience function to decrypt raw EAD bytes.

    Combines parsing and decryption in a single call for simpler usage.

    Args:
        raw_ead_data: Raw EAD advertisement bytes (AD Type 0x31 payload)
        session_key: 16-byte AES-128 session key
        mac_address: Device MAC address string (e.g., "AA:BB:CC:DD:EE:FF")
        associated_data: Optional additional authenticated data

    Returns:
        EADDecryptResult with success status and plaintext or error details

    Example:
        >>> result = decrypt_ead_from_raw(
        ...     raw_ead_data=advertisement_payload,
        ...     session_key=bytes.fromhex("0123456789abcdef0123456789abcdef"),
        ...     mac_address="AA:BB:CC:DD:EE:FF",
        ... )
        >>> if result.success:
        ...     print(f"Decrypted: {result.plaintext.hex()}")
    """
    # Parse raw bytes
    if len(raw_ead_data) < EAD_MIN_SIZE:
        return EADDecryptResult(
            success=False,
            error=(f"EAD data too short: {len(raw_ead_data)} bytes, minimum {EAD_MIN_SIZE} required"),
            error_type=EADError.INSUFFICIENT_DATA,
        )

    try:
        encrypted_data = EncryptedAdvertisingData.from_bytes(raw_ead_data)
        device_address = mac_address_to_bytes(mac_address)
    except ValueError as err:
        return EADDecryptResult(
            success=False,
            error=str(err),
            error_type=EADError.CORRUPTED_DATA,
        )

    return decrypt_ead(encrypted_data, session_key, device_address, associated_data)


class EADDecryptor:
    """Stateful EAD decryptor with cipher caching and key provider support.

    For one-off decryption, use the module-level `decrypt_ead()` function.
    For repeated decryption with the same key, this class caches the AESCCM
    cipher instance for better performance.

    This class also integrates with `EADKeyProvider` for automatic key lookup
    by MAC address.

    Use the factory methods `from_key()` or `from_provider()` to create instances.

    Attributes:
        _key_provider: Optional key provider for MAC-based key lookup
        _static_key: Static session key (used if no provider)
        _cipher_cache: Cached cipher instances keyed by session key

    Example with static key:
        >>> from bluetooth_sig.advertising import EADDecryptor
        >>>
        >>> decryptor = EADDecryptor.from_key(bytes.fromhex("0123456789abcdef0123456789abcdef"))
        >>> result = decryptor.decrypt(raw_ead_data, "AA:BB:CC:DD:EE:FF")
        >>> if result.success:
        ...     print(result.plaintext)

    Example with key provider:
        >>> from bluetooth_sig.advertising import EADDecryptor, DictKeyProvider
        >>> from bluetooth_sig.types.ead import EADKeyMaterial
        >>>
        >>> provider = DictKeyProvider()
        >>> provider.set_ead_key(
        ...     "AA:BB:CC:DD:EE:FF",
        ...     EADKeyMaterial(
        ...         session_key=bytes.fromhex("0123456789abcdef0123456789abcdef"),
        ...         iv=bytes.fromhex("0102030405060708"),
        ...     ),
        ... )
        >>> decryptor = EADDecryptor.from_provider(provider)
        >>> result = decryptor.decrypt(raw_ead_data, "AA:BB:CC:DD:EE:FF")
    """

    def __init__(
        self,
        *,
        _key_provider: EADKeyProvider | None = None,
        _static_key: bytes | None = None,
    ) -> None:
        """Private constructor. Use `from_key()` or `from_provider()` instead."""
        self._key_provider = _key_provider
        self._static_key = _static_key
        self._cipher_cache: dict[bytes, AESCCM] = {}

    @classmethod
    def from_key(cls, session_key: bytes) -> EADDecryptor:
        """Create decryptor with a static session key.

        Args:
            session_key: 16-byte AES-128 session key

        Returns:
            Configured EADDecryptor instance

        Raises:
            ValueError: If session_key is not 16 bytes

        Example:
            >>> decryptor = EADDecryptor.from_key(bytes.fromhex("0123456789abcdef0123456789abcdef"))
        """
        if len(session_key) != EAD_KEY_SIZE:
            msg = f"Session key must be {EAD_KEY_SIZE} bytes, got {len(session_key)}"
            raise ValueError(msg)
        return cls(_static_key=session_key)

    @classmethod
    def from_provider(cls, key_provider: EADKeyProvider) -> EADDecryptor:
        """Create decryptor with a key provider for MAC-based lookup.

        Args:
            key_provider: Provider that looks up keys by MAC address

        Returns:
            Configured EADDecryptor instance

        Example:
            >>> provider = DictKeyProvider()
            >>> provider.set_ead_key("AA:BB:CC:DD:EE:FF", key_material)
            >>> decryptor = EADDecryptor.from_provider(provider)
        """
        return cls(_key_provider=key_provider)

    def _get_cached_cipher(self, session_key: bytes) -> AESCCM:
        """Get or create a cached cipher for the session key.

        Args:
            session_key: 16-byte AES session key

        Returns:
            AESCCM cipher instance
        """
        if session_key not in self._cipher_cache:
            self._cipher_cache[session_key] = _get_aesccm_cipher(session_key)
        return self._cipher_cache[session_key]

    def decrypt(
        self,
        raw_ead_data: bytes,
        mac_address: str,
        associated_data: bytes | None = None,
    ) -> EADDecryptResult:
        """Decrypt EAD data using cached cipher.

        Looks up the session key from the key provider (if configured)
        or uses the static key. Caches the cipher instance for reuse.

        Args:
            raw_ead_data: Raw EAD advertisement bytes (AD Type 0x31 payload)
            mac_address: Device MAC address (e.g., "AA:BB:CC:DD:EE:FF")
            associated_data: Optional additional authenticated data (AAD)

        Returns:
            EADDecryptResult with success status and plaintext or error details
        """
        # Determine session key
        if self._key_provider is not None:
            key_material = self._key_provider.get_ead_key(mac_address)
            if key_material is None:
                return EADDecryptResult(
                    success=False,
                    error=f"No EAD key available for {mac_address}",
                    error_type=EADError.NO_KEY_AVAILABLE,
                )
            session_key = key_material.session_key
        else:
            # Static key guaranteed non-None by __init__ validation
            session_key = self._static_key  # type: ignore[assignment]

        # Parse raw data
        if len(raw_ead_data) < EAD_MIN_SIZE:
            return EADDecryptResult(
                success=False,
                error=f"EAD data too short: {len(raw_ead_data)} bytes, minimum {EAD_MIN_SIZE} required",
                error_type=EADError.INSUFFICIENT_DATA,
            )

        try:
            encrypted_data = EncryptedAdvertisingData.from_bytes(raw_ead_data)
            device_address = mac_address_to_bytes(mac_address)
        except ValueError as err:
            return EADDecryptResult(
                success=False,
                error=str(err),
                error_type=EADError.CORRUPTED_DATA,
            )

        try:
            # Get cached cipher
            cipher = self._get_cached_cipher(session_key)

            # Build nonce and decrypt
            nonce = build_ead_nonce(encrypted_data.randomizer, device_address)
            ciphertext_with_mic = encrypted_data.encrypted_payload + encrypted_data.mic
            plaintext = cipher.decrypt(nonce, ciphertext_with_mic, associated_data)

            return EADDecryptResult(success=True, plaintext=plaintext)

        except InvalidTag:
            logger.debug("EAD decryption failed: MIC verification failed")
            return EADDecryptResult(
                success=False,
                error="MIC verification failed - incorrect key or corrupted data",
                error_type=EADError.INVALID_KEY,
            )
        except ValueError as err:
            logger.debug("EAD decryption failed: %s", err)
            return EADDecryptResult(
                success=False,
                error=str(err),
                error_type=EADError.CORRUPTED_DATA,
            )

    def clear_cache(self) -> None:
        """Clear the cipher cache.

        Call this if you need to free memory or if keys have been rotated.
        """
        self._cipher_cache.clear()

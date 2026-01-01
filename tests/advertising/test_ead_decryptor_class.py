"""Tests for EADDecryptor class - runtime and functional tests.

Tests the EADDecryptor class methods including:
- Factory methods (from_key, from_provider)
- decrypt() method with various scenarios
- Cipher caching and clear_cache()
- Error handling paths
"""

from __future__ import annotations

import pytest

from bluetooth_sig.advertising.ead_decryptor import EADDecryptor
from bluetooth_sig.advertising.encryption import DictKeyProvider
from bluetooth_sig.types.ead import EADError, EADKeyMaterial

# Skip all tests in this module if cryptography is not installed
pytest.importorskip("cryptography")


# Test data - valid AES-128 key
VALID_KEY = bytes.fromhex("0123456789abcdef0123456789abcdef")
MAC_ADDRESS = "AA:BB:CC:DD:EE:FF"


class TestEADDecryptorFactoryMethods:
    """Tests for EADDecryptor factory methods."""

    def test_from_key_valid(self) -> None:
        """Test creating decryptor with valid 16-byte key."""
        decryptor = EADDecryptor.from_key(VALID_KEY)
        assert decryptor is not None
        assert decryptor._static_key == VALID_KEY
        assert decryptor._key_provider is None

    def test_from_key_invalid_size_short(self) -> None:
        """Test error when key is too short."""
        with pytest.raises(ValueError) as exc_info:
            EADDecryptor.from_key(bytes.fromhex("0123456789abcdef"))  # 8 bytes

        assert "16 bytes" in str(exc_info.value)
        assert "8" in str(exc_info.value)

    def test_from_key_invalid_size_long(self) -> None:
        """Test error when key is too long."""
        with pytest.raises(ValueError) as exc_info:
            EADDecryptor.from_key(bytes(32))  # 32 bytes

        assert "16 bytes" in str(exc_info.value)
        assert "32" in str(exc_info.value)

    def test_from_provider(self) -> None:
        """Test creating decryptor with key provider."""
        provider = DictKeyProvider()
        decryptor = EADDecryptor.from_provider(provider)

        assert decryptor is not None
        assert decryptor._key_provider is provider
        assert decryptor._static_key is None


class TestEADDecryptorDecrypt:
    """Tests for EADDecryptor.decrypt() method."""

    def test_decrypt_data_too_short(self) -> None:
        """Test decrypt returns error for data shorter than minimum."""
        decryptor = EADDecryptor.from_key(VALID_KEY)

        # 7 bytes - less than minimum 9 bytes
        result = decryptor.decrypt(bytes(7), MAC_ADDRESS)

        assert result.success is False
        assert result.error_type == EADError.INSUFFICIENT_DATA
        assert "7 bytes" in str(result.error)
        assert "9" in str(result.error)

    def test_decrypt_empty_data(self) -> None:
        """Test decrypt returns error for empty data."""
        decryptor = EADDecryptor.from_key(VALID_KEY)

        result = decryptor.decrypt(b"", MAC_ADDRESS)

        assert result.success is False
        assert result.error_type == EADError.INSUFFICIENT_DATA

    def test_decrypt_invalid_mac_format(self) -> None:
        """Test decrypt handles invalid MAC address format."""
        decryptor = EADDecryptor.from_key(VALID_KEY)

        # Valid EAD structure but invalid MAC
        raw_ead = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")  # 13 bytes

        result = decryptor.decrypt(raw_ead, "INVALID")

        assert result.success is False
        assert result.error_type == EADError.CORRUPTED_DATA

    def test_decrypt_no_key_from_provider(self) -> None:
        """Test decrypt returns NO_KEY_AVAILABLE when provider has no key."""
        provider = DictKeyProvider()  # Empty provider
        decryptor = EADDecryptor.from_provider(provider)

        # Valid structure EAD data
        raw_ead = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")

        result = decryptor.decrypt(raw_ead, MAC_ADDRESS)

        assert result.success is False
        assert result.error_type == EADError.NO_KEY_AVAILABLE
        assert MAC_ADDRESS in str(result.error)

    def test_decrypt_wrong_key_returns_invalid_key(self) -> None:
        """Test decrypt with wrong key returns INVALID_KEY error."""
        # Create decryptor with a key that won't match the MIC
        decryptor = EADDecryptor.from_key(VALID_KEY)

        # Valid structure but MIC won't verify with this key
        raw_ead = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")

        result = decryptor.decrypt(raw_ead, MAC_ADDRESS)

        assert result.success is False
        assert result.error_type == EADError.INVALID_KEY
        assert "MIC verification failed" in str(result.error)

    def test_decrypt_with_associated_data_mismatch(self) -> None:
        """Test decrypt fails when associated data doesn't match."""
        decryptor = EADDecryptor.from_key(VALID_KEY)

        # Data encrypted without AAD, try to decrypt with AAD
        raw_ead = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")

        result = decryptor.decrypt(raw_ead, MAC_ADDRESS, associated_data=b"some_aad")

        assert result.success is False
        assert result.error_type == EADError.INVALID_KEY


class TestEADDecryptorCaching:
    """Tests for EADDecryptor cipher caching."""

    def test_cipher_cache_populated(self) -> None:
        """Test that cipher is cached after first use."""
        decryptor = EADDecryptor.from_key(VALID_KEY)

        # Cache should be empty initially
        assert len(decryptor._cipher_cache) == 0

        # Attempt decrypt (will fail but still caches cipher)
        raw_ead = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")
        decryptor.decrypt(raw_ead, MAC_ADDRESS)

        # Cache should now have one entry
        assert len(decryptor._cipher_cache) == 1
        assert VALID_KEY in decryptor._cipher_cache

    def test_cipher_cache_reused(self) -> None:
        """Test that cached cipher is reused on subsequent calls."""
        decryptor = EADDecryptor.from_key(VALID_KEY)
        raw_ead = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")

        # First call
        decryptor.decrypt(raw_ead, MAC_ADDRESS)
        cipher1 = decryptor._cipher_cache.get(VALID_KEY)

        # Second call
        decryptor.decrypt(raw_ead, MAC_ADDRESS)
        cipher2 = decryptor._cipher_cache.get(VALID_KEY)

        # Same cipher object should be reused
        assert cipher1 is cipher2

    def test_clear_cache(self) -> None:
        """Test clear_cache() empties the cipher cache."""
        decryptor = EADDecryptor.from_key(VALID_KEY)
        raw_ead = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")

        # Populate cache
        decryptor.decrypt(raw_ead, MAC_ADDRESS)
        assert len(decryptor._cipher_cache) > 0

        # Clear cache
        decryptor.clear_cache()

        # Cache should be empty
        assert len(decryptor._cipher_cache) == 0

    def test_multiple_keys_in_cache(self) -> None:
        """Test provider-based decryptor can cache multiple keys."""
        key1 = bytes.fromhex("0123456789abcdef0123456789abcdef")
        key2 = bytes.fromhex("fedcba9876543210fedcba9876543210")
        iv = bytes.fromhex("0102030405060708")

        provider = DictKeyProvider(
            ead_keys={
                "AA:BB:CC:DD:EE:FF": EADKeyMaterial(session_key=key1, iv=iv),
                "11:22:33:44:55:66": EADKeyMaterial(session_key=key2, iv=iv),
            }
        )
        decryptor = EADDecryptor.from_provider(provider)

        raw_ead = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")

        # Decrypt for both devices
        decryptor.decrypt(raw_ead, "AA:BB:CC:DD:EE:FF")
        decryptor.decrypt(raw_ead, "11:22:33:44:55:66")

        # Both keys should be cached
        assert len(decryptor._cipher_cache) == 2
        assert key1 in decryptor._cipher_cache
        assert key2 in decryptor._cipher_cache


class TestEADDecryptorIntegration:
    """Integration tests for EADDecryptor with real encryption/decryption."""

    def test_encrypt_then_decrypt_roundtrip(self) -> None:
        """Test encrypting data and then decrypting it."""
        from cryptography.hazmat.primitives.ciphers.aead import AESCCM

        from bluetooth_sig.advertising.ead_decryptor import build_ead_nonce, mac_address_to_bytes
        from bluetooth_sig.types.ead import EAD_MIC_SIZE

        # Setup
        session_key = VALID_KEY
        plaintext = b"Hello, BLE!"
        randomizer = bytes.fromhex("0102030405")
        device_address = mac_address_to_bytes(MAC_ADDRESS)

        # Encrypt
        cipher = AESCCM(session_key, tag_length=EAD_MIC_SIZE)
        nonce = build_ead_nonce(randomizer, device_address)
        ciphertext_with_mic = cipher.encrypt(nonce, plaintext, None)

        # Build raw EAD format: randomizer + ciphertext + mic
        # Note: AESCCM appends MIC to ciphertext
        encrypted_payload = ciphertext_with_mic[:-EAD_MIC_SIZE]
        mic = ciphertext_with_mic[-EAD_MIC_SIZE:]
        raw_ead = randomizer + encrypted_payload + mic

        # Decrypt
        decryptor = EADDecryptor.from_key(session_key)
        result = decryptor.decrypt(raw_ead, MAC_ADDRESS)

        assert result.success is True
        assert result.plaintext == plaintext
        assert result.error is None
        assert result.error_type is None

    def test_encrypt_decrypt_with_aad(self) -> None:
        """Test encryption/decryption with associated authenticated data."""
        from cryptography.hazmat.primitives.ciphers.aead import AESCCM

        from bluetooth_sig.advertising.ead_decryptor import build_ead_nonce, mac_address_to_bytes
        from bluetooth_sig.types.ead import EAD_MIC_SIZE

        session_key = VALID_KEY
        plaintext = b"Secure data"
        aad = b"authenticated_context"
        randomizer = bytes.fromhex("0102030405")
        device_address = mac_address_to_bytes(MAC_ADDRESS)

        # Encrypt with AAD
        cipher = AESCCM(session_key, tag_length=EAD_MIC_SIZE)
        nonce = build_ead_nonce(randomizer, device_address)
        ciphertext_with_mic = cipher.encrypt(nonce, plaintext, aad)

        encrypted_payload = ciphertext_with_mic[:-EAD_MIC_SIZE]
        mic = ciphertext_with_mic[-EAD_MIC_SIZE:]
        raw_ead = randomizer + encrypted_payload + mic

        # Decrypt with same AAD
        decryptor = EADDecryptor.from_key(session_key)
        result = decryptor.decrypt(raw_ead, MAC_ADDRESS, associated_data=aad)

        assert result.success is True
        assert result.plaintext == plaintext

    def test_decrypt_empty_payload(self) -> None:
        """Test decrypting EAD with empty payload (just randomizer + MIC)."""
        from cryptography.hazmat.primitives.ciphers.aead import AESCCM

        from bluetooth_sig.advertising.ead_decryptor import build_ead_nonce, mac_address_to_bytes
        from bluetooth_sig.types.ead import EAD_MIC_SIZE

        session_key = VALID_KEY
        plaintext = b""  # Empty payload
        randomizer = bytes.fromhex("0102030405")
        device_address = mac_address_to_bytes(MAC_ADDRESS)

        # Encrypt empty data
        cipher = AESCCM(session_key, tag_length=EAD_MIC_SIZE)
        nonce = build_ead_nonce(randomizer, device_address)
        ciphertext_with_mic = cipher.encrypt(nonce, plaintext, None)

        # For empty plaintext, ciphertext_with_mic is just the MIC
        raw_ead = randomizer + ciphertext_with_mic

        # Decrypt
        decryptor = EADDecryptor.from_key(session_key)
        result = decryptor.decrypt(raw_ead, MAC_ADDRESS)

        assert result.success is True
        assert result.plaintext == b""


class TestEADDecryptorProviderIntegration:
    """Tests for EADDecryptor with DictKeyProvider."""

    def test_provider_key_lookup_success(self) -> None:
        """Test successful key lookup from provider."""
        from cryptography.hazmat.primitives.ciphers.aead import AESCCM

        from bluetooth_sig.advertising.ead_decryptor import build_ead_nonce, mac_address_to_bytes
        from bluetooth_sig.types.ead import EAD_MIC_SIZE

        session_key = VALID_KEY
        iv = bytes.fromhex("0102030405060708")
        provider = DictKeyProvider(ead_keys={MAC_ADDRESS: EADKeyMaterial(session_key=session_key, iv=iv)})

        # Create EAD data
        plaintext = b"Provider test"
        randomizer = bytes.fromhex("0102030405")
        device_address = mac_address_to_bytes(MAC_ADDRESS)

        cipher = AESCCM(session_key, tag_length=EAD_MIC_SIZE)
        nonce = build_ead_nonce(randomizer, device_address)
        ciphertext_with_mic = cipher.encrypt(nonce, plaintext, None)

        encrypted_payload = ciphertext_with_mic[:-EAD_MIC_SIZE]
        mic = ciphertext_with_mic[-EAD_MIC_SIZE:]
        raw_ead = randomizer + encrypted_payload + mic

        # Decrypt using provider
        decryptor = EADDecryptor.from_provider(provider)
        result = decryptor.decrypt(raw_ead, MAC_ADDRESS)

        assert result.success is True
        assert result.plaintext == plaintext

    def test_provider_case_insensitive_mac(self) -> None:
        """Test provider handles case-insensitive MAC addresses."""
        iv = bytes.fromhex("0102030405060708")
        provider = DictKeyProvider(ead_keys={"aa:bb:cc:dd:ee:ff": EADKeyMaterial(session_key=VALID_KEY, iv=iv)})

        decryptor = EADDecryptor.from_provider(provider)
        raw_ead = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")

        # Query with uppercase should still find the key
        result = decryptor.decrypt(raw_ead, "AA:BB:CC:DD:EE:FF")

        # Will fail MIC verification but NOT return NO_KEY_AVAILABLE
        assert result.error_type != EADError.NO_KEY_AVAILABLE

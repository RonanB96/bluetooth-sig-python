"""Tests for BLE Encrypted Advertising Data (EAD) decryption.

Tests the EAD module implementation per Bluetooth Core Spec
Supplement Section 1.23.
"""

from __future__ import annotations

import pytest

from bluetooth_sig.advertising.ead_decryptor import (
    build_ead_nonce,
    decrypt_ead,
    decrypt_ead_from_raw,
    mac_address_to_bytes,
)
from bluetooth_sig.advertising.encryption import DictKeyProvider
from bluetooth_sig.types.ead import (
    EAD_MIC_SIZE,
    EAD_MIN_SIZE,
    EAD_RANDOMIZER_SIZE,
    EADDecryptResult,
    EADError,
    EADKeyMaterial,
    EncryptedAdvertisingData,
)

# Skip all tests in this module if cryptography is not installed
pytest.importorskip("cryptography")


class TestEncryptedAdvertisingData:
    """Tests for EncryptedAdvertisingData parsing."""

    def test_from_bytes_valid_minimum(self) -> None:
        """Test parsing minimum valid EAD data (9 bytes: randomizer + MIC)."""
        # 5-byte randomizer + 0-byte payload + 4-byte MIC
        raw = bytes.fromhex("0102030405" + "11223344")
        ead = EncryptedAdvertisingData.from_bytes(raw)

        assert ead.randomizer == bytes.fromhex("0102030405")
        assert ead.encrypted_payload == b""
        assert ead.mic == bytes.fromhex("11223344")

    def test_from_bytes_valid_with_payload(self) -> None:
        """Test parsing EAD data with encrypted payload."""
        # 5-byte randomizer + 4-byte payload + 4-byte MIC
        raw = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")
        ead = EncryptedAdvertisingData.from_bytes(raw)

        assert ead.randomizer == bytes.fromhex("0102030405")
        assert ead.encrypted_payload == bytes.fromhex("aabbccdd")
        assert ead.mic == bytes.fromhex("11223344")

    def test_from_bytes_too_short(self) -> None:
        """Test error on data shorter than minimum size."""
        raw = bytes.fromhex("01020304050607")  # 7 bytes, need 9

        with pytest.raises(ValueError) as exc_info:
            EncryptedAdvertisingData.from_bytes(raw)

        assert "at least 9 bytes" in str(exc_info.value)
        assert "7 bytes" in str(exc_info.value)

    def test_from_bytes_empty(self) -> None:
        """Test error on empty data."""
        with pytest.raises(ValueError) as exc_info:
            EncryptedAdvertisingData.from_bytes(b"")

        assert "at least 9 bytes" in str(exc_info.value)

    def test_constants(self) -> None:
        """Test EAD format constants."""
        assert EAD_RANDOMIZER_SIZE == 5
        assert EAD_MIC_SIZE == 4
        assert EAD_MIN_SIZE == 9


class TestBuildEadNonce:
    """Tests for EAD nonce construction."""

    def test_nonce_construction(self) -> None:
        """Test 13-byte nonce is correctly constructed."""
        randomizer = bytes.fromhex("0102030405")
        address = bytes.fromhex("aabbccddeeff")

        nonce = build_ead_nonce(randomizer, address)

        assert len(nonce) == 13
        # Nonce = randomizer(5) + address(6) + padding(2)
        assert nonce[:5] == randomizer
        assert nonce[5:11] == address
        assert nonce[11:] == b"\x00\x00"

    def test_nonce_invalid_randomizer_size(self) -> None:
        """Test error on wrong randomizer size."""
        randomizer = bytes.fromhex("01020304")  # 4 bytes, need 5
        address = bytes.fromhex("aabbccddeeff")

        with pytest.raises(ValueError) as exc_info:
            build_ead_nonce(randomizer, address)

        assert "5 bytes" in str(exc_info.value)

    def test_nonce_invalid_address_size(self) -> None:
        """Test error on wrong address size."""
        randomizer = bytes.fromhex("0102030405")
        address = bytes.fromhex("aabbccddee")  # 5 bytes, need 6

        with pytest.raises(ValueError) as exc_info:
            build_ead_nonce(randomizer, address)

        assert "6 bytes" in str(exc_info.value)


class TestMacAddressToBytes:
    """Tests for MAC address string conversion."""

    def test_colon_format(self) -> None:
        """Test MAC address with colons."""
        result = mac_address_to_bytes("AA:BB:CC:DD:EE:FF")
        assert result == bytes.fromhex("aabbccddeeff")

    def test_dash_format(self) -> None:
        """Test MAC address with dashes."""
        result = mac_address_to_bytes("AA-BB-CC-DD-EE-FF")
        assert result == bytes.fromhex("aabbccddeeff")

    def test_lowercase(self) -> None:
        """Test lowercase MAC address."""
        result = mac_address_to_bytes("aa:bb:cc:dd:ee:ff")
        assert result == bytes.fromhex("aabbccddeeff")

    def test_no_separator(self) -> None:
        """Test MAC address without separators."""
        result = mac_address_to_bytes("AABBCCDDEEFF")
        assert result == bytes.fromhex("aabbccddeeff")

    def test_invalid_length(self) -> None:
        """Test error on invalid MAC length."""
        with pytest.raises(ValueError) as exc_info:
            mac_address_to_bytes("AA:BB:CC:DD:EE")

        assert "Invalid MAC address" in str(exc_info.value)

    def test_invalid_hex(self) -> None:
        """Test error on invalid hex characters."""
        with pytest.raises(ValueError) as exc_info:
            mac_address_to_bytes("GG:HH:II:JJ:KK:LL")

        assert "Invalid MAC address" in str(exc_info.value)


class TestDecryptEad:
    """Tests for EAD decryption function."""

    @pytest.fixture
    def valid_key(self) -> bytes:
        """Return a valid 16-byte AES key."""
        return bytes.fromhex("0123456789abcdef0123456789abcdef")

    @pytest.fixture
    def device_address(self) -> bytes:
        """Return a valid 6-byte device address."""
        return bytes.fromhex("aabbccddeeff")

    def test_decrypt_invalid_key_size(
        self,
        device_address: bytes,
    ) -> None:
        """Test error on invalid session key size."""
        # Create minimal valid EAD data
        raw = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")
        ead = EncryptedAdvertisingData.from_bytes(raw)

        # 15-byte key (invalid, should be 16)
        invalid_key = bytes.fromhex("0123456789abcdef0123456789abcd")

        result = decrypt_ead(ead, invalid_key, device_address)

        assert result.success is False
        assert result.error_type == EADError.CORRUPTED_DATA
        assert "16 bytes" in str(result.error)

    def test_decrypt_invalid_address_size(
        self,
        valid_key: bytes,
    ) -> None:
        """Test error on invalid device address size."""
        raw = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")
        ead = EncryptedAdvertisingData.from_bytes(raw)

        # 5-byte address (invalid, should be 6)
        invalid_address = bytes.fromhex("aabbccddee")

        result = decrypt_ead(ead, valid_key, invalid_address)

        assert result.success is False
        assert result.error_type == EADError.CORRUPTED_DATA
        assert "6 bytes" in str(result.error)

    def test_decrypt_wrong_key_returns_invalid_key_error(
        self,
        device_address: bytes,
    ) -> None:
        """Test that wrong key returns INVALID_KEY error."""
        # This test encrypts data with one key and decrypts with another
        from cryptography.hazmat.primitives.ciphers.aead import AESCCM

        correct_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        wrong_key = bytes.fromhex("fedcba9876543210fedcba9876543210")

        # Encrypt some data with the correct key
        randomizer = bytes.fromhex("0102030405")
        plaintext = b"test sensor data"
        nonce = build_ead_nonce(randomizer, device_address)

        cipher = AESCCM(correct_key, tag_length=4)
        ciphertext_with_mic = cipher.encrypt(nonce, plaintext, None)

        # Build EAD structure
        ead = EncryptedAdvertisingData(
            randomizer=randomizer,
            encrypted_payload=ciphertext_with_mic[:-4],
            mic=ciphertext_with_mic[-4:],
        )

        # Try to decrypt with wrong key
        result = decrypt_ead(ead, wrong_key, device_address)

        assert result.success is False
        assert result.error_type == EADError.INVALID_KEY
        assert "MIC verification failed" in str(result.error)

    def test_decrypt_success(
        self,
        device_address: bytes,
    ) -> None:
        """Test successful decryption."""
        from cryptography.hazmat.primitives.ciphers.aead import AESCCM

        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        randomizer = bytes.fromhex("0102030405")
        plaintext = b"sensor data 123"

        # Encrypt
        nonce = build_ead_nonce(randomizer, device_address)
        cipher = AESCCM(session_key, tag_length=4)
        ciphertext_with_mic = cipher.encrypt(nonce, plaintext, None)

        # Build EAD structure
        ead = EncryptedAdvertisingData(
            randomizer=randomizer,
            encrypted_payload=ciphertext_with_mic[:-4],
            mic=ciphertext_with_mic[-4:],
        )

        # Decrypt
        result = decrypt_ead(ead, session_key, device_address)

        assert result.success is True
        assert result.plaintext == plaintext
        assert result.error is None
        assert result.error_type is None

    def test_decrypt_with_associated_data(
        self,
        device_address: bytes,
    ) -> None:
        """Test decryption with associated data (AAD)."""
        from cryptography.hazmat.primitives.ciphers.aead import AESCCM

        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        randomizer = bytes.fromhex("0102030405")
        plaintext = b"sensor readings"
        aad = b"device_context"

        # Encrypt with AAD
        nonce = build_ead_nonce(randomizer, device_address)
        cipher = AESCCM(session_key, tag_length=4)
        ciphertext_with_mic = cipher.encrypt(nonce, plaintext, aad)

        # Build EAD structure
        ead = EncryptedAdvertisingData(
            randomizer=randomizer,
            encrypted_payload=ciphertext_with_mic[:-4],
            mic=ciphertext_with_mic[-4:],
        )

        # Decrypt with same AAD
        result = decrypt_ead(ead, session_key, device_address, aad)

        assert result.success is True
        assert result.plaintext == plaintext

    def test_decrypt_wrong_associated_data(
        self,
        device_address: bytes,
    ) -> None:
        """Test decryption fails with wrong associated data."""
        from cryptography.hazmat.primitives.ciphers.aead import AESCCM

        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        randomizer = bytes.fromhex("0102030405")
        plaintext = b"sensor readings"
        correct_aad = b"device_context"
        wrong_aad = b"wrong_context"

        # Encrypt with correct AAD
        nonce = build_ead_nonce(randomizer, device_address)
        cipher = AESCCM(session_key, tag_length=4)
        ciphertext_with_mic = cipher.encrypt(nonce, plaintext, correct_aad)

        # Build EAD structure
        ead = EncryptedAdvertisingData(
            randomizer=randomizer,
            encrypted_payload=ciphertext_with_mic[:-4],
            mic=ciphertext_with_mic[-4:],
        )

        # Decrypt with wrong AAD
        result = decrypt_ead(ead, session_key, device_address, wrong_aad)

        assert result.success is False
        assert result.error_type == EADError.INVALID_KEY

    def test_decrypt_corrupted_mic(
        self,
        device_address: bytes,
    ) -> None:
        """Test decryption fails with corrupted MIC."""
        from cryptography.hazmat.primitives.ciphers.aead import AESCCM

        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        randomizer = bytes.fromhex("0102030405")
        plaintext = b"sensor data"

        # Encrypt
        nonce = build_ead_nonce(randomizer, device_address)
        cipher = AESCCM(session_key, tag_length=4)
        ciphertext_with_mic = cipher.encrypt(nonce, plaintext, None)

        # Corrupt the MIC (last 4 bytes)
        corrupted_mic = bytes([b ^ 0xFF for b in ciphertext_with_mic[-4:]])

        # Build EAD structure with corrupted MIC
        ead = EncryptedAdvertisingData(
            randomizer=randomizer,
            encrypted_payload=ciphertext_with_mic[:-4],
            mic=corrupted_mic,
        )

        # Decrypt should fail
        result = decrypt_ead(ead, session_key, device_address)

        assert result.success is False
        assert result.error_type == EADError.INVALID_KEY

    def test_decrypt_corrupted_ciphertext(
        self,
        device_address: bytes,
    ) -> None:
        """Test decryption fails with corrupted ciphertext."""
        from cryptography.hazmat.primitives.ciphers.aead import AESCCM

        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        randomizer = bytes.fromhex("0102030405")
        plaintext = b"sensor data"

        # Encrypt
        nonce = build_ead_nonce(randomizer, device_address)
        cipher = AESCCM(session_key, tag_length=4)
        ciphertext_with_mic = cipher.encrypt(nonce, plaintext, None)

        # Corrupt the ciphertext (flip bits in first byte)
        encrypted_payload = bytearray(ciphertext_with_mic[:-4])
        encrypted_payload[0] ^= 0xFF

        # Build EAD structure with corrupted payload
        ead = EncryptedAdvertisingData(
            randomizer=randomizer,
            encrypted_payload=bytes(encrypted_payload),
            mic=ciphertext_with_mic[-4:],
        )

        # Decrypt should fail
        result = decrypt_ead(ead, session_key, device_address)

        assert result.success is False
        assert result.error_type == EADError.INVALID_KEY


class TestDecryptEadFromRaw:
    """Tests for convenience decrypt_ead_from_raw function."""

    def test_decrypt_from_raw_success(self) -> None:
        """Test decryption from raw bytes with MAC address string."""
        from cryptography.hazmat.primitives.ciphers.aead import AESCCM

        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        mac_address = "AA:BB:CC:DD:EE:FF"
        device_address = bytes.fromhex("aabbccddeeff")
        randomizer = bytes.fromhex("0102030405")
        plaintext = b"test data"

        # Encrypt
        nonce = build_ead_nonce(randomizer, device_address)
        cipher = AESCCM(session_key, tag_length=4)
        ciphertext_with_mic = cipher.encrypt(nonce, plaintext, None)

        # Build raw EAD bytes
        raw_ead = randomizer + ciphertext_with_mic

        # Decrypt using convenience function
        result = decrypt_ead_from_raw(raw_ead, session_key, mac_address)

        assert result.success is True
        assert result.plaintext == plaintext

    def test_decrypt_from_raw_too_short(self) -> None:
        """Test error on raw data too short."""
        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        mac_address = "AA:BB:CC:DD:EE:FF"
        raw_ead = bytes.fromhex("0102030405060708")  # 8 bytes, need 9

        result = decrypt_ead_from_raw(raw_ead, session_key, mac_address)

        assert result.success is False
        assert result.error_type == EADError.INSUFFICIENT_DATA

    def test_decrypt_from_raw_invalid_mac(self) -> None:
        """Test error on invalid MAC address format."""
        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        invalid_mac = "INVALID"
        raw_ead = bytes.fromhex("0102030405" + "aabbccdd" + "11223344")

        result = decrypt_ead_from_raw(raw_ead, session_key, invalid_mac)

        assert result.success is False
        assert result.error_type == EADError.CORRUPTED_DATA


class TestEADKeyMaterial:
    """Tests for EADKeyMaterial dataclass."""

    def test_valid_key_material(self) -> None:
        """Test creating valid EAD key material."""
        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        iv = bytes.fromhex("0102030405060708")

        key_material = EADKeyMaterial(session_key=session_key, iv=iv)

        assert key_material.session_key == session_key
        assert key_material.iv == iv

    def test_invalid_session_key_size(self) -> None:
        """Test error on invalid session key size."""
        # 15-byte key (should be 16)
        session_key = bytes.fromhex("0123456789abcdef0123456789abcd")
        iv = bytes.fromhex("0102030405060708")

        with pytest.raises(ValueError) as exc_info:
            EADKeyMaterial(session_key=session_key, iv=iv)

        assert "16 bytes" in str(exc_info.value)

    def test_invalid_iv_size(self) -> None:
        """Test error on invalid IV size."""
        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        # 7-byte IV (should be 8)
        iv = bytes.fromhex("01020304050607")

        with pytest.raises(ValueError) as exc_info:
            EADKeyMaterial(session_key=session_key, iv=iv)

        assert "8 bytes" in str(exc_info.value)


class TestDictKeyProviderEAD:
    """Tests for DictKeyProvider EAD key support."""

    def test_get_ead_key_found(self) -> None:
        """Test getting an existing EAD key."""
        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        iv = bytes.fromhex("0102030405060708")
        key_material = EADKeyMaterial(session_key=session_key, iv=iv)

        provider = DictKeyProvider(ead_keys={"AA:BB:CC:DD:EE:FF": key_material})

        result = provider.get_ead_key("AA:BB:CC:DD:EE:FF")

        assert result is not None
        assert result.session_key == session_key
        assert result.iv == iv

    def test_get_ead_key_case_insensitive(self) -> None:
        """Test EAD key lookup is case insensitive."""
        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        iv = bytes.fromhex("0102030405060708")
        key_material = EADKeyMaterial(session_key=session_key, iv=iv)

        provider = DictKeyProvider(ead_keys={"aa:bb:cc:dd:ee:ff": key_material})

        result = provider.get_ead_key("AA:BB:CC:DD:EE:FF")

        assert result is not None

    def test_get_ead_key_not_found(self) -> None:
        """Test getting a missing EAD key returns None."""
        provider = DictKeyProvider()

        result = provider.get_ead_key("AA:BB:CC:DD:EE:FF")

        assert result is None

    def test_set_ead_key(self) -> None:
        """Test setting an EAD key."""
        provider = DictKeyProvider()
        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        iv = bytes.fromhex("0102030405060708")
        key_material = EADKeyMaterial(session_key=session_key, iv=iv)

        provider.set_ead_key("AA:BB:CC:DD:EE:FF", key_material)

        assert provider.get_ead_key("AA:BB:CC:DD:EE:FF") is not None

    def test_remove_ead_key(self) -> None:
        """Test removing an EAD key."""
        session_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        iv = bytes.fromhex("0102030405060708")
        key_material = EADKeyMaterial(session_key=session_key, iv=iv)

        provider = DictKeyProvider(ead_keys={"AA:BB:CC:DD:EE:FF": key_material})
        provider.remove_ead_key("AA:BB:CC:DD:EE:FF")

        assert provider.get_ead_key("AA:BB:CC:DD:EE:FF") is None

    def test_both_key_types(self) -> None:
        """Test provider can hold both legacy and EAD keys."""
        legacy_key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        session_key = bytes.fromhex("fedcba9876543210fedcba9876543210")
        iv = bytes.fromhex("0102030405060708")
        ead_key = EADKeyMaterial(session_key=session_key, iv=iv)

        provider = DictKeyProvider(
            keys={"AA:BB:CC:DD:EE:FF": legacy_key},
            ead_keys={"11:22:33:44:55:66": ead_key},
        )

        assert provider.get_key("AA:BB:CC:DD:EE:FF") == legacy_key
        retrieved_ead_key = provider.get_ead_key("11:22:33:44:55:66")
        assert retrieved_ead_key is not None
        assert retrieved_ead_key.session_key == session_key


class TestEADDecryptResult:
    """Tests for EADDecryptResult struct."""

    def test_success_result(self) -> None:
        """Test creating a successful result."""
        result = EADDecryptResult(success=True, plaintext=b"decrypted data")

        assert result.success is True
        assert result.plaintext == b"decrypted data"
        assert result.error is None
        assert result.error_type is None

    def test_error_result(self) -> None:
        """Test creating an error result."""
        result = EADDecryptResult(
            success=False,
            plaintext=None,
            error="MIC verification failed",
            error_type=EADError.INVALID_KEY,
        )

        assert result.success is False
        assert result.plaintext is None
        assert result.error == "MIC verification failed"
        assert result.error_type == EADError.INVALID_KEY


class TestEADError:
    """Tests for EADError enum."""

    def test_all_error_types_exist(self) -> None:
        """Test all expected error types are defined."""
        assert EADError.INVALID_KEY is not None
        assert EADError.REPLAY_DETECTED is not None
        assert EADError.CORRUPTED_DATA is not None
        assert EADError.NO_KEY_AVAILABLE is not None
        assert EADError.INSUFFICIENT_DATA is not None

    def test_error_types_are_distinct(self) -> None:
        """Test error types have distinct values."""
        error_values = [e.value for e in EADError]
        assert len(error_values) == len(set(error_values))

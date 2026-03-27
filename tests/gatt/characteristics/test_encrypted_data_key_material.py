"""Tests for Encrypted Data Key Material characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.encrypted_data_key_material import (
    EncryptedDataKeyMaterialCharacteristic,
    EncryptedDataKeyMaterialData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestEncryptedDataKeyMaterialCharacteristic(CommonCharacteristicTests):
    """Test suite for Encrypted Data Key Material characteristic."""

    @pytest.fixture
    def characteristic(self) -> EncryptedDataKeyMaterialCharacteristic:
        return EncryptedDataKeyMaterialCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B88"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"\x00" * 24),
                expected_value=EncryptedDataKeyMaterialData(
                    session_key=b"\x00" * 16,
                    iv=b"\x00" * 8,
                ),
                description="All zeros key material",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8"
                ),
                expected_value=EncryptedDataKeyMaterialData(
                    session_key=(b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10"),
                    iv=b"\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8",
                ),
                description="Sequential session key with distinct IV",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = EncryptedDataKeyMaterialCharacteristic()
        original = EncryptedDataKeyMaterialData(
            session_key=b"\xff" * 16,
            iv=b"\xaa" * 8,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

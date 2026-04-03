"""Tests for ESL Response Key Material characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.esl_response_key_material import (
    ESLResponseKeyMaterialCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestESLResponseKeyMaterialCharacteristic(CommonCharacteristicTests):
    """Test suite for ESL Response Key Material characteristic."""

    @pytest.fixture
    def characteristic(self) -> ESLResponseKeyMaterialCharacteristic:
        return ESLResponseKeyMaterialCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BF8"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"\x00" * 16),
                expected_value=b"\x00" * 16,
                description="All-zero 128-bit key material",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10"),
                expected_value=(b"\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10"),
                description="Non-trivial 128-bit key material",
            ),
        ]

    def test_encode_rejects_wrong_length(self) -> None:
        """Verify encode rejects non-16-byte input."""
        from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError

        char = ESLResponseKeyMaterialCharacteristic()
        with pytest.raises(CharacteristicEncodeError, match="exactly 16 bytes"):
            char.build_value(b"\x00" * 8)

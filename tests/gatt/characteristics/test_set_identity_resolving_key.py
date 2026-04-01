"""Tests for Set Identity Resolving Key characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.set_identity_resolving_key import (
    SetIdentityResolvingKeyCharacteristic,
    SetIdentityResolvingKeyData,
    SIRKType,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSetIdentityResolvingKeyCharacteristic(CommonCharacteristicTests):
    """Test suite for Set Identity Resolving Key characteristic."""

    @pytest.fixture
    def characteristic(self) -> SetIdentityResolvingKeyCharacteristic:
        return SetIdentityResolvingKeyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B84"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"\x00" + b"\x00" * 16),
                expected_value=SetIdentityResolvingKeyData(sirk_type=SIRKType.ENCRYPTED, value=b"\x00" * 16),
                description="Encrypted SIRK, all zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x01\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10"),
                expected_value=SetIdentityResolvingKeyData(
                    sirk_type=SIRKType.PLAIN_TEXT,
                    value=b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10",
                ),
                description="Plain text SIRK, sequential bytes",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = SetIdentityResolvingKeyCharacteristic()
        original = SetIdentityResolvingKeyData(sirk_type=SIRKType.ENCRYPTED, value=b"\xaa\xbb\xcc\xdd" * 4)
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

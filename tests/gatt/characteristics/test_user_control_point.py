"""Tests for User Control Point characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.user_control_point import (
    UserControlPointCharacteristic,
    UserControlPointData,
    UserControlPointOpCode,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestUserControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for User Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> UserControlPointCharacteristic:
        return UserControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A9F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=UserControlPointData(
                    opcode=UserControlPointOpCode.REGISTER_NEW_USER,
                ),
                description="Register new user, no params",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x03, 0xE8]),
                expected_value=UserControlPointData(
                    opcode=UserControlPointOpCode.CONSENT,
                    parameter=b"\x03\xe8",
                ),
                description="Consent with user index and consent code",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x20, 0x01, 0x01]),
                expected_value=UserControlPointData(
                    opcode=UserControlPointOpCode.RESPONSE,
                    parameter=b"\x01\x01",
                ),
                description="Response code",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = UserControlPointCharacteristic()
        original = UserControlPointData(
            opcode=UserControlPointOpCode.DELETE_USER,
            parameter=b"\x05",
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

"""Tests for TerminationReasonCharacteristic (2BC0)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.termination_reason import TerminationReason, TerminationReasonCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTerminationReason(CommonCharacteristicTests):
    """Test suite for TerminationReasonCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> TerminationReasonCharacteristic:
        return TerminationReasonCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BC0"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), TerminationReason.REMOTE_PARTY_ENDED, "Remote ended"),
            CharacteristicTestData(bytearray([0x01]), TerminationReason.SERVER_ENDED, "Server ended"),
            CharacteristicTestData(bytearray([0x04]), TerminationReason.CLIENT_ENDED, "Client ended"),
            CharacteristicTestData(bytearray([0x07]), TerminationReason.UNSPECIFIED, "Unspecified"),
        ]

    def test_roundtrip(self, characteristic: TerminationReasonCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), TerminationReason.REMOTE_PARTY_ENDED, "Remote ended"),
            CharacteristicTestData(bytearray([0x01]), TerminationReason.SERVER_ENDED, "Server ended"),
            CharacteristicTestData(bytearray([0x04]), TerminationReason.CLIENT_ENDED, "Client ended"),
            CharacteristicTestData(bytearray([0x07]), TerminationReason.UNSPECIFIED, "Unspecified"),
        ]

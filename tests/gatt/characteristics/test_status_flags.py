"""Tests for StatusFlagsCharacteristic (2BBB)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.status_flags import StatusFlags, StatusFlagsCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestStatusFlags(CommonCharacteristicTests):
    """Test suite for StatusFlagsCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> StatusFlagsCharacteristic:
        return StatusFlagsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BBB"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00]), StatusFlags(0), "No flags"),
            CharacteristicTestData(bytearray([0x01, 0x00]), StatusFlags.INBAND_RINGTONE, "Inband ringtone"),
            CharacteristicTestData(
                bytearray([0x03, 0x00]), StatusFlags.INBAND_RINGTONE | StatusFlags.SILENT_MODE, "All flags"
            ),
        ]

    def test_roundtrip(self, characteristic: StatusFlagsCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00]), StatusFlags(0), "No flags"),
            CharacteristicTestData(bytearray([0x01, 0x00]), StatusFlags.INBAND_RINGTONE, "Inband ringtone"),
            CharacteristicTestData(
                bytearray([0x03, 0x00]), StatusFlags.INBAND_RINGTONE | StatusFlags.SILENT_MODE, "All flags"
            ),
        ]

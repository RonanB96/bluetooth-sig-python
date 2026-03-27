"""Tests for IMD Status characteristic (0x2C0C)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.imd_status import (
    IMDStatusCharacteristic,
    IMDStatusData,
    IMDStatusFlags,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIMDStatusCharacteristic(CommonCharacteristicTests):
    """Test suite for IMD Status characteristic."""

    @pytest.fixture
    def characteristic(self) -> IMDStatusCharacteristic:
        return IMDStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C0C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=IMDStatusData(flags=IMDStatusFlags(0), additional_data=b""),
                description="No flags, no additional data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x13, 0xAA, 0xBB]),
                expected_value=IMDStatusData(
                    flags=IMDStatusFlags.DEVICE_OPERATING | IMDStatusFlags.ALARM_ACTIVE | IMDStatusFlags.BATTERY_LOW,
                    additional_data=b"\xaa\xbb",
                ),
                description="Multiple flags with additional data",
            ),
        ]

    def test_roundtrip(self, characteristic: IMDStatusCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = IMDStatusData(
            flags=IMDStatusFlags.WARNING_ACTIVE | IMDStatusFlags.MAINTENANCE_REQUIRED,
            additional_data=b"\x01\x02\x03",
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original

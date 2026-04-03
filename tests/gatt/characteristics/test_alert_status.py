"""Tests for AlertStatusCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.alert_status import (
    AlertStatusCharacteristic,
    AlertStatusData,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAlertStatusCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> AlertStatusCharacteristic:
        return AlertStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A3F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=AlertStatusData(
                    ringer_state=False,
                    vibrate_state=False,
                    display_alert_status=False,
                ),
                description="All alerts inactive",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x07]),
                expected_value=AlertStatusData(
                    ringer_state=True,
                    vibrate_state=True,
                    display_alert_status=True,
                ),
                description="All alerts active (bits 0-2 set)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05]),
                expected_value=AlertStatusData(
                    ringer_state=True,
                    vibrate_state=False,
                    display_alert_status=True,
                ),
                description="Ringer and display active, vibrate inactive",
            ),
        ]

    def test_reserved_bits_ignored(self, characteristic: AlertStatusCharacteristic) -> None:
        """Test that reserved bits (3-7) are ignored during decoding."""
        data = bytearray([0xFF])  # All bits set including reserved
        result = characteristic.parse_value(data)
        assert result is not None
        assert result.ringer_state is True
        assert result.vibrate_state is True
        assert result.display_alert_status is True

    def test_only_reserved_bits_set(self, characteristic: AlertStatusCharacteristic) -> None:
        """Test data where only reserved bits are set (bits 3-7), defined bits are 0."""
        data = bytearray([0xF8])  # Bits 3-7 set, bits 0-2 clear
        result = characteristic.parse_value(data)
        assert result is not None
        assert result.ringer_state is False
        assert result.vibrate_state is False
        assert result.display_alert_status is False

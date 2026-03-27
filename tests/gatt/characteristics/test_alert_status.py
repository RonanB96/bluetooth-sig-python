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

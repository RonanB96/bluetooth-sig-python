"""Tests for ACSStatusCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.acs_status import (
    ACSStatusCharacteristic,
    ACSStatusData,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestACSStatusCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ACSStatusCharacteristic:
        return ACSStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B2F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x34, 0x12]),
                expected_value=ACSStatusData(
                    security_controls_switch=False,
                    security_established=False,
                    current_restriction_map_id=0x1234,
                ),
                description="No status flags set",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x01, 0x00]),
                expected_value=ACSStatusData(
                    security_controls_switch=True,
                    security_established=False,
                    current_restriction_map_id=0x0001,
                ),
                description="Security controls switch set",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0xFF, 0x00]),
                expected_value=ACSStatusData(
                    security_controls_switch=True,
                    security_established=True,
                    current_restriction_map_id=0x00FF,
                ),
                description="Both status flags set",
            ),
        ]

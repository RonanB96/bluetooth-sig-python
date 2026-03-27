"""Tests for ACSStatusCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.acs_status import (
    ACSHearingAidPresence,
    ACSStatusCharacteristic,
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
                input_data=bytearray([0x00]),
                expected_value=ACSHearingAidPresence.NO_HEARING_AID_PRESENT,
                description="No hearing aid present",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=ACSHearingAidPresence.LEFT_PRESENT,
                description="Left hearing aid present",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03]),
                expected_value=ACSHearingAidPresence.BOTH_PRESENT,
                description="Both hearing aids present",
            ),
        ]

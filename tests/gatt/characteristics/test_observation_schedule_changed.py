"""Tests for ObservationScheduleChangedCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.observation_schedule_changed import (
    ObservationScheduleChangedCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestObservationScheduleChangedCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ObservationScheduleChangedCharacteristic:
        return ObservationScheduleChangedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BF1"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b""),
                expected_value=True,
                description="empty payload indicates schedule changed",
            ),
            CharacteristicTestData(
                input_data=bytearray(b""),
                expected_value=True,
                description="another empty payload also returns True",
            ),
        ]

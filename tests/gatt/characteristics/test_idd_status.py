"""Tests for IDDStatusCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.idd_status import (
    IDDOperationalState,
    IDDStatusCharacteristic,
    IDDStatusData,
    TherapyControlState,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestIDDStatusCharacteristic(CommonCharacteristicTests):
    """Tests for IDDStatusCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> IDDStatusCharacteristic:
        return IDDStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B21"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                # therapy=RUN (0x03), operational=DELIVERING (0x02),
                # reservoir_remaining=5000 (0x1388 LE)
                input_data=bytearray([0x03, 0x02, 0x88, 0x13]),
                expected_value=IDDStatusData(
                    therapy_control_state=TherapyControlState.RUN,
                    operational_state=IDDOperationalState.DELIVERING,
                    reservoir_remaining=5000,
                ),
                description="Running, delivering, 50.00 IU remaining",
            ),
            CharacteristicTestData(
                # therapy=STOP (0x01), operational=STOPPED (0x04),
                # reservoir_remaining=0 (0x0000 LE)
                input_data=bytearray([0x01, 0x04, 0x00, 0x00]),
                expected_value=IDDStatusData(
                    therapy_control_state=TherapyControlState.STOP,
                    operational_state=IDDOperationalState.STOPPED,
                    reservoir_remaining=0,
                ),
                description="Stopped, no reservoir remaining",
            ),
            CharacteristicTestData(
                # therapy=PAUSE (0x02), operational=PAUSED (0x03),
                # reservoir_remaining=10000 (0x2710 LE)
                input_data=bytearray([0x02, 0x03, 0x10, 0x27]),
                expected_value=IDDStatusData(
                    therapy_control_state=TherapyControlState.PAUSE,
                    operational_state=IDDOperationalState.PAUSED,
                    reservoir_remaining=10000,
                ),
                description="Paused, 100.00 IU remaining",
            ),
        ]

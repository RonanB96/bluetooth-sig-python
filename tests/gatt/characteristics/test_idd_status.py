"""Tests for IDDStatusCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.idd_status import (
    IDDOperationalState,
    IDDStatusCharacteristic,
    IDDStatusData,
    IDDStatusFlags,
    TherapyControlState,
)
from bluetooth_sig.gatt.characteristics.utils import IEEE11073Parser
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
        sfloat_100 = list(IEEE11073Parser.encode_sfloat(100.0))
        sfloat_0 = list(IEEE11073Parser.encode_sfloat(0.0))
        return [
            CharacteristicTestData(
                # therapy=RUN (0x55), operational=PREPARING (0x55),
                # reservoir=SFLOAT(100.0), flags=RESERVOIR_ATTACHED (0x01)
                input_data=bytearray([0x55, 0x55] + sfloat_100 + [0x01]),
                expected_value=IDDStatusData(
                    therapy_control_state=TherapyControlState.RUN,
                    operational_state=IDDOperationalState.PREPARING,
                    reservoir_remaining=100.0,
                    flags=IDDStatusFlags.RESERVOIR_ATTACHED,
                ),
                description="Running, preparing, 100.0 remaining, reservoir attached",
            ),
            CharacteristicTestData(
                # therapy=STOP (0x33), operational=WAITING (0x66),
                # reservoir=SFLOAT(0.0), flags=0x00
                input_data=bytearray([0x33, 0x66] + sfloat_0 + [0x00]),
                expected_value=IDDStatusData(
                    therapy_control_state=TherapyControlState.STOP,
                    operational_state=IDDOperationalState.WAITING,
                    reservoir_remaining=0.0,
                    flags=IDDStatusFlags(0),
                ),
                description="Stopped, waiting, no reservoir remaining",
            ),
            CharacteristicTestData(
                # therapy=PAUSE (0x3C), operational=PRIMING (0x5A),
                # reservoir=SFLOAT(100.0), flags=0x00
                input_data=bytearray([0x3C, 0x5A] + sfloat_100 + [0x00]),
                expected_value=IDDStatusData(
                    therapy_control_state=TherapyControlState.PAUSE,
                    operational_state=IDDOperationalState.PRIMING,
                    reservoir_remaining=100.0,
                    flags=IDDStatusFlags(0),
                ),
                description="Paused, priming, 100.0 remaining",
            ),
        ]

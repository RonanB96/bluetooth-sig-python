"""Tests for GeneralActivityInstantaneousDataCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.general_activity_instantaneous_data import (
    GeneralActivityInstantaneousData,
    GeneralActivityInstantaneousDataCharacteristic,
    GeneralActivityInstFlags,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestGeneralActivityInstantaneousDataCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> GeneralActivityInstantaneousDataCharacteristic:
        return GeneralActivityInstantaneousDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B3C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0xE8, 0x03]),
                expected_value=GeneralActivityInstantaneousData(
                    flags=GeneralActivityInstFlags.STEPS_PRESENT,
                    steps=1000,
                ),
                description="Steps only, 1000 steps",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0F, 0xF4, 0x01, 0xC4, 0x09, 0x00, 0x10, 0x0E, 0x00, 0x4B]),
                expected_value=GeneralActivityInstantaneousData(
                    flags=(
                        GeneralActivityInstFlags.STEPS_PRESENT
                        | GeneralActivityInstFlags.DISTANCE_PRESENT
                        | GeneralActivityInstFlags.DURATION_PRESENT
                        | GeneralActivityInstFlags.INTENSITY_PRESENT
                    ),
                    steps=500,
                    distance=2500,
                    duration=3600,
                    intensity=75,
                ),
                description="All fields present",
            ),
        ]

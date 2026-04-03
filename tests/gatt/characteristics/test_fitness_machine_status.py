"""Tests for Fitness Machine Status characteristic (0x2ADA)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.fitness_machine_status import (
    FitnessMachineStatusCharacteristic,
    FitnessMachineStatusData,
    FitnessMachineStatusOpCode,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestFitnessMachineStatusCharacteristic(CommonCharacteristicTests):
    """Test suite for Fitness Machine Status characteristic."""

    @pytest.fixture
    def characteristic(self) -> FitnessMachineStatusCharacteristic:
        return FitnessMachineStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ADA"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=FitnessMachineStatusData(
                    op_code=FitnessMachineStatusOpCode.RESET,
                ),
                description="Reset (no params)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x01]),
                expected_value=FitnessMachineStatusData(
                    op_code=FitnessMachineStatusOpCode.FITNESS_MACHINE_STOPPED_OR_PAUSED_BY_USER,
                    parameter=b"\x01",
                ),
                description="Stopped by user (param=stop)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04]),
                expected_value=FitnessMachineStatusData(
                    op_code=FitnessMachineStatusOpCode.FITNESS_MACHINE_STARTED_OR_RESUMED_BY_USER,
                ),
                description="Started or resumed by user",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF]),
                expected_value=FitnessMachineStatusData(
                    op_code=FitnessMachineStatusOpCode.CONTROL_PERMISSION_LOST,
                ),
                description="Control permission lost",
            ),
        ]

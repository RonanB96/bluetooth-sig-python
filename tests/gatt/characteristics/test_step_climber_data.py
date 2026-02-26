"""Tests for Step Climber Data characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.step_climber_data import (
    StepClimberData,
    StepClimberDataCharacteristic,
    StepClimberDataFlags,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestStepClimberDataCharacteristic(CommonCharacteristicTests):
    """Tests for StepClimberDataCharacteristic."""

    characteristic_cls = StepClimberDataCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return StepClimberDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ACF"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            # Case 1: Flags only — bit 0 set (MORE_DATA), all fields absent
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=StepClimberData(
                    flags=StepClimberDataFlags.MORE_DATA,
                ),
                description="Flags only, no optional fields",
            ),
            # Case 2: Floors + Step Count (bit 0 = 0) + HR (bit 5)
            # Flags = 0x0020, Floors = 8, Step Count = 150, HR = 95
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x20,
                        0x00,  # Flags = 0x0020
                        0x08,
                        0x00,  # Floors = 8
                        0x96,
                        0x00,  # Step Count = 150
                        0x5F,  # HR = 95
                    ]
                ),
                expected_value=StepClimberData(
                    flags=StepClimberDataFlags.HEART_RATE_PRESENT,
                    floors=8,
                    step_count=150,
                    heart_rate=95,
                ),
                description="Floors, step count, and heart rate",
            ),
            # Case 3: All fields present
            # Flags = 0x01FE (bits 1-8 set, bit 0 clear → floors + step count present)
            # Floors=12, Steps=300, Steps/min=40, Avg=35, Elev=50
            # Energy: total=250, /hr=200, /min=3
            # HR=130, MET=6.5 (raw 65), Elapsed=900, Remaining=300
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xFE,
                        0x01,  # Flags = 0x01FE
                        0x0C,
                        0x00,  # Floors = 12
                        0x2C,
                        0x01,  # Step Count = 300
                        0x28,
                        0x00,  # Steps/min = 40
                        0x23,
                        0x00,  # Avg step rate = 35
                        0x32,
                        0x00,  # Pos elevation = 50
                        0xFA,
                        0x00,  # Total energy = 250
                        0xC8,
                        0x00,  # Energy/hr = 200
                        0x03,  # Energy/min = 3
                        0x82,  # HR = 130
                        0x41,  # MET = 65 → 6.5
                        0x84,
                        0x03,  # Elapsed = 900
                        0x2C,
                        0x01,  # Remaining = 300
                    ]
                ),
                expected_value=StepClimberData(
                    flags=StepClimberDataFlags(0x01FE),
                    floors=12,
                    step_count=300,
                    steps_per_minute=40,
                    average_step_rate=35,
                    positive_elevation_gain=50,
                    total_energy=250,
                    energy_per_hour=200,
                    energy_per_minute=3,
                    heart_rate=130,
                    metabolic_equivalent=6.5,
                    elapsed_time=900,
                    remaining_time=300,
                ),
                description="All fields present",
            ),
        ]

    def test_more_data_inverted_logic(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify bit 0 inversion: 0 → Floors + Step Count present, 1 → absent."""
        # Bit 0 = 0: Floors + Step Count present
        data_with = bytearray([0x00, 0x00, 0x03, 0x00, 0x64, 0x00])
        result = characteristic.parse_value(data_with)
        assert result.floors == 3
        assert result.step_count == 100

        # Bit 0 = 1: both absent
        data_without = bytearray([0x01, 0x00])
        result = characteristic.parse_value(data_without)
        assert result.floors is None
        assert result.step_count is None

    def test_dual_field_bit0_gating(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify that bit 0 gates both Floors and Step Count together."""
        # Bit 0 = 0, bit 1 = 1 (steps per minute present)
        # Floors = 2, Step Count = 50, Steps/min = 20
        data = bytearray(
            [
                0x02,
                0x00,  # Flags = 0x0002
                0x02,
                0x00,  # Floors = 2
                0x32,
                0x00,  # Step Count = 50
                0x14,
                0x00,  # Steps/min = 20
            ]
        )
        result = characteristic.parse_value(data)
        assert result.floors == 2
        assert result.step_count == 50
        assert result.steps_per_minute == 20

    def test_metabolic_equivalent_scaling(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify MET field is scaled by 0.1 (raw / 10)."""
        # Flags = 0x0041 (bit 0 + bit 6 → no floors, MET present)
        data = bytearray([0x41, 0x00, 0x50])  # raw MET = 80 → 8.0
        result = characteristic.parse_value(data)
        assert result.metabolic_equivalent == pytest.approx(8.0)

"""Tests for Stair Climber Data characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.stair_climber_data import (
    StairClimberData,
    StairClimberDataCharacteristic,
    StairClimberDataFlags,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestStairClimberDataCharacteristic(CommonCharacteristicTests):
    """Tests for StairClimberDataCharacteristic."""

    characteristic_cls = StairClimberDataCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return StairClimberDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AD0"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            # Case 1: Flags only — bit 0 set (MORE_DATA), all fields absent
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=StairClimberData(
                    flags=StairClimberDataFlags.MORE_DATA,
                ),
                description="Flags only, no optional fields",
            ),
            # Case 2: Floors present (bit 0 = 0) + Steps Per Minute (bit 1)
            # Flags = 0x0002, Floors = 5, Steps/min = 30
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x00, 0x05, 0x00, 0x1E, 0x00]),
                expected_value=StairClimberData(
                    flags=StairClimberDataFlags.STEPS_PER_MINUTE_PRESENT,
                    floors=5,
                    steps_per_minute=30,
                ),
                description="Floors and steps per minute",
            ),
            # Case 3: All fields present
            # Flags = 0x03FE (bits 1-9 set, bit 0 clear → floors present)
            # Floors=10, Steps/min=50, Avg=45, Elev=100, Stride=200
            # Energy: total=500, /hr=300, /min=5
            # HR=120, MET=5.0 (raw 50), Elapsed=1800, Remaining=600
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xFE,
                        0x03,  # Flags = 0x03FE
                        0x0A,
                        0x00,  # Floors = 10
                        0x32,
                        0x00,  # Steps/min = 50
                        0x2D,
                        0x00,  # Avg step rate = 45
                        0x64,
                        0x00,  # Pos elevation = 100
                        0xC8,
                        0x00,  # Stride count = 200
                        0xF4,
                        0x01,  # Total energy = 500
                        0x2C,
                        0x01,  # Energy/hr = 300
                        0x05,  # Energy/min = 5
                        0x78,  # HR = 120
                        0x32,  # MET = 50 → 5.0
                        0x08,
                        0x07,  # Elapsed = 1800
                        0x58,
                        0x02,  # Remaining = 600
                    ]
                ),
                expected_value=StairClimberData(
                    flags=StairClimberDataFlags(0x03FE),
                    floors=10,
                    steps_per_minute=50,
                    average_step_rate=45,
                    positive_elevation_gain=100,
                    stride_count=200,
                    total_energy=500,
                    energy_per_hour=300,
                    energy_per_minute=5,
                    heart_rate=120,
                    metabolic_equivalent=5.0,
                    elapsed_time=1800,
                    remaining_time=600,
                ),
                description="All fields present",
            ),
        ]

    def test_more_data_inverted_logic(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify bit 0 inversion: 0 → Floors present, 1 → absent."""
        # Bit 0 = 0: Floors present
        data_with_floors = bytearray([0x00, 0x00, 0x03, 0x00])
        result = characteristic.parse_value(data_with_floors)
        assert result.floors == 3

        # Bit 0 = 1: Floors absent
        data_without_floors = bytearray([0x01, 0x00])
        result = characteristic.parse_value(data_without_floors)
        assert result.floors is None

    def test_energy_triplet_gated_by_single_bit(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify bit 5 gates all three energy fields together."""
        # Flags = 0x0021 (bit 0 set + bit 5 set → no floors, energy present)
        data = bytearray(
            [
                0x21,
                0x00,  # Flags
                0x64,
                0x00,  # Total energy = 100
                0x32,
                0x00,  # Energy/hr = 50
                0x0A,  # Energy/min = 10
            ]
        )
        result = characteristic.parse_value(data)
        assert result.floors is None
        assert result.total_energy == 100
        assert result.energy_per_hour == 50
        assert result.energy_per_minute == 10

    def test_metabolic_equivalent_scaling(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify MET field is scaled by 0.1 (raw / 10)."""
        # Flags = 0x0081 (bit 0 + bit 7 → no floors, MET present)
        data = bytearray([0x81, 0x00, 0x4B])  # raw MET = 75 → 7.5
        result = characteristic.parse_value(data)
        assert result.metabolic_equivalent == pytest.approx(7.5)

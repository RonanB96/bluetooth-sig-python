"""Test cycling power vector characteristic parsing."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cycling_power_vector import (
    CrankRevolutionData,
    CyclingPowerVectorCharacteristic,
    CyclingPowerVectorData,
    CyclingPowerVectorFlags,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCyclingPowerVectorCharacteristic(CommonCharacteristicTests):
    """Test Cycling Power Vector characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> CyclingPowerVectorCharacteristic:
        return CyclingPowerVectorCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A64"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            # Flags only (no optional fields)
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=CyclingPowerVectorData(
                    flags=CyclingPowerVectorFlags(0),
                    crank_revolution_data=None,
                    first_crank_measurement_angle=None,
                    instantaneous_force_magnitude_array=None,
                    instantaneous_torque_magnitude_array=None,
                    instantaneous_measurement_direction=0,
                ),
                description="Flags only, no optional fields",
            ),
            # Crank revolution data present (bit 0)
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,  # flags: CRANK_REVOLUTION_DATA_PRESENT
                        0xE8,
                        0x03,  # crank revolutions = 1000
                        0x00,
                        0x04,  # crank time = 1024 (1.0s)
                    ]
                ),
                expected_value=CyclingPowerVectorData(
                    flags=CyclingPowerVectorFlags.CRANK_REVOLUTION_DATA_PRESENT,
                    crank_revolution_data=CrankRevolutionData(
                        crank_revolutions=1000,
                        last_crank_event_time=1.0,
                    ),
                    first_crank_measurement_angle=None,
                    instantaneous_force_magnitude_array=None,
                    instantaneous_torque_magnitude_array=None,
                    instantaneous_measurement_direction=0,
                ),
                description="Crank revolution data present",
            ),
            # Crank + angle + force array
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x07,  # flags: CRANK(0x01) + ANGLE(0x02) + FORCE(0x04)
                        0x2A,
                        0x01,  # crank revolutions = 298
                        0x80,
                        0x07,  # crank time = 1920 (1.875s)
                        0xB4,
                        0x00,  # first angle = 180 degrees
                        0x64,
                        0x00,  # force 1 = 100 N
                        0x96,
                        0x00,  # force 2 = 150 N
                    ]
                ),
                expected_value=CyclingPowerVectorData(
                    flags=(
                        CyclingPowerVectorFlags.CRANK_REVOLUTION_DATA_PRESENT
                        | CyclingPowerVectorFlags.FIRST_CRANK_MEASUREMENT_ANGLE_PRESENT
                        | CyclingPowerVectorFlags.INSTANTANEOUS_FORCE_MAGNITUDE_ARRAY_PRESENT
                    ),
                    crank_revolution_data=CrankRevolutionData(
                        crank_revolutions=298,
                        last_crank_event_time=1.875,
                    ),
                    first_crank_measurement_angle=180.0,
                    instantaneous_force_magnitude_array=(100.0, 150.0),
                    instantaneous_torque_magnitude_array=None,
                    instantaneous_measurement_direction=0,
                ),
                description="Crank + angle + force array",
            ),
        ]

    def test_cycling_power_vector_with_torque_array(self) -> None:
        """Test cycling power vector with torque magnitude array."""
        char = CyclingPowerVectorCharacteristic()
        # flags: CRANK(0x01) + ANGLE(0x02) + TORQUE(0x08)
        data = bytearray(
            [
                0x0B,
                0xE8,
                0x03,  # crank revs = 1000
                0x00,
                0x04,  # crank time = 1024 (1.0s)
                0x68,
                0x01,  # angle = 360 degrees
                0xA0,
                0x00,  # torque 1 = 160 -> 5.0 Nm
                0xC0,
                0x00,  # torque 2 = 192 -> 6.0 Nm
            ]
        )
        result = char.parse_value(data)
        assert result.instantaneous_torque_magnitude_array == (5.0, 6.0)
        assert result.crank_revolution_data is not None
        assert result.first_crank_measurement_angle == 360.0

    def test_cycling_power_vector_direction(self) -> None:
        """Test instantaneous measurement direction from bits 4-5."""
        char = CyclingPowerVectorCharacteristic()
        # flags = 0x10 -> direction bits 4-5 = 01 -> direction = 1
        data = bytearray([0x10])
        result = char.parse_value(data)
        assert result.instantaneous_measurement_direction == 1

    def test_cycling_power_vector_flags_only(self) -> None:
        """Test minimum valid data (just flags byte)."""
        char = CyclingPowerVectorCharacteristic()
        data = bytearray([0x00])
        result = char.parse_value(data)
        assert result.crank_revolution_data is None
        assert result.first_crank_measurement_angle is None
        assert result.instantaneous_force_magnitude_array is None
        assert result.instantaneous_torque_magnitude_array is None

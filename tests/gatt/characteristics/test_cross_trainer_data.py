"""Tests for Cross Trainer Data characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.cross_trainer_data import (
    CrossTrainerData,
    CrossTrainerDataCharacteristic,
    CrossTrainerDataFlags,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCrossTrainerDataCharacteristic(CommonCharacteristicTests):
    """Tests for CrossTrainerDataCharacteristic."""

    characteristic_cls = CrossTrainerDataCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return CrossTrainerDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ACE"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            # Case 1: Flags only -- bit 0 set (MORE_DATA), all fields absent
            # 24-bit flags = 0x000001 (3 bytes)
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00]),
                expected_value=CrossTrainerData(
                    flags=CrossTrainerDataFlags.MORE_DATA,
                ),
                description="Flags only, no optional fields (24-bit)",
            ),
            # Case 2: Speed (bit 0=0) + HR (bit 11) + backward direction (bit 15)
            # Flags = 0x008800: bit 11=1 (HR), bit 15=1 (backward)
            # Speed raw=1500 -> 15.00 km/h, HR=160
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,
                        0x88,
                        0x00,  # Flags = 0x008800
                        0xDC,
                        0x05,  # Speed raw = 1500 -> 15.00
                        0xA0,  # HR = 160
                    ]
                ),
                expected_value=CrossTrainerData(
                    flags=CrossTrainerDataFlags.HEART_RATE_PRESENT | CrossTrainerDataFlags.MOVEMENT_DIRECTION_BACKWARD,
                    instantaneous_speed=15.00,
                    heart_rate=160,
                    movement_direction_backward=True,
                ),
                description="Speed + HR + backward direction",
            ),
            # Case 3: Multiple fields - speed, step count, stride, power, energy
            # Flags = 0x00051C: bit 0=0 (speed), bit 2 (distance), bit 3 (steps),
            #   bit 4 (stride), bit 8 (inst power), bit 10 (energy)
            # Speed raw=1000 -> 10.00, Distance=3000,
            # Steps/min=120, Avg step rate=115,
            # Stride raw=500 -> 50.0, Power=200,
            # Energy: total=300, /hr=400, /min=7
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x1C,
                        0x05,
                        0x00,  # Flags = 0x00051C
                        0xE8,
                        0x03,  # Speed raw = 1000 -> 10.00
                        0xB8,
                        0x0B,
                        0x00,  # Distance = 3000
                        0x78,
                        0x00,  # Steps/min = 120
                        0x73,
                        0x00,  # Avg step rate = 115
                        0xF4,
                        0x01,  # Stride raw = 500 -> 50.0
                        0xC8,
                        0x00,  # Inst power = 200
                        0x2C,
                        0x01,  # Total energy = 300
                        0x90,
                        0x01,  # Energy/hr = 400
                        0x07,  # Energy/min = 7
                    ]
                ),
                expected_value=CrossTrainerData(
                    flags=CrossTrainerDataFlags(0x00051C),
                    instantaneous_speed=10.00,
                    total_distance=3000,
                    steps_per_minute=120,
                    average_step_rate=115,
                    stride_count=50.0,
                    instantaneous_power=200,
                    total_energy=300,
                    energy_per_hour=400,
                    energy_per_minute=7,
                ),
                description="Speed + distance + steps + stride + power + energy",
            ),
        ]

    def test_24bit_flags_parsed_correctly(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """24-bit flags (3 bytes) are parsed correctly."""
        # Flags = 0x000001 (MORE_DATA), 3 bytes
        data = bytearray([0x01, 0x00, 0x00])
        result = characteristic.parse_value(data)
        assert result.flags == CrossTrainerDataFlags.MORE_DATA
        assert result.instantaneous_speed is None

    def test_inverted_bit0_speed_present_when_bit_clear(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Bit 0 = 0 means Instantaneous Speed IS present (inverted)."""
        # Flags = 0x000000: bit 0 clear -> speed present
        data = bytearray([0x00, 0x00, 0x00, 0xE8, 0x03])  # Speed raw=1000 -> 10.00
        result = characteristic.parse_value(data)
        assert result.instantaneous_speed == 10.00

    def test_inverted_bit0_speed_absent_when_bit_set(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Bit 0 = 1 means Instantaneous Speed IS absent (inverted)."""
        data = bytearray([0x01, 0x00, 0x00])
        result = characteristic.parse_value(data)
        assert result.instantaneous_speed is None

    def test_movement_direction_forward(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Bit 15 = 0 means forward movement."""
        data = bytearray([0x01, 0x00, 0x00])  # No bit 15
        result = characteristic.parse_value(data)
        assert result.movement_direction_backward is False

    def test_movement_direction_backward(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Bit 15 = 1 means backward movement (semantic flag)."""
        # Flags = 0x008001: bit 0=1 (no speed), bit 15=1 (backward)
        data = bytearray([0x01, 0x80, 0x00])
        result = characteristic.parse_value(data)
        assert result.movement_direction_backward is True
        assert result.instantaneous_speed is None

    def test_step_count_dual_field_gating(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Bit 3 gates both Steps Per Minute and Average Step Rate (4 bytes)."""
        # Flags = 0x000009: bit 0=1 (no speed), bit 3=1 (step count)
        data = bytearray(
            [
                0x09,
                0x00,
                0x00,  # Flags
                0x64,
                0x00,  # Steps/min = 100
                0x5A,
                0x00,  # Avg step rate = 90
            ]
        )
        result = characteristic.parse_value(data)
        assert result.steps_per_minute == 100
        assert result.average_step_rate == 90

    def test_stride_count_tenth_resolution(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Stride count uses d=-1 scaling (raw/10)."""
        # Flags = 0x000011: bit 0=1 (no speed), bit 4=1 (stride count)
        data = bytearray(
            [
                0x11,
                0x00,
                0x00,  # Flags
                0xFB,
                0x00,  # Stride raw = 251 -> 25.1
            ]
        )
        result = characteristic.parse_value(data)
        assert result.stride_count == pytest.approx(25.1)

    def test_elevation_gain_raw_metres(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Cross trainer elevation gain is raw metres (no d=-1 scaling)."""
        # Flags = 0x000021: bit 0=1 (no speed), bit 5=1 (elevation gain)
        data = bytearray(
            [
                0x21,
                0x00,
                0x00,  # Flags
                0xC8,
                0x00,  # Pos elev = 200 m
                0x64,
                0x00,  # Neg elev = 100 m
            ]
        )
        result = characteristic.parse_value(data)
        assert result.positive_elevation_gain == 200
        assert result.negative_elevation_gain == 100

    def test_inclination_and_ramp_tenth_resolution(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Inclination and ramp use d=-1 scaling (raw/10)."""
        # Flags = 0x000041: bit 0=1 (no speed), bit 6=1 (incl+ramp)
        data = bytearray(
            [
                0x41,
                0x00,
                0x00,  # Flags
                0xEC,
                0xFF,  # Incl raw = -20 -> -2.0%
                0x1E,
                0x00,  # Ramp raw = 30 -> 3.0 deg
            ]
        )
        result = characteristic.parse_value(data)
        assert result.inclination == -2.0
        assert result.ramp_setting == 3.0

    def test_resistance_level_times_ten_scaling(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Resistance level uses d=1 scaling (raw * 10)."""
        # Flags = 0x000081: bit 0=1 (no speed), bit 7=1 (resistance)
        data = bytearray(
            [
                0x81,
                0x00,
                0x00,  # Flags
                0x05,  # Resistance raw = 5 -> 50.0
            ]
        )
        result = characteristic.parse_value(data)
        assert result.resistance_level == 50.0

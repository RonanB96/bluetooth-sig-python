"""Tests for Treadmill Data characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.treadmill_data import (
    TreadmillData,
    TreadmillDataCharacteristic,
    TreadmillDataFlags,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTreadmillDataCharacteristic(CommonCharacteristicTests):
    """Tests for TreadmillDataCharacteristic."""

    characteristic_cls = TreadmillDataCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return TreadmillDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ACD"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            # Case 1: Flags only -- bit 0 set (MORE_DATA), all fields absent
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=TreadmillData(
                    flags=TreadmillDataFlags.MORE_DATA,
                ),
                description="Flags only, no optional fields",
            ),
            # Case 2: Speed (bit 0 = 0) + Average Speed (bit 1) + HR (bit 8)
            # Flags = 0x0102, Speed raw=1250 -> 12.50 km/h,
            # Avg Speed raw=1200 -> 12.00 km/h, HR=155
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x02,
                        0x01,  # Flags = 0x0102
                        0xE2,
                        0x04,  # Inst speed raw = 1250 -> 12.50
                        0xB0,
                        0x04,  # Avg speed raw = 1200 -> 12.00
                        0x9B,  # HR = 155
                    ]
                ),
                expected_value=TreadmillData(
                    flags=TreadmillDataFlags.AVERAGE_SPEED_PRESENT | TreadmillDataFlags.HEART_RATE_PRESENT,
                    instantaneous_speed=12.50,
                    average_speed=12.00,
                    heart_rate=155,
                ),
                description="Speed + Average Speed + Heart Rate",
            ),
            # Case 3: All fields present (comprehensive)
            # Flags = 0x1FFE (bits 1-12 set, bit 0=0 for speed present)
            # Speed raw=800 -> 8.00, Avg Speed raw=750 -> 7.50
            # Distance = 5000 (uint24), Incl raw=-50 -> -5.0%, Ramp raw=30 -> 3.0 deg
            # Pos elev raw=100 -> 10.0m, Neg elev raw=50 -> 5.0m
            # Inst pace = 300, Avg pace = 310
            # Energy: total=500, /hr=600, /min=10
            # HR=140, MET raw=85 -> 8.5, Elapsed=1800, Remaining=600
            # Force=-100, Power=250
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xFE,
                        0x1F,  # Flags = 0x1FFE
                        0x20,
                        0x03,  # Speed raw = 800 -> 8.00
                        0xEE,
                        0x02,  # Avg speed raw = 750 -> 7.50
                        0x88,
                        0x13,
                        0x00,  # Distance = 5000
                        0xCE,
                        0xFF,  # Incl raw = -50 -> -5.0
                        0x1E,
                        0x00,  # Ramp raw = 30 -> 3.0
                        0x64,
                        0x00,  # Pos elev raw = 100 -> 10.0
                        0x32,
                        0x00,  # Neg elev raw = 50 -> 5.0
                        0x2C,
                        0x01,  # Inst pace = 300
                        0x36,
                        0x01,  # Avg pace = 310
                        0xF4,
                        0x01,  # Total energy = 500
                        0x58,
                        0x02,  # Energy/hr = 600
                        0x0A,  # Energy/min = 10
                        0x8C,  # HR = 140
                        0x55,  # MET raw = 85 -> 8.5
                        0x08,
                        0x07,  # Elapsed = 1800
                        0x58,
                        0x02,  # Remaining = 600
                        0x9C,
                        0xFF,  # Force = -100 (signed)
                        0xFA,
                        0x00,  # Power = 250 (signed)
                    ]
                ),
                expected_value=TreadmillData(
                    flags=TreadmillDataFlags(0x1FFE),
                    instantaneous_speed=8.00,
                    average_speed=7.50,
                    total_distance=5000,
                    inclination=-5.0,
                    ramp_angle_setting=3.0,
                    positive_elevation_gain=10.0,
                    negative_elevation_gain=5.0,
                    instantaneous_pace=300,
                    average_pace=310,
                    total_energy=500,
                    energy_per_hour=600,
                    energy_per_minute=10,
                    heart_rate=140,
                    metabolic_equivalent=8.5,
                    elapsed_time=1800,
                    remaining_time=600,
                    force_on_belt=-100,
                    power_output=250,
                ),
                description="All fields present",
            ),
        ]

    def test_inverted_bit0_speed_present_when_bit_clear(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Bit 0 = 0 means Instantaneous Speed IS present (inverted)."""
        # Flags = 0x0000: bit 0 clear -> speed present
        data = bytearray([0x00, 0x00, 0xE8, 0x03])  # Speed raw = 1000 -> 10.00
        result = characteristic.parse_value(data)
        assert result.instantaneous_speed == 10.00

    def test_inverted_bit0_speed_absent_when_bit_set(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Bit 0 = 1 means Instantaneous Speed IS absent (inverted)."""
        data = bytearray([0x01, 0x00])  # Flags = 0x0001: MORE_DATA set
        result = characteristic.parse_value(data)
        assert result.instantaneous_speed is None

    def test_inclination_and_ramp_dual_field_gating(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Bit 3 gates both Inclination and Ramp Angle (4 bytes)."""
        # Flags = 0x0009: bit 0=1 (no speed), bit 3=1 (incl+ramp)
        # Incl raw=25 -> 2.5%, Ramp raw=-15 -> -1.5 deg
        data = bytearray(
            [
                0x09,
                0x00,  # Flags
                0x19,
                0x00,  # Incl raw = 25 -> 2.5
                0xF1,
                0xFF,  # Ramp raw = -15 -> -1.5
            ]
        )
        result = characteristic.parse_value(data)
        assert result.instantaneous_speed is None
        assert result.inclination == 2.5
        assert result.ramp_angle_setting == -1.5

    def test_elevation_gain_dual_field_gating(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Bit 4 gates both Positive and Negative Elevation Gain (4 bytes)."""
        # Flags = 0x0011: bit 0=1 (no speed), bit 4=1 (elevation)
        data = bytearray(
            [
                0x11,
                0x00,  # Flags
                0xC8,
                0x00,  # Pos elev raw = 200 -> 20.0 m
                0x96,
                0x00,  # Neg elev raw = 150 -> 15.0 m
            ]
        )
        result = characteristic.parse_value(data)
        assert result.positive_elevation_gain == 20.0
        assert result.negative_elevation_gain == 15.0

    def test_force_and_power_dual_field_gating(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Bit 12 gates both Force On Belt and Power Output (4 bytes, signed)."""
        # Flags = 0x1001: bit 0=1 (no speed), bit 12=1 (force+power)
        # Force = -200 (sint16), Power = 350 (sint16)
        data = bytearray(
            [
                0x01,
                0x10,  # Flags = 0x1001
                0x38,
                0xFF,  # Force = -200
                0x5E,
                0x01,  # Power = 350
            ]
        )
        result = characteristic.parse_value(data)
        assert result.force_on_belt == -200
        assert result.power_output == 350

    def test_speed_hundredths_scaling(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Speed fields use d=-2 scaling (raw/100 km/h)."""
        # Flags = 0x0002: bit 0=0 (speed present), bit 1=1 (avg speed)
        # Inst speed raw=1234 -> 12.34, Avg speed raw=1111 -> 11.11
        data = bytearray(
            [
                0x02,
                0x00,  # Flags
                0xD2,
                0x04,  # Inst speed raw = 1234
                0x57,
                0x04,  # Avg speed raw = 1111
            ]
        )
        result = characteristic.parse_value(data)
        assert result.instantaneous_speed == 12.34
        assert result.average_speed == 11.11

    def test_negative_inclination(
        self,
        characteristic: BaseCharacteristic[Any],
    ) -> None:
        """Inclination can be negative (downhill)."""
        # Flags = 0x0009: bit 0=1 (no speed), bit 3=1 (incl+ramp)
        # Incl raw=-100 -> -10.0%, Ramp raw=0 -> 0.0 deg
        data = bytearray(
            [
                0x09,
                0x00,  # Flags
                0x9C,
                0xFF,  # Incl raw = -100 -> -10.0
                0x00,
                0x00,  # Ramp raw = 0 -> 0.0
            ]
        )
        result = characteristic.parse_value(data)
        assert result.inclination == -10.0
        assert result.ramp_angle_setting == 0.0

"""Tests for Rower Data characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.rower_data import (
    RowerData,
    RowerDataCharacteristic,
    RowerDataFlags,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRowerDataCharacteristic(CommonCharacteristicTests):
    """Tests for RowerDataCharacteristic."""

    characteristic_cls = RowerDataCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return RowerDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AD1"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            # Case 1: Flags only -- bit 0 set (MORE_DATA), all fields absent
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=RowerData(
                    flags=RowerDataFlags.MORE_DATA,
                ),
                description="Flags only, no optional fields",
            ),
            # Case 2: Stroke Rate + Stroke Count (bit 0 = 0) + HR (bit 9)
            # Flags = 0x0200, Stroke Rate raw=60 -> 30.0, Count=150, HR=140
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,
                        0x02,  # Flags = 0x0200
                        0x3C,  # Stroke rate raw = 60 -> 30.0
                        0x96,
                        0x00,  # Stroke count = 150
                        0x8C,  # HR = 140
                    ]
                ),
                expected_value=RowerData(
                    flags=RowerDataFlags.HEART_RATE_PRESENT,
                    stroke_rate=30.0,
                    stroke_count=150,
                    heart_rate=140,
                ),
                description="Stroke rate, count, and heart rate",
            ),
            # Case 3: All fields present
            # Flags = 0x1FFE (bits 1-12 set, bit 0 clear -> stroke fields present)
            # Stroke Rate raw=50 -> 25.0, Count=200
            # Avg Stroke Rate raw=48 -> 24.0
            # Total Distance=5000 (uint24), Inst Pace=120, Avg Pace=125
            # Inst Power=250 (sint16), Avg Power=240 (sint16)
            # Resistance raw=5 -> 50.0
            # Energy: total=500, /hr=300, /min=5
            # HR=130, MET raw=65 -> 6.5, Elapsed=3600, Remaining=1200
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xFE,
                        0x1F,  # Flags = 0x1FFE
                        0x32,  # Stroke rate raw = 50 -> 25.0
                        0xC8,
                        0x00,  # Stroke count = 200
                        0x30,  # Avg stroke rate raw = 48 -> 24.0
                        0x88,
                        0x13,
                        0x00,  # Total distance = 5000 (uint24)
                        0x78,
                        0x00,  # Inst pace = 120
                        0x7D,
                        0x00,  # Avg pace = 125
                        0xFA,
                        0x00,  # Inst power = 250 (sint16)
                        0xF0,
                        0x00,  # Avg power = 240 (sint16)
                        0x05,  # Resistance raw = 5 -> 50.0
                        0xF4,
                        0x01,  # Total energy = 500
                        0x2C,
                        0x01,  # Energy/hr = 300
                        0x05,  # Energy/min = 5
                        0x82,  # HR = 130
                        0x41,  # MET raw = 65 -> 6.5
                        0x10,
                        0x0E,  # Elapsed = 3600
                        0xB0,
                        0x04,  # Remaining = 1200
                    ]
                ),
                expected_value=RowerData(
                    flags=RowerDataFlags(0x1FFE),
                    stroke_rate=25.0,
                    stroke_count=200,
                    average_stroke_rate=24.0,
                    total_distance=5000,
                    instantaneous_pace=120,
                    average_pace=125,
                    instantaneous_power=250,
                    average_power=240,
                    resistance_level=50.0,
                    total_energy=500,
                    energy_per_hour=300,
                    energy_per_minute=5,
                    heart_rate=130,
                    metabolic_equivalent=6.5,
                    elapsed_time=3600,
                    remaining_time=1200,
                ),
                description="All fields present",
            ),
        ]

    def test_more_data_inverted_logic(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify bit 0 inversion: 0 -> Stroke Rate+Count present, 1 -> absent."""
        # Bit 0 = 0: Stroke Rate + Count present
        data_with_strokes = bytearray([0x00, 0x00, 0x3C, 0x0A, 0x00])
        result = characteristic.parse_value(data_with_strokes)
        assert result.stroke_rate == 30.0
        assert result.stroke_count == 10

        # Bit 0 = 1: Stroke fields absent
        data_without_strokes = bytearray([0x01, 0x00])
        result = characteristic.parse_value(data_without_strokes)
        assert result.stroke_rate is None
        assert result.stroke_count is None

    def test_dual_field_bit0_gating(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify bit 0 gates both Stroke Rate and Stroke Count together."""
        # Bit 0 = 0 + bit 2 (total distance): stroke fields + distance
        data = bytearray(
            [
                0x04,
                0x00,  # Flags = 0x0004 (bit 2 set, bit 0 clear)
                0x14,  # Stroke rate raw = 20 -> 10.0
                0x64,
                0x00,  # Stroke count = 100
                0xE8,
                0x03,
                0x00,  # Total distance = 1000 (uint24)
            ]
        )
        result = characteristic.parse_value(data)
        assert result.stroke_rate == 10.0
        assert result.stroke_count == 100
        assert result.total_distance == 1000

    def test_stroke_rate_half_resolution(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify stroke rate uses 0.5 resolution (raw / 2)."""
        # Bit 0 = 0: stroke fields present, raw stroke rate = 45 -> 22.5
        data = bytearray([0x00, 0x00, 0x2D, 0x00, 0x00])
        result = characteristic.parse_value(data)
        assert result.stroke_rate == pytest.approx(22.5)

    def test_signed_power_fields(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify power fields are signed (can be negative)."""
        # Flags = 0x0061 (bit 0 + bit 5 + bit 6 -> no strokes, inst+avg power)
        # Inst power = -100 (0xFF9C as signed), Avg power = -50 (0xFFCE)
        data = bytearray(
            [
                0x61,
                0x00,  # Flags
                0x9C,
                0xFF,  # Inst power = -100
                0xCE,
                0xFF,  # Avg power = -50
            ]
        )
        result = characteristic.parse_value(data)
        assert result.instantaneous_power == -100
        assert result.average_power == -50

    def test_resistance_level_scaling(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify resistance level is scaled by 10 (raw * 10)."""
        # Flags = 0x0081 (bit 0 + bit 7 -> no strokes, resistance present)
        data = bytearray([0x81, 0x00, 0x08])  # raw = 8 -> 80.0
        result = characteristic.parse_value(data)
        assert result.resistance_level == pytest.approx(80.0)

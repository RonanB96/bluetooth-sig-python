"""Tests for Indoor Bike Data characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.indoor_bike_data import (
    IndoorBikeData,
    IndoorBikeDataCharacteristic,
    IndoorBikeDataFlags,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIndoorBikeDataCharacteristic(CommonCharacteristicTests):
    """Tests for IndoorBikeDataCharacteristic."""

    characteristic_cls = IndoorBikeDataCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return IndoorBikeDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AD2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            # Case 1: Flags only -- bit 0 set (MORE_DATA), all fields absent
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=IndoorBikeData(
                    flags=IndoorBikeDataFlags.MORE_DATA,
                ),
                description="Flags only, no optional fields",
            ),
            # Case 2: Speed present (bit 0 = 0) + Cadence (bit 2) + HR (bit 9)
            # Flags = 0x0204, Speed raw=2500 -> 25.00 km/h,
            # Cadence raw=180 -> 90.0 rpm, HR=155
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x04,
                        0x02,  # Flags = 0x0204
                        0xC4,
                        0x09,  # Speed raw = 2500 -> 25.00
                        0xB4,
                        0x00,  # Cadence raw = 180 -> 90.0
                        0x9B,  # HR = 155
                    ]
                ),
                expected_value=IndoorBikeData(
                    flags=IndoorBikeDataFlags(0x0204),
                    instantaneous_speed=25.0,
                    instantaneous_cadence=90.0,
                    heart_rate=155,
                ),
                description="Speed, cadence, and heart rate",
            ),
            # Case 3: All fields present
            # Flags = 0x1FFE (bits 1-12 set, bit 0 clear -> speed present)
            # Speed raw=3000 -> 30.00, Avg Speed raw=2800 -> 28.00
            # Cadence raw=160 -> 80.0, Avg Cadence raw=150 -> 75.0
            # Distance=10000 (uint24), Resistance raw=7 -> 70.0
            # Inst Power=200 (sint16), Avg Power=185 (sint16)
            # Energy: total=800, /hr=400, /min=7
            # HR=145, MET raw=80 -> 8.0, Elapsed=5400, Remaining=600
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xFE,
                        0x1F,  # Flags = 0x1FFE
                        0xB8,
                        0x0B,  # Speed raw = 3000 -> 30.00
                        0xF0,
                        0x0A,  # Avg speed raw = 2800 -> 28.00
                        0xA0,
                        0x00,  # Cadence raw = 160 -> 80.0
                        0x96,
                        0x00,  # Avg cadence raw = 150 -> 75.0
                        0x10,
                        0x27,
                        0x00,  # Distance = 10000 (uint24)
                        0x07,  # Resistance raw = 7 -> 70.0
                        0xC8,
                        0x00,  # Inst power = 200 (sint16)
                        0xB9,
                        0x00,  # Avg power = 185 (sint16)
                        0x20,
                        0x03,  # Total energy = 800
                        0x90,
                        0x01,  # Energy/hr = 400
                        0x07,  # Energy/min = 7
                        0x91,  # HR = 145
                        0x50,  # MET raw = 80 -> 8.0
                        0x18,
                        0x15,  # Elapsed = 5400
                        0x58,
                        0x02,  # Remaining = 600
                    ]
                ),
                expected_value=IndoorBikeData(
                    flags=IndoorBikeDataFlags(0x1FFE),
                    instantaneous_speed=30.0,
                    average_speed=28.0,
                    instantaneous_cadence=80.0,
                    average_cadence=75.0,
                    total_distance=10000,
                    resistance_level=70.0,
                    instantaneous_power=200,
                    average_power=185,
                    total_energy=800,
                    energy_per_hour=400,
                    energy_per_minute=7,
                    heart_rate=145,
                    metabolic_equivalent=8.0,
                    elapsed_time=5400,
                    remaining_time=600,
                ),
                description="All fields present",
            ),
        ]

    def test_more_data_inverted_logic(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify bit 0 inversion: 0 -> Speed present, 1 -> absent."""
        # Bit 0 = 0: Speed present (raw=1500 -> 15.00 km/h)
        data_with_speed = bytearray([0x00, 0x00, 0xDC, 0x05])
        result = characteristic.parse_value(data_with_speed)
        assert result.instantaneous_speed == pytest.approx(15.0)

        # Bit 0 = 1: Speed absent
        data_without_speed = bytearray([0x01, 0x00])
        result = characteristic.parse_value(data_without_speed)
        assert result.instantaneous_speed is None

    def test_speed_hundredth_resolution(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify speed uses 0.01 km/h resolution (raw / 100)."""
        # Bit 0 = 0: speed present, raw = 1234 -> 12.34 km/h
        data = bytearray([0x00, 0x00, 0xD2, 0x04])
        result = characteristic.parse_value(data)
        assert result.instantaneous_speed == pytest.approx(12.34)

    def test_cadence_half_resolution(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify cadence uses 0.5 rpm resolution (raw / 2)."""
        # Flags = 0x0005 (bit 0 set + bit 2 -> no speed, cadence present)
        # Cadence raw = 145 -> 72.5 rpm
        data = bytearray([0x05, 0x00, 0x91, 0x00])
        result = characteristic.parse_value(data)
        assert result.instantaneous_cadence == pytest.approx(72.5)

    def test_signed_power_fields(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify power fields are signed (can be negative)."""
        # Flags = 0x00C1 (bit 0 + bit 6 + bit 7 -> no speed, inst+avg power)
        # Inst power = -50 (0xFFCE), Avg power = -25 (0xFFE7)
        data = bytearray(
            [
                0xC1,
                0x00,  # Flags
                0xCE,
                0xFF,  # Inst power = -50
                0xE7,
                0xFF,  # Avg power = -25
            ]
        )
        result = characteristic.parse_value(data)
        assert result.instantaneous_power == -50
        assert result.average_power == -25

    def test_resistance_level_scaling(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify resistance level is scaled by 10 (raw * 10)."""
        # Flags = 0x0021 (bit 0 + bit 5 -> no speed, resistance present)
        data = bytearray([0x21, 0x00, 0x0C])  # raw = 12 -> 120.0
        result = characteristic.parse_value(data)
        assert result.resistance_level == pytest.approx(120.0)

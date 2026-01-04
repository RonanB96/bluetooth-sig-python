"""Test cycling power measurement characteristic parsing."""

from __future__ import annotations

import struct

import pytest

from bluetooth_sig.gatt.characteristics.cycling_power_measurement import (
    CyclingPowerMeasurementCharacteristic,
    CyclingPowerMeasurementData,
    CyclingPowerMeasurementFlags,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCyclingPowerMeasurementCharacteristic(CommonCharacteristicTests):
    """Test Cycling Power Measurement characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> CyclingPowerMeasurementCharacteristic:
        """Provide Cycling Power Measurement characteristic for testing."""
        return CyclingPowerMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Cycling Power Measurement characteristic."""
        return "2A63"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid cycling power measurement test data covering various flag combinations and features."""
        return [
            # Test 1: Basic measurement (no optional fields)
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0xFA, 0x00]),  # flags=0, power=250W
                expected_value=CyclingPowerMeasurementData(
                    flags=CyclingPowerMeasurementFlags(0),
                    instantaneous_power=250,
                    pedal_power_balance=None,
                    accumulated_energy=None,
                    cumulative_wheel_revolutions=None,
                    last_wheel_event_time=None,
                    cumulative_crank_revolutions=None,
                    last_crank_event_time=None,
                ),
                description="Basic 250W power measurement",
            ),
            # Test 2: With pedal power balance
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x2C, 0x01, 0x64]),  # flags=1, power=300W, balance=50%
                expected_value=CyclingPowerMeasurementData(
                    flags=CyclingPowerMeasurementFlags.PEDAL_POWER_BALANCE_PRESENT,
                    instantaneous_power=300,
                    pedal_power_balance=50.0,  # 100 * 0.5% resolution
                    accumulated_energy=None,
                    cumulative_wheel_revolutions=None,
                    last_wheel_event_time=None,
                    cumulative_crank_revolutions=None,
                    last_crank_event_time=None,
                ),
                description="300W with 50% pedal power balance",
            ),
            # Test 3: With accumulated energy
            CharacteristicTestData(
                input_data=bytearray([0x08, 0x00, 0x40, 0x01, 0x0A, 0x00]),  # flags=8, power=320W, energy=10kJ
                expected_value=CyclingPowerMeasurementData(
                    flags=CyclingPowerMeasurementFlags.ACCUMULATED_ENERGY_PRESENT,
                    instantaneous_power=320,
                    pedal_power_balance=None,
                    accumulated_energy=10,
                    cumulative_wheel_revolutions=None,
                    last_wheel_event_time=None,
                    cumulative_crank_revolutions=None,
                    last_crank_event_time=None,
                ),
                description="320W with 10kJ accumulated energy",
            ),
            # Test 4: With wheel revolution data
            CharacteristicTestData(
                input_data=bytearray(
                    [0x10, 0x00, 0x4B, 0x01, 0x39, 0x30, 0x00, 0x00, 0x00, 0x08]
                ),  # flags=16, power=331W, wheel_revs=12345, time=2048 (2048/2048 = 1s)
                expected_value=CyclingPowerMeasurementData(
                    flags=CyclingPowerMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT,
                    instantaneous_power=331,
                    pedal_power_balance=None,
                    accumulated_energy=None,
                    cumulative_wheel_revolutions=12345,
                    last_wheel_event_time=1.0,  # 2048 / 2048 = 1.0 second
                    cumulative_crank_revolutions=None,
                    last_crank_event_time=None,
                ),
                description="331W with wheel revolution data (12345 revs, 1s)",
            ),
            # Test 5: With crank revolution data
            CharacteristicTestData(
                input_data=bytearray(
                    [0x20, 0x00, 0x70, 0x01, 0x90, 0x01, 0x00, 0x04]
                ),  # flags=32, power=368W, crank_revs=400, time=1s
                expected_value=CyclingPowerMeasurementData(
                    flags=CyclingPowerMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT,
                    instantaneous_power=368,
                    pedal_power_balance=None,
                    accumulated_energy=None,
                    cumulative_wheel_revolutions=None,
                    last_wheel_event_time=None,
                    cumulative_crank_revolutions=400,
                    last_crank_event_time=1.0,  # 1024 / 1024 = 1.0 second
                ),
                description="368W with crank revolution data (400 revs, 1s)",
            ),
            # Test 6: Complex measurement with multiple optional fields
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x39,
                        0x00,
                        0x94,
                        0x01,
                        0x6E,
                        0x15,
                        0x00,
                        0x39,
                        0x30,
                        0x00,
                        0x00,
                        0x00,
                        0x10,
                        0x90,
                        0x01,
                        0x00,
                        0x08,
                    ]
                ),  # multiple flags
                expected_value=CyclingPowerMeasurementData(
                    flags=(
                        CyclingPowerMeasurementFlags.PEDAL_POWER_BALANCE_PRESENT
                        | CyclingPowerMeasurementFlags.ACCUMULATED_ENERGY_PRESENT
                        | CyclingPowerMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT
                        | CyclingPowerMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT
                    ),
                    instantaneous_power=404,
                    pedal_power_balance=55.0,  # 110 * 0.5% = 55%
                    accumulated_energy=21,  # 21kJ
                    cumulative_wheel_revolutions=12345,
                    last_wheel_event_time=2.0,  # 4096 / 2048 = 2.0 seconds
                    cumulative_crank_revolutions=400,
                    last_crank_event_time=2.0,  # 2048 / 1024 = 2.0 seconds
                ),
                description="Complex 404W measurement with all optional fields",
            ),
        ]

    def test_cycling_power_measurement_basic_parsing(
        self, characteristic: CyclingPowerMeasurementCharacteristic
    ) -> None:
        """Test basic cycling power measurement parsing."""
        # Test minimum required data: Flags(2) + Power(2)
        flags = 0x0000  # No optional fields
        power = 250  # 250 watts
        test_data = struct.pack("<Hh", flags, power)
        result = characteristic.parse_value(bytearray(test_data))
        assert result.value is not None

        assert result.value.flags == 0
        assert result.value.instantaneous_power == 250

    def test_cycling_power_measurement_with_pedal_balance(
        self, characteristic: CyclingPowerMeasurementCharacteristic
    ) -> None:
        """Test cycling power measurement with pedal power balance."""
        # Test with pedal power balance
        flags = 0x0001  # Pedal power balance present
        power = 300
        balance = 100  # 50% (100 * 0.5%)
        test_data = struct.pack("<HhB", flags, power, balance)
        result = characteristic.parse_value(bytearray(test_data))
        assert result.value is not None

        assert result.value.flags == 1
        assert result.value.instantaneous_power == 300
        assert result.value.pedal_power_balance == 50.0

    def test_cycling_power_measurement_with_wheel_data(
        self, characteristic: CyclingPowerMeasurementCharacteristic
    ) -> None:
        """Test cycling power measurement with wheel revolution data."""
        # Test with wheel revolution data
        flags = 0x0010  # Wheel revolution data present
        power = 320
        wheel_revs = 12345
        wheel_time = 2048  # 1 second in 1/2048 units
        test_data = struct.pack("<HhIH", flags, power, wheel_revs, wheel_time)
        result = characteristic.parse_value(bytearray(test_data))
        assert result.value is not None

        assert result.value.flags == 16
        assert result.value.instantaneous_power == 320
        assert result.value.cumulative_wheel_revolutions == 12345
        assert result.value.last_wheel_event_time == 1.0  # 2048 / 2048 = 1.0 second

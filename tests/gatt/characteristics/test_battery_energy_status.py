"""Tests for Battery Energy Status characteristic (0x2BF0)."""

from __future__ import annotations

import math
from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.battery_energy_status import (
    BatteryEnergyStatus,
    BatteryEnergyStatusCharacteristic,
    BatteryEnergyStatusFlags,
)
from bluetooth_sig.gatt.characteristics.utils import IEEE11073Parser
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


def _sfloat_bytes(value: float) -> list[int]:
    """Encode a float to SFLOAT and return as list of ints."""
    return list(IEEE11073Parser.encode_sfloat(value))


class TestBatteryEnergyStatusCharacteristic(CommonCharacteristicTests):
    """Test Battery Energy Status characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Battery Energy Status characteristic for testing."""
        return BatteryEnergyStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Battery Energy Status characteristic."""
        return "2BF0"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid battery energy status test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x3F,  # flags: all 6 fields present
                        *_sfloat_bytes(5.0),  # external_source_power: 5W
                        *_sfloat_bytes(4.0),  # present_voltage: 4V
                        *_sfloat_bytes(10.0),  # available_energy: 10kWh
                        *_sfloat_bytes(20.0),  # available_battery_capacity: 20kWh
                        *_sfloat_bytes(3.0),  # charge_rate: 3W
                        *_sfloat_bytes(8.0),  # available_energy_at_last_charge: 8kWh
                    ]
                ),
                expected_value=BatteryEnergyStatus(
                    flags=BatteryEnergyStatusFlags(0x3F),
                    external_source_power=5.0,
                    present_voltage=4.0,
                    available_energy=10.0,
                    available_battery_capacity=20.0,
                    charge_rate=3.0,
                    available_energy_at_last_charge=8.0,
                ),
                description="All fields present",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00]),  # flags only, no fields
                expected_value=BatteryEnergyStatus(
                    flags=BatteryEnergyStatusFlags(0x00),
                ),
                description="Flags only, no optional fields",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [0x02, *_sfloat_bytes(4.0)]  # flags + present_voltage: 4V
                ),
                expected_value=BatteryEnergyStatus(
                    flags=BatteryEnergyStatusFlags(0x02),
                    present_voltage=4.0,
                ),
                description="Voltage only",
            ),
        ]

    def test_single_field_external_power(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify external source power only."""
        data = bytearray([0x01, *_sfloat_bytes(100.0)])
        result = characteristic.parse_value(data)
        assert result.external_source_power == 100.0
        assert result.present_voltage is None
        assert result.available_energy is None

    def test_charge_rate_negative(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify negative charge rate (discharging)."""
        data = bytearray([0x10, *_sfloat_bytes(-2.0)])
        result = characteristic.parse_value(data)
        assert result.charge_rate == -2.0

    def test_roundtrip_all_fields(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify encode/decode roundtrip with all fields."""
        original = BatteryEnergyStatus(
            flags=BatteryEnergyStatusFlags(0x3F),
            external_source_power=5.0,
            present_voltage=4.0,
            available_energy=10.0,
            available_battery_capacity=20.0,
            charge_rate=3.0,
            available_energy_at_last_charge=8.0,
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original

    def test_roundtrip_partial_fields(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify encode/decode roundtrip with subset of fields."""
        original = BatteryEnergyStatus(
            flags=BatteryEnergyStatusFlags(0x0A),
            present_voltage=4.0,
            available_battery_capacity=20.0,
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original

    def test_nan_sfloat(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify NaN SFLOAT value is handled."""
        data = bytearray([0x02, *IEEE11073Parser.encode_sfloat(float("nan"))])
        result = characteristic.parse_value(data)
        assert math.isnan(result.present_voltage)

    def test_too_short_data(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify that empty data raises error."""
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([]))

"""Tests for Battery Health Information characteristic (0x2BEB)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.battery_health_information import (
    BatteryHealthInformation,
    BatteryHealthInformationCharacteristic,
    BatteryHealthInformationFlags,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestBatteryHealthInformationCharacteristic(CommonCharacteristicTests):
    """Test Battery Health Information characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Battery Health Information characteristic for testing."""
        return BatteryHealthInformationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Battery Health Information characteristic."""
        return "2BEB"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid battery health information test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x03,  # flags: both fields present
                        0xE8,
                        0x03,  # cycle_count_designed_lifetime: 1000
                        0xEC,  # min_temp: -20 C
                        0x3C,  # max_temp: 60 C
                    ]
                ),
                expected_value=BatteryHealthInformation(
                    flags=BatteryHealthInformationFlags(0x03),
                    cycle_count_designed_lifetime=1000,
                    min_designed_operating_temperature=-20,
                    max_designed_operating_temperature=60,
                ),
                description="All fields present",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00]),  # flags only
                expected_value=BatteryHealthInformation(
                    flags=BatteryHealthInformationFlags(0x00),
                ),
                description="Flags only, no optional fields",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,  # flags: cycle count only
                        0xD0,
                        0x07,  # cycle_count_designed_lifetime: 2000
                    ]
                ),
                expected_value=BatteryHealthInformation(
                    flags=BatteryHealthInformationFlags(0x01),
                    cycle_count_designed_lifetime=2000,
                ),
                description="Cycle count only",
            ),
        ]

    def test_bit1_gates_two_temperature_fields(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify bit 1 gates both min and max temperature simultaneously."""
        data = bytearray(
            [
                0x02,  # flags: temperature range present
                0xF6,  # min_temp: -10 C
                0x37,  # max_temp: 55 C
            ]
        )
        result = characteristic.parse_value(data)
        assert result.cycle_count_designed_lifetime is None
        assert result.min_designed_operating_temperature == -10
        assert result.max_designed_operating_temperature == 55

    def test_temperature_sentinels(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify temperature sentinel values."""
        data = bytearray(
            [
                0x02,  # flags: temperature range present
                0x80,  # min_temp: -128 (means "<-127")
                0x7F,  # max_temp: 127 (means ">126")
            ]
        )
        result = characteristic.parse_value(data)
        assert result.min_designed_operating_temperature == -128
        assert result.max_designed_operating_temperature == 127

    def test_roundtrip_all_fields(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify encode/decode roundtrip with all fields."""
        original = BatteryHealthInformation(
            flags=BatteryHealthInformationFlags(0x03),
            cycle_count_designed_lifetime=500,
            min_designed_operating_temperature=-10,
            max_designed_operating_temperature=45,
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original

    def test_validation_cycle_count(self) -> None:
        """Verify cycle count range validation."""
        with pytest.raises(ValueError, match="Cycle count designed lifetime"):
            BatteryHealthInformation(
                flags=BatteryHealthInformationFlags(0x01),
                cycle_count_designed_lifetime=-1,
            )

    def test_too_short_data(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify that empty data raises error."""
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([]))

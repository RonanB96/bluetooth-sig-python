"""Tests for Battery Health Status characteristic (0x2BEA)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.battery_health_status import (
    BatteryHealthStatus,
    BatteryHealthStatusCharacteristic,
    BatteryHealthStatusFlags,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestBatteryHealthStatusCharacteristic(CommonCharacteristicTests):
    """Test Battery Health Status characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Battery Health Status characteristic for testing."""
        return BatteryHealthStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Battery Health Status characteristic."""
        return "2BEA"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid battery health status test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x0F,  # flags: all 4 fields present
                        0x50,  # health_summary: 80%
                        0xE8,
                        0x03,  # cycle_count: 1000
                        0x19,  # current_temperature: 25 C
                        0x05,
                        0x00,  # deep_discharge_count: 5
                    ]
                ),
                expected_value=BatteryHealthStatus(
                    flags=BatteryHealthStatusFlags(0x0F),
                    battery_health_summary=80,
                    cycle_count=1000,
                    current_temperature=25,
                    deep_discharge_count=5,
                ),
                description="All fields present",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00]),  # flags only, no optional fields
                expected_value=BatteryHealthStatus(
                    flags=BatteryHealthStatusFlags(0x00),
                ),
                description="Flags only, no optional fields",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,  # flags: only health summary
                        0x64,  # health_summary: 100%
                    ]
                ),
                expected_value=BatteryHealthStatus(
                    flags=BatteryHealthStatusFlags(0x01),
                    battery_health_summary=100,
                ),
                description="Only health summary present",
            ),
        ]

    def test_temperature_sentinel_greater_than_126(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify sint8 0x7F (127) decodes as >126 sentinel."""
        data = bytearray(
            [
                0x04,  # flags: temperature present
                0x7F,  # temperature: 127 (means ">126")
            ]
        )
        result = characteristic.parse_value(data)
        assert result.current_temperature == 127

    def test_temperature_sentinel_less_than_minus_127(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify sint8 0x80 (-128) decodes as <-127 sentinel."""
        data = bytearray(
            [
                0x04,  # flags: temperature present
                0x80,  # temperature: -128 (means "<-127")
            ]
        )
        result = characteristic.parse_value(data)
        assert result.current_temperature == -128

    def test_negative_temperature(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify negative temperature values decode correctly."""
        data = bytearray(
            [
                0x04,  # flags: temperature present
                0xF6,  # temperature: -10 C (signed: 0xF6 = 246 unsigned = -10 signed)
            ]
        )
        result = characteristic.parse_value(data)
        assert result.current_temperature == -10

    def test_cycle_count_only(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify cycle count only field present."""
        data = bytearray(
            [
                0x02,  # flags: cycle count present
                0xFF,
                0xFF,  # cycle_count: 65535 (max uint16)
            ]
        )
        result = characteristic.parse_value(data)
        assert result.battery_health_summary is None
        assert result.cycle_count == 65535
        assert result.current_temperature is None
        assert result.deep_discharge_count is None

    def test_deep_discharge_count_only(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify deep discharge count only field present."""
        data = bytearray(
            [
                0x08,  # flags: deep discharge present
                0x0A,
                0x00,  # deep_discharge_count: 10
            ]
        )
        result = characteristic.parse_value(data)
        assert result.deep_discharge_count == 10

    def test_health_summary_validation(self) -> None:
        """Verify health summary must be 0-100."""
        with pytest.raises(ValueError, match="Battery health summary must be 0-100"):
            BatteryHealthStatus(
                flags=BatteryHealthStatusFlags(0x01),
                battery_health_summary=101,
            )

    def test_roundtrip_all_fields(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify encode/decode roundtrip with all fields."""
        original = BatteryHealthStatus(
            flags=BatteryHealthStatusFlags(0x0F),
            battery_health_summary=75,
            cycle_count=500,
            current_temperature=-5,
            deep_discharge_count=3,
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original

    def test_too_short_data(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify that empty data raises error."""
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([]))

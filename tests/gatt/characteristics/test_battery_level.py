"""Tests for Battery Level characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBatteryLevelCharacteristic(CommonCharacteristicTests):
    """Test suite for Battery Level characteristic.

    Inherits behavioral tests from CommonCharacteristicTests.
    Only adds battery-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> BatteryLevelCharacteristic:
        """Return a Battery Level characteristic instance."""
        return BatteryLevelCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Battery Level characteristic."""
        return "2A19"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData:
        """Return valid test data for battery level (75%)."""
        return CharacteristicTestData(input_data=bytearray([75]), expected_value=75, description="75% battery level")

    # === Battery-Specific Tests ===
    @pytest.mark.parametrize(
        "battery_level",
        [
            0,  # Empty
            1,  # 1%
            25,  # Quarter
            50,  # Half
            75,  # Three quarters
            99,  # Almost full
            100,  # Full
        ],
    )
    def test_battery_level_various_values(self, characteristic: BatteryLevelCharacteristic, battery_level: int) -> None:
        """Test battery level with various valid values."""
        data = bytearray([battery_level])
        result = characteristic.decode_value(data)
        assert result == battery_level

    def test_battery_level_boundary_values(self, characteristic: BatteryLevelCharacteristic) -> None:
        """Test battery level boundary values (0% and 100%)."""
        # Test 0% battery
        result = characteristic.decode_value(bytearray([0]))
        assert result == 0

        # Test 100% battery
        result = characteristic.decode_value(bytearray([100]))
        assert result == 100

    def test_battery_level_out_of_range_validation(self, characteristic: BatteryLevelCharacteristic) -> None:
        """Test that values > 100% are rejected."""
        result = characteristic.parse_value(bytearray([101]))
        assert not result.parse_success
        assert "range" in result.error_message.lower()

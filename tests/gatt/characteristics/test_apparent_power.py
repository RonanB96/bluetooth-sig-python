"""Tests for Apparent Power characteristic (0x2B80)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.apparent_power import ApparentPowerCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestApparentPowerCharacteristic(CommonCharacteristicTests):
    """Test Apparent Power characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        """Provide Apparent Power characteristic for testing."""
        return ApparentPowerCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Apparent Power characteristic."""
        return "2B80"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid apparent power test data covering various powers and edge cases."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]), expected_value=0.0, description="0 VA (no power)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x00]), expected_value=1.0, description="1.0 VA (one VA)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFD, 0xFF, 0xFF]), expected_value=1677721.3, description="Maximum power"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00]),
                expected_value=0.1,
                description="0.1 VA (precision test)",
            ),
        ]

    # === Apparent Power-Specific Tests ===
    def test_apparent_power_precision_and_boundaries(self, characteristic: BaseCharacteristic) -> None:
        """Test apparent power precision and boundary values."""
        # Test zero power
        result = characteristic.decode_value(bytearray([0x00, 0x00, 0x00]))
        assert result == 0.0

        # Test positive power (500.5 VA)
        result = characteristic.decode_value(bytearray([0xF9, 0x0F, 0x01]))  # 5005 = 500.5 VA
        assert abs(result - 500.5) < 0.001

        # Test maximum power
        result = characteristic.decode_value(bytearray([0xFD, 0xFF, 0xFF]))  # 16777213 = 1677721.3 VA
        assert abs(result - 1677721.3) < 0.001

    def test_apparent_power_special_values(self, characteristic: BaseCharacteristic) -> None:
        """Test special values for apparent power."""
        # Test "value is not valid" (0xFFFFFE)
        result = characteristic.decode_value(bytearray([0xFE, 0xFF, 0xFF]))
        assert result is None

        # Test "value is not known" (0xFFFFFF)
        result = characteristic.decode_value(bytearray([0xFF, 0xFF, 0xFF]))
        assert result is None

    def test_apparent_power_extreme_values(self, characteristic: BaseCharacteristic) -> None:
        """Test extreme apparent power values within valid range."""
        # Test maximum positive value (just below special values)
        max_data = bytearray([0xFD, 0xFF, 0xFF])  # 16777213 = 1677721.3 VA
        result = characteristic.decode_value(max_data)
        assert abs(result - 1677721.3) < 0.001

        # Test minimum positive value
        min_data = bytearray([0x01, 0x00, 0x00])  # 1 = 0.1 VA
        result = characteristic.decode_value(min_data)
        assert abs(result - 0.1) < 0.001

    def test_apparent_power_encoding_accuracy(self, characteristic: ApparentPowerCharacteristic) -> None:
        """Test encoding produces correct byte sequences."""
        # Test encoding common powers
        assert characteristic.encode_value(0.0) == bytearray([0x00, 0x00, 0x00])
        assert characteristic.encode_value(1.0) == bytearray([0xE8, 0x03, 0x00])
        assert characteristic.encode_value(500.5) == bytearray([0xF9, 0x0F, 0x01])

    def test_encode_value(self, characteristic: ApparentPowerCharacteristic) -> None:
        """Test encoding apparent power values."""
        # Test encoding positive power
        encoded = characteristic.encode_value(500.5)
        assert encoded == bytearray([0xF9, 0x0F, 0x01])

        # Test encoding zero
        encoded = characteristic.encode_value(0.0)
        assert encoded == bytearray([0x00, 0x00, 0x00])

        # Test encoding small power
        encoded = characteristic.encode_value(0.1)
        assert encoded == bytearray([0x01, 0x00, 0x00])

    def test_characteristic_metadata(self, characteristic: ApparentPowerCharacteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Apparent Power"
        assert characteristic.unit == "VA"
        assert characteristic.uuid == "2B80"

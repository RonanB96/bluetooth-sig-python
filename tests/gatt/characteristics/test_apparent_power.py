"""Tests for Apparent Power characteristic (0x2B80)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.apparent_power import ApparentPowerCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestApparentPowerCharacteristic(CommonCharacteristicTests):
    """Test Apparent Power characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Apparent Power characteristic for testing."""
        return ApparentPowerCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Apparent Power characteristic."""
        return "2B8A"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid apparent power test data covering various powers and edge cases."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]), expected_value=0.0, description="0 VA (no power)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0A, 0x00, 0x00]), expected_value=1.0, description="1.0 VA (one VA)"
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
    def test_apparent_power_precision_and_boundaries(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test apparent power precision and boundary values."""
        # Test zero power
        result = characteristic.parse_value(bytearray([0x00, 0x00, 0x00]))
        assert result is not None
        assert result == 0.0

        # Test positive power (500.5 VA)
        result = characteristic.parse_value(bytearray([0x8D, 0x13, 0x00]))  # 5005 = 500.5 VA
        assert result is not None
        assert abs(result - 500.5) < 0.001

        # Test maximum power
        result = characteristic.parse_value(bytearray([0xFD, 0xFF, 0xFF]))  # 16777213 = 1677721.3 VA
        assert result is not None
        assert abs(result - 1677721.3) < 0.001

    def test_apparent_power_special_values(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test special values for apparent power."""
        from bluetooth_sig.gatt.exceptions import SpecialValueDetectedError

        # Test "value is not valid" (0xFFFFFE)
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(bytearray([0xFE, 0xFF, 0xFF]))
        assert exc_info.value.special_value.meaning == "value is not valid"

        # Test "value is not known" (0xFFFFFF)
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(bytearray([0xFF, 0xFF, 0xFF]))
        assert exc_info.value.special_value.meaning == "value is not known"

    def test_apparent_power_extreme_values(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test extreme apparent power values within valid range."""
        # Test maximum positive value (just below special values)
        max_data = bytearray([0xFD, 0xFF, 0xFF])  # 16777213 = 1677721.3 VA
        result = characteristic.parse_value(max_data)
        assert result is not None
        assert abs(result - 1677721.3) < 0.001

        # Test minimum positive value
        min_data = bytearray([0x01, 0x00, 0x00])  # 1 = 0.1 VA
        result = characteristic.parse_value(min_data)
        assert result is not None
        assert abs(result - 0.1) < 0.001

    def test_apparent_power_encoding_accuracy(self, characteristic: ApparentPowerCharacteristic) -> None:
        """Test encoding produces correct byte sequences."""
        # Test encoding common powers
        assert characteristic.build_value(0.0) == bytearray([0x00, 0x00, 0x00])
        assert characteristic.build_value(1.0) == bytearray([0x0A, 0x00, 0x00])
        assert characteristic.build_value(500.5) == bytearray([0x8D, 0x13, 0x00])

    def test_encode_value(self, characteristic: ApparentPowerCharacteristic) -> None:
        """Test encoding apparent power values."""
        # Test encoding positive power
        encoded = characteristic.build_value(500.5)
        assert encoded == bytearray([0x8D, 0x13, 0x00])

        # Test encoding zero
        encoded = characteristic.build_value(0.0)
        assert encoded == bytearray([0x00, 0x00, 0x00])

        # Test encoding small power
        encoded = characteristic.build_value(0.1)
        assert encoded == bytearray([0x01, 0x00, 0x00])

    def test_characteristic_metadata(self, characteristic: ApparentPowerCharacteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Apparent Power"
        assert characteristic.unit == "VA"
        assert characteristic.uuid == "2B8A"

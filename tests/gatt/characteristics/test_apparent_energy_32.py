"""Tests for Apparent Energy 32 characteristic (0x2B83)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.apparent_energy_32 import ApparentEnergy32Characteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestApparentEnergy32Characteristic(CommonCharacteristicTests):
    """Test Apparent Energy 32 characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Apparent Energy 32 characteristic for testing."""
        return ApparentEnergy32Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Apparent Energy 32 characteristic."""
        return "2B89"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid apparent energy 32 test data covering various energies and edge cases."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]), expected_value=0.0, description="0 kVAh (no energy)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x00, 0x00]), expected_value=1.0, description="1.0 kVAh (one kVAh)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFD, 0xFF, 0xFF, 0xFF]), expected_value=4294967.293, description="Maximum energy"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00]),
                expected_value=0.001,
                description="0.001 kVAh (precision test)",
            ),
        ]

    # === Apparent Energy 32-Specific Tests ===
    def test_apparent_energy_32_precision_and_boundaries(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test apparent energy 32 precision and boundary values."""
        # Test zero energy
        result = characteristic.parse_value(bytearray([0x00, 0x00, 0x00, 0x00]))
        assert result.value == 0.0

        # Test positive energy (100.5 kVAh)
        result = characteristic.parse_value(bytearray([0x94, 0x88, 0x01, 0x00]))  # 100500 = 100.5 kVAh
        assert result.value is not None
        assert abs(result.value - 100.5) < 0.001

        # Test maximum energy
        result = characteristic.parse_value(bytearray([0xFD, 0xFF, 0xFF, 0xFF]))  # 4294967293 = 4294967.293 kVAh
        assert result.value is not None
        assert abs(result.value - 4294967.293) < 0.001

    def test_apparent_energy_32_special_values(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test special values for apparent energy 32."""
        # Test "value is not valid" (0xFFFFFFFE)
        result = characteristic.parse_value(bytearray([0xFE, 0xFF, 0xFF, 0xFF]))
        assert result.value is None

        # Test "value is not known" (0xFFFFFFFF)
        result = characteristic.parse_value(bytearray([0xFF, 0xFF, 0xFF, 0xFF]))
        assert result.value is None

    def test_apparent_energy_32_extreme_values(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test extreme apparent energy 32 values within valid range."""
        # Test maximum positive value (just below special values)
        max_data = bytearray([0xFD, 0xFF, 0xFF, 0xFF])  # 4294967293 = 4294967.293 kVAh
        result = characteristic.parse_value(max_data)
        assert result.value is not None
        assert abs(result.value - 4294967.293) < 0.001

        # Test minimum positive value
        min_data = bytearray([0x01, 0x00, 0x00, 0x00])  # 1 = 0.001 kVAh
        result = characteristic.parse_value(min_data)
        assert result.value is not None
        assert abs(result.value - 0.001) < 0.001

    def test_apparent_energy_32_encoding_accuracy(self, characteristic: ApparentEnergy32Characteristic) -> None:
        """Test encoding produces correct byte sequences."""
        # Test encoding common energies
        assert characteristic.build_value(0.0) == bytearray([0x00, 0x00, 0x00, 0x00])
        assert characteristic.build_value(1.0) == bytearray([0xE8, 0x03, 0x00, 0x00])
        assert characteristic.build_value(100.5) == bytearray([0x94, 0x88, 0x01, 0x00])

    def test_encode_value(self, characteristic: ApparentEnergy32Characteristic) -> None:
        """Test encoding apparent energy 32 values."""
        # Test encoding positive energy
        encoded = characteristic.build_value(100.5)
        assert encoded == bytearray([0x94, 0x88, 0x01, 0x00])

        # Test encoding zero
        encoded = characteristic.build_value(0.0)
        assert encoded == bytearray([0x00, 0x00, 0x00, 0x00])

        # Test encoding small energy
        encoded = characteristic.build_value(0.001)
        assert encoded == bytearray([0x01, 0x00, 0x00, 0x00])

    def test_characteristic_metadata(self, characteristic: ApparentEnergy32Characteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Apparent Energy 32"
        assert characteristic.unit == "kVAh"
        assert characteristic.uuid == "2B89"

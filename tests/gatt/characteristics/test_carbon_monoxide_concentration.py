"""Tests for Carbon Monoxide Concentration characteristic (0x2BD5)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import CarbonMonoxideConcentrationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCarbonMonoxideConcentrationCharacteristic(CommonCharacteristicTests):
    """Test suite for Carbon Monoxide Concentration characteristic."""

    @pytest.fixture
    def characteristic(self) -> CarbonMonoxideConcentrationCharacteristic:
        """Return a Carbon Monoxide Concentration characteristic instance."""
        return CarbonMonoxideConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Carbon Monoxide Concentration characteristic."""
        return "2BD0"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for carbon monoxide concentration."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x80]), expected_value=0.0, description="Zero concentration"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x20]), expected_value=1.0e-6, description="Low concentration"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x30]), expected_value=1.0e-5, description="Medium concentration"
            ),
        ]

    def test_zero_concentration(self) -> None:
        """Test zero CO concentration."""
        char = CarbonMonoxideConcentrationCharacteristic()
        result = char.parse_value(bytearray([0x00, 0x80]))
        assert result == 0.0

    def test_typical_concentration(self) -> None:
        """Test typical CO concentration value."""
        char = CarbonMonoxideConcentrationCharacteristic()
        result = char.parse_value(bytearray([0x64, 0x00]))
        assert result == pytest.approx(1.0e-6, abs=1e-9)

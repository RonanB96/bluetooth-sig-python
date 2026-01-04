"""Tests for Carbon Monoxide Concentration characteristic (0x2BD5)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import CarbonMonoxideConcentrationCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
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
                input_data=bytearray([0x64, 0x00]), expected_value=1.0e-6, description="Low concentration"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xC8, 0x01]), expected_value=4.56e-6, description="Medium concentration"
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

    def test_round_trip(
        self,
        characteristic: BaseCharacteristic[Any],
        valid_test_data: CharacteristicTestData | list[CharacteristicTestData],
    ) -> None:
        """Test round trip with value comparison (SFLOAT has precision limits)."""
        test_cases = valid_test_data if isinstance(valid_test_data, list) else [valid_test_data]

        for i, test_case in enumerate(test_cases):
            case_desc = f"Test case {i + 1} ({test_case.description})"
            # Decode the input
            parsed = characteristic.parse_value(test_case.input_data)
            # Re-encode the parsed value
            encoded = characteristic.build_value(parsed)
            # Decode again and check the value matches
            re_decoded = characteristic.parse_value(encoded)
            assert re_decoded == pytest.approx(parsed, rel=0.1), (
                f"{case_desc}: Value changed during round trip"
            )

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = CarbonMonoxideConcentrationCharacteristic()
        for value in [0.0, 1.0, 10.0, 100.0]:
            encoded = char.build_value(value)
            decoded = char.parse_value(encoded)
            assert decoded == pytest.approx(value, rel=0.01)

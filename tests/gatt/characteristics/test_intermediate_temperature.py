"""Tests for Intermediate Temperature characteristic (0x2A1E)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import IntermediateTemperatureCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIntermediateTemperatureCharacteristic(CommonCharacteristicTests):
    """Test suite for Intermediate Temperature characteristic."""

    @pytest.fixture
    def characteristic(self) -> IntermediateTemperatureCharacteristic:
        """Return an Intermediate Temperature characteristic instance."""
        return IntermediateTemperatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Intermediate Temperature characteristic."""
        return "2A1E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for intermediate temperature."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0xFE, 0x8F]),
                expected_value=pytest.approx(-2.0, abs=0.01),
                description="Below freezing",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0B, 0x80]),
                expected_value=pytest.approx(11.0, abs=0.1),
                description="Room temperature",
            ),
        ]

    def test_freezing_temperature(self) -> None:
        """Test freezing point temperature."""
        char = IntermediateTemperatureCharacteristic()
        result = char.parse_value(bytearray([0x00, 0x80]))
        assert result.value == pytest.approx(0.0)

    def test_body_temperature(self) -> None:
        """Test typical body temperature."""
        char = IntermediateTemperatureCharacteristic()
        result = char.parse_value(bytearray([0x25, 0x80]))
        assert result.value == pytest.approx(37.0, abs=0.1)

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve temperature values."""
        char = IntermediateTemperatureCharacteristic()
        for temp in [-2.0, 0.0, 20.0, 37.0]:
            encoded = char.build_value(temp)
            decoded = char.parse_value(encoded)
            assert decoded.value == pytest.approx(temp, abs=0.1)

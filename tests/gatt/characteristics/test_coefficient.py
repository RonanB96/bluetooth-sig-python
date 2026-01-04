"""Tests for Coefficient characteristic (0x2AE8)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import CoefficientCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCoefficientCharacteristic(CommonCharacteristicTests):
    """Test suite for Coefficient characteristic."""

    @pytest.fixture
    def characteristic(self) -> CoefficientCharacteristic:
        """Return a Coefficient characteristic instance."""
        return CoefficientCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Coefficient characteristic."""
        return "2AE8"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for coefficient."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]), expected_value=0.0, description="Zero coefficient"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x80, 0x3F]), expected_value=1.0, description="One coefficient"
            ),
        ]

    def test_zero_coefficient(self) -> None:
        """Test zero coefficient value."""
        char = CoefficientCharacteristic()
        result = char.parse_value(bytearray([0x00, 0x00, 0x00, 0x00]))
        assert result.value == 0.0

    def test_maximum_coefficient(self) -> None:
        """Test maximum coefficient value."""
        char = CoefficientCharacteristic()
        result = char.parse_value(bytearray([0xFF, 0xFF, 0x7F, 0x7F]))
        assert result.value == pytest.approx(3.4028234663852886e38, rel=1e-5)

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = CoefficientCharacteristic()
        for value in [0.0, 1.0, 2.5, -1.5, 100.0]:
            encoded = char.build_value(value)
            decoded = char.parse_value(encoded)
            assert decoded.value == pytest.approx(value)

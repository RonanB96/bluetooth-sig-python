"""Test Uncertainty characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import UncertaintyCharacteristic
from bluetooth_sig.gatt.exceptions import InsufficientDataError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestUncertaintyCharacteristic(CommonCharacteristicTests):
    """Test Uncertainty characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> UncertaintyCharacteristic:
        """Provide Uncertainty characteristic for testing."""
        return UncertaintyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Uncertainty characteristic."""
        return "2AB4"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid Uncertainty test data."""
        return [
            CharacteristicTestData(input_data=bytearray([0x69]), expected_value=10.5, description="10.5 m uncertainty"),
            CharacteristicTestData(
                input_data=bytearray([0x00]), expected_value=0.0, description="Perfect accuracy (0.0 m)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF]), expected_value=25.5, description="Maximum uncertainty (25.5 m)"
            ),
        ]

    def test_uncertainty_parsing(self, characteristic: UncertaintyCharacteristic) -> None:
        """Test Uncertainty characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "m"
        assert characteristic.value_type.value == "float"

        # Test normal parsing
        test_data = bytearray([0x69])  # 105 = 10.5m
        parsed = characteristic.decode_value(test_data)
        assert parsed == 10.5

    def test_uncertainty_error_handling(self, characteristic: UncertaintyCharacteristic) -> None:
        """Test Uncertainty error handling."""
        # Test insufficient data
        with pytest.raises(InsufficientDataError, match="need 1 bytes, got 0"):
            characteristic.decode_value(bytearray())

    def test_uncertainty_boundary_values(self, characteristic: UncertaintyCharacteristic) -> None:
        """Test Uncertainty boundary values."""
        # Minimum
        data_min = bytearray([0x00])
        result = characteristic.decode_value(data_min)
        assert result == 0.0

        # Maximum (255 * 0.1 = 25.5m)
        data_max = bytearray([0xFF])
        result = characteristic.decode_value(data_max)
        assert result == 25.5

    def test_uncertainty_round_trip(self, characteristic: UncertaintyCharacteristic) -> None:
        """Test encode/decode round trip."""
        test_value = 12.3
        encoded = characteristic.encode_value(test_value)
        decoded = characteristic.decode_value(encoded)
        assert decoded == test_value

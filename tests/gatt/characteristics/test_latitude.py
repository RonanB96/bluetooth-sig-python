"""Tests for Latitude characteristic (0x2AAE)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.latitude import LatitudeCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLatitudeCharacteristic(CommonCharacteristicTests):
    """Test suite for Latitude characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Tests latitude coordinate parsing and validation.
    """

    @pytest.fixture
    def characteristic(self) -> LatitudeCharacteristic:
        """Return a Latitude characteristic instance."""
        return LatitudeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Latitude characteristic."""
        return "2AAE"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for latitude values."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]), expected_value=0.0, description="Equator (0.0 degrees)"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x00\xe9\xa4\x35"), expected_value=90.0, description="North Pole (90.0 degrees)"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x00\x17[\xca"), expected_value=-90.0, description="South Pole (-90.0 degrees)"
            ),
        ]

    def test_latitude_range_validation(self, characteristic: LatitudeCharacteristic) -> None:
        """Test that latitude values outside [-90, 90] are rejected."""
        # Test values outside valid range
        invalid_values = [-90.1, 90.1, -100.0, 100.0]

        for invalid_lat in invalid_values:
            with pytest.raises(ValueError, match="out of range"):
                characteristic.encode_value(invalid_lat)

    def test_latitude_precision(self, characteristic: LatitudeCharacteristic) -> None:
        """Test that latitude encoding/decoding preserves precision."""
        test_values = [45.1234567, -33.9876543, 0.0000001, -0.0000001]

        for expected_lat in test_values:
            encoded = characteristic.encode_value(expected_lat)
            decoded = characteristic.decode_value(encoded)
            # Should be accurate to within the resolution (10^-7 degrees)
            precision_error = abs(decoded - expected_lat)
            assert precision_error < characteristic.DEGREE_SCALING_FACTOR, (
                f"Precision lost for {expected_lat}: got {decoded}, error={precision_error}"
            )

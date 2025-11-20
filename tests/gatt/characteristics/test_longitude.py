"""Tests for Longitude characteristic (0x2AAF)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.longitude import LongitudeCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLongitudeCharacteristic(CommonCharacteristicTests):
    """Test suite for Longitude characteristic.

    Inherits behavioral tests from CommonCharacteristicTests.
    Tests longitude coordinate parsing and validation.
    """

    @pytest.fixture
    def characteristic(self) -> LongitudeCharacteristic:
        """Return a Longitude characteristic instance."""
        return LongitudeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Longitude characteristic."""
        return "2AAF"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for longitude values."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=0.0,
                description="Prime Meridian (0.0 degrees)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0xD2, 0x49, 0x6B]),  # 180 * 10^7 = 1800000000 = 0x6B49D200, little endian
                expected_value=180.0,
                description="International Date Line (180.0 degrees)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x2E, 0xB6, 0x94]),  # -180 * 10^7 = -1800000000 = 0x94B62E00, little endian
                expected_value=-180.0,
                description="International Date Line (-180.0 degrees)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xA0, 0x94, 0xE3, 0xD3]),
                # -74.0060 * 10^7 ≈ -740060000 = 0xD3E394A0, little endian
                expected_value=-74.0060,
                description="New York City longitude (-74.0060 degrees)",
            ),
        ]

    def test_longitude_range_validation(self, characteristic: LongitudeCharacteristic) -> None:
        """Test that longitude values outside [-180, 180] are rejected."""
        # Test values outside valid range
        invalid_values = [-180.1, 180.1, -200.0, 200.0]

        for invalid_lon in invalid_values:
            with pytest.raises(ValueError, match="out of range"):
                characteristic.encode_value(invalid_lon)

    def test_longitude_precision(self, characteristic: LongitudeCharacteristic) -> None:
        """Test that longitude encoding/decoding preserves precision."""
        test_values = [120.1234567, -45.9876543, 0.0000001, -0.0000001]

        for expected_lon in test_values:
            encoded = characteristic.encode_value(expected_lon)
            decoded = characteristic.decode_value(encoded)
            # Should be accurate to within the resolution (10^-7 degrees)
            precision_error = abs(decoded - expected_lon)
            assert precision_error < characteristic.DEGREE_SCALING_FACTOR, (
                f"Precision lost for {expected_lon}: got {decoded}, error={precision_error}"
            )

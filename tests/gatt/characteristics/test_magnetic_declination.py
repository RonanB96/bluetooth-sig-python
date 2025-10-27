"""Test magnetic declination characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import MagneticDeclinationCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMagneticDeclinationCharacteristic(CommonCharacteristicTests):
    """Test Magnetic Declination characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> MagneticDeclinationCharacteristic:
        """Provide Magnetic Declination characteristic for testing."""
        return MagneticDeclinationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Magnetic Declination characteristic."""
        return "2A2C"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData:
        """Valid magnetic declination test data."""
        return CharacteristicTestData(
            input_data=bytearray([0x40, 0x46]), expected_value=179.84, description="179.84 degrees magnetic declination"
        )

    def test_magnetic_declination_parsing(self, characteristic: MagneticDeclinationCharacteristic) -> None:
        """Test Magnetic Declination characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "°"
        assert characteristic.value_type.value == "float"

        # Test normal parsing: 18000 (in 0.01 degrees) = 180.00 degrees
        test_data = bytearray([0x40, 0x46])  # 18000 in little endian uint16
        parsed = characteristic.decode_value(test_data)
        assert parsed == 179.84

        # Test boundary values
        zero_data = bytearray([0x00, 0x00])  # 0 degrees
        assert characteristic.decode_value(zero_data) == 0.0

        max_data = bytearray([0x9F, 0x8C])  # 35999 = 359.99 degrees
        assert characteristic.decode_value(max_data) == 359.99

    def test_magnetic_declination_error_handling(self, characteristic: MagneticDeclinationCharacteristic) -> None:
        """Test Magnetic Declination error handling."""
        # Test insufficient data
        with pytest.raises(ValueError, match="Insufficient data"):
            characteristic.decode_value(bytearray([0x12]))

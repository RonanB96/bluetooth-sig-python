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
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid magnetic declination test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0.0,
                description="0.0° (no declination)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x28, 0x23]),
                expected_value=90.0,
                description="90.0° (east)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x40, 0x46]),
                expected_value=179.84,
                description="179.84° (near south)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x78, 0x69]),
                expected_value=270.0,
                description="270.0° (west)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x9F, 0x8C]),
                expected_value=359.99,
                description="359.99° (maximum)",
            ),
        ]

    def test_magnetic_declination_parsing(self, characteristic: MagneticDeclinationCharacteristic) -> None:
        """Test Magnetic Declination characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "°"
        assert characteristic.value_type.value == "float"

        # Test normal parsing: 18000 (in 0.01 degrees) = 180.00 degrees
        test_data = bytearray([0x40, 0x46])  # 18000 in little endian uint16
        parsed = characteristic.parse_value(test_data)
        assert parsed == 179.84

        # Test boundary values
        zero_data = bytearray([0x00, 0x00])  # 0 degrees
        assert characteristic.parse_value(zero_data) == 0.0

        max_data = bytearray([0x9F, 0x8C])  # 35999 = 359.99 degrees
        assert characteristic.parse_value(max_data) == 359.99

    def test_magnetic_declination_error_handling(self, characteristic: MagneticDeclinationCharacteristic) -> None:
        """Test Magnetic Declination error handling."""
        # Test insufficient data - parse_value returns parse_success=False
        result = characteristic.parse_value(bytearray([0x12]))
        assert result.parse_success is False
        assert result.error_message == "Failed to parse int16 data [12]: need 2 bytes, got 1"

    def test_magnetic_declination_cardinal_directions(self, characteristic: MagneticDeclinationCharacteristic) -> None:
        """Test magnetic declination cardinal directions."""
        # North (0°)
        data_north = bytearray([0x00, 0x00])
        assert characteristic.parse_value(data_north) == 0.0

        # East (90°)
        data_east = bytearray([0x28, 0x23])  # 9000 * 0.01 = 90.0
        assert characteristic.parse_value(data_east) == 90.0

        # West (270°)
        data_west = bytearray([0x78, 0x69])  # 27000 * 0.01 = 270.0
        assert characteristic.parse_value(data_west) == 270.0

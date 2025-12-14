"""Test Local North Coordinate characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import LocalNorthCoordinateCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLocalNorthCoordinateCharacteristic(CommonCharacteristicTests):
    """Test Local North Coordinate characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> LocalNorthCoordinateCharacteristic:
        """Provide Local North Coordinate characteristic for testing."""
        return LocalNorthCoordinateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Local North Coordinate characteristic."""
        return "2AB0"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid Local North Coordinate test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0xED, 0x03, 0x00]), expected_value=100.5, description="100.5 m north"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]), expected_value=0.0, description="Origin (0.0 m)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF]), expected_value=-0.1, description="-0.1 m south"
            ),
        ]

    def test_local_north_coordinate_parsing(self, characteristic: LocalNorthCoordinateCharacteristic) -> None:
        """Test Local North Coordinate characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "m"
        assert characteristic.value_type.value == "float"

        # Test normal parsing
        test_data = bytearray([0xED, 0x03, 0x00])  # 1005 = 100.5m
        parsed = characteristic.decode_value(test_data)
        assert parsed == 100.5

    def test_local_north_coordinate_error_handling(self, characteristic: LocalNorthCoordinateCharacteristic) -> None:
        """Test Local North Coordinate error handling."""
        # Test insufficient data
        with pytest.raises(ValueError, match="Insufficient data"):
            characteristic.decode_value(bytearray([0x12, 0x34]))

    def test_local_north_coordinate_boundary_values(self, characteristic: LocalNorthCoordinateCharacteristic) -> None:
        """Test Local North Coordinate boundary values."""
        # Maximum positive (8388607 * 0.1 = 838860.7m)
        data_max = bytearray([0xFF, 0xFF, 0x7F])
        result = characteristic.decode_value(data_max)
        assert abs(result - 838860.7) < 0.1

        # Maximum negative (-8388608 * 0.1 = -838860.8m)
        data_min = bytearray([0x00, 0x00, 0x80])
        result = characteristic.decode_value(data_min)
        assert abs(result - (-838860.8)) < 0.1

    def test_local_north_coordinate_round_trip(self, characteristic: LocalNorthCoordinateCharacteristic) -> None:
        """Test encode/decode round trip."""
        test_value = 123.4
        encoded = characteristic.encode_value(test_value)
        decoded = characteristic.decode_value(encoded)
        assert decoded == test_value

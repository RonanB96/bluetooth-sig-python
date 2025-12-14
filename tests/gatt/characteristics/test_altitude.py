"""Test Altitude characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AltitudeCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAltitudeCharacteristic(CommonCharacteristicTests):
    """Test Altitude characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> AltitudeCharacteristic:
        """Provide Altitude characteristic for testing."""
        return AltitudeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Altitude characteristic."""
        return "2AB3"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid Altitude test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0xED, 0x03]), expected_value=100.5, description="100.5 m altitude"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]), expected_value=0.0, description="Sea level (0.0 m)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]), expected_value=-0.1, description="-0.1 m below sea level"
            ),
        ]

    def test_altitude_parsing(self, characteristic: AltitudeCharacteristic) -> None:
        """Test Altitude characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "m"
        assert characteristic.value_type.value == "float"

        # Test normal parsing
        test_data = bytearray([0xED, 0x03])  # 1005 = 100.5m
        parsed = characteristic.decode_value(test_data)
        assert parsed == 100.5

    def test_altitude_error_handling(self, characteristic: AltitudeCharacteristic) -> None:
        """Test Altitude error handling."""
        # Test insufficient data
        with pytest.raises(ValueError, match="Insufficient data"):
            characteristic.decode_value(bytearray([0x12]))

    def test_altitude_boundary_values(self, characteristic: AltitudeCharacteristic) -> None:
        """Test Altitude boundary values."""
        # Maximum positive (32767 * 0.1 = 3276.7m)
        data_max = bytearray([0xFF, 0x7F])
        result = characteristic.decode_value(data_max)
        assert abs(result - 3276.7) < 0.1

        # Maximum negative (-32768 * 0.1 = -3276.8m)
        data_min = bytearray([0x00, 0x80])
        result = characteristic.decode_value(data_min)
        assert abs(result - (-3276.8)) < 0.1

    def test_altitude_round_trip(self, characteristic: AltitudeCharacteristic) -> None:
        """Test encode/decode round trip."""
        test_value = 123.4
        encoded = characteristic.encode_value(test_value)
        decoded = characteristic.decode_value(encoded)
        assert decoded == test_value

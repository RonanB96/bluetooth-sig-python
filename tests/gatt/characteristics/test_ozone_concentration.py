"""Test ozone concentration characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import OzoneConcentrationCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestOzoneConcentrationCharacteristic(CommonCharacteristicTests):
    """Test Ozone Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> OzoneConcentrationCharacteristic:
        """Provide Ozone Concentration characteristic for testing."""
        return OzoneConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Ozone Concentration characteristic."""
        return "2BD4"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid ozone concentration test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x32, 0x00]), expected_value=50.0, description="50.0 ppb (typical low)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00]), expected_value=100.0, description="100.0 ppb (typical moderate)"
            ),
        ]

    def test_ozone_concentration_parsing(self, characteristic: OzoneConcentrationCharacteristic) -> None:
        """Test ozone concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "ppb"

        # Test normal parsing
        test_data = bytearray([0x64, 0x00])  # 100 ppb little endian
        parsed = characteristic.decode_value(test_data)
        assert parsed == 100

    def test_ozone_concentration_boundary_values(self, characteristic: OzoneConcentrationCharacteristic) -> None:
        """Test ozone concentration boundary values."""
        # Minimum value
        data_min = bytearray([0x00, 0x00])
        assert characteristic.decode_value(data_min) == 0.0

        # Maximum value (uint16 max)
        data_max = bytearray([0xFF, 0xFF])
        assert characteristic.decode_value(data_max) == 65535.0

    def test_ozone_concentration_typical_values(self, characteristic: OzoneConcentrationCharacteristic) -> None:
        """Test typical ozone concentration values."""
        # Low concentration (50 ppb)
        data_low = bytearray([0x32, 0x00])
        assert characteristic.decode_value(data_low) == 50.0

        # Moderate concentration (100 ppb)
        data_moderate = bytearray([0x64, 0x00])
        assert characteristic.decode_value(data_moderate) == 100.0

        # High concentration (500 ppb)
        data_high = bytearray([0xF4, 0x01])
        assert characteristic.decode_value(data_high) == 500.0

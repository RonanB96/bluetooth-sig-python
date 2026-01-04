"""Test sulfur dioxide concentration characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import SulfurDioxideConcentrationCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSulfurDioxideConcentrationCharacteristic(CommonCharacteristicTests):
    """Test Sulfur Dioxide Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> SulfurDioxideConcentrationCharacteristic:
        """Provide Sulfur Dioxide Concentration characteristic for testing."""
        return SulfurDioxideConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Sulfur Dioxide Concentration characteristic."""
        return "2BD8"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid sulfur dioxide concentration test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x14, 0x00]),
                expected_value=20.0,
                description="20.0 ppb (typical urban)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00]),
                expected_value=100.0,
                description="100.0 ppb (moderate pollution)",
            ),
        ]

    def test_sulfur_dioxide_concentration_parsing(
        self, characteristic: SulfurDioxideConcentrationCharacteristic
    ) -> None:
        """Test sulfur dioxide concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "ppb"

        # Test normal parsing
        test_data = bytearray([0x64, 0x00])  # 100 ppb little endian
        parsed = characteristic.parse_value(test_data)
        assert parsed == 100

    def test_sulfur_dioxide_concentration_boundary_values(
        self, characteristic: SulfurDioxideConcentrationCharacteristic
    ) -> None:
        """Test boundary values for SO2 concentration."""
        # Clean air
        data_min = bytearray([0x00, 0x00])
        assert characteristic.parse_value(data_min).value == 0.0

        # Maximum
        data_max = bytearray([0xFF, 0xFF])
        assert characteristic.parse_value(data_max).value == 65535.0

    def test_sulfur_dioxide_concentration_typical_levels(
        self, characteristic: SulfurDioxideConcentrationCharacteristic
    ) -> None:
        """Test typical SO2 concentration levels."""
        # Typical urban (20 ppb)
        data_urban = bytearray([0x14, 0x00])
        assert characteristic.parse_value(data_urban).value == 20.0

        # High pollution (500 ppb)
        data_high = bytearray([0xF4, 0x01])
        assert characteristic.parse_value(data_high).value == 500.0

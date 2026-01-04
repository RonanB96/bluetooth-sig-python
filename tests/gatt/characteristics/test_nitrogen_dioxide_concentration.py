"""Test nitrogen dioxide concentration characteristic parsing."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import NitrogenDioxideConcentrationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestNitrogenDioxideConcentrationCharacteristic(CommonCharacteristicTests):
    """Test Nitrogen Dioxide Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> NitrogenDioxideConcentrationCharacteristic:
        """Provide Nitrogen Dioxide Concentration characteristic for testing."""
        return NitrogenDioxideConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Nitrogen Dioxide Concentration characteristic."""
        return "2BD2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid nitrogen dioxide concentration test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x28, 0x00]),
                expected_value=40,
                description="40 ppb (typical urban)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xC8, 0x00]),
                expected_value=200,
                description="200 ppb (high pollution)",
            ),
        ]

    def test_nitrogen_dioxide_concentration_parsing(
        self, characteristic: NitrogenDioxideConcentrationCharacteristic
    ) -> None:
        """Test nitrogen dioxide concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "ppb"

        # Test normal parsing
        test_data = bytearray([0x32, 0x00])  # 50 ppb little endian
        parsed = characteristic.parse_value(test_data)
        assert parsed.value == 50

    def test_nitrogen_dioxide_concentration_boundary_values(
        self, characteristic: NitrogenDioxideConcentrationCharacteristic
    ) -> None:
        """Test boundary NO2 concentration values."""
        # Clean air
        data_min = bytearray([0x00, 0x00])
        assert characteristic.parse_value(data_min).value == 0

        # Maximum
        data_max = bytearray([0xFF, 0xFF])
        assert characteristic.parse_value(data_max).value == 65535

    def test_nitrogen_dioxide_concentration_typical_levels(
        self, characteristic: NitrogenDioxideConcentrationCharacteristic
    ) -> None:
        """Test typical NO2 concentration levels."""
        # Typical urban (40 ppb)
        data_urban = bytearray([0x28, 0x00])
        assert characteristic.parse_value(data_urban).value == 40

        # High pollution (200 ppb)
        data_high = bytearray([0xC8, 0x00])
        assert characteristic.parse_value(data_high).value == 200

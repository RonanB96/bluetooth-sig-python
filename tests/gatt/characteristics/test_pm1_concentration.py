"""Test PM1 concentration characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PM1ConcentrationCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPM1ConcentrationCharacteristic(CommonCharacteristicTests):
    """Test PM1 Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> PM1ConcentrationCharacteristic:
        """Provide PM1 Concentration characteristic for testing."""
        return PM1ConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for PM1 Concentration characteristic."""
        return "2BD5"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid PM1 concentration test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x0A, 0x00]), expected_value=10.0, description="10.0 µg/m³ (good)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x32, 0x00]), expected_value=50.0, description="50.0 µg/m³ (moderate)"
            ),
        ]

    def test_pm1_concentration_parsing(self, characteristic: PM1ConcentrationCharacteristic) -> None:
        """Test PM1 concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "µg/m³"

        # Test normal parsing
        test_data = bytearray([0x32, 0x00])  # 50 µg/m³ little endian
        parsed = characteristic.parse_value(test_data)
        assert parsed.value == 50

    def test_pm1_concentration_boundary_values(self, characteristic: PM1ConcentrationCharacteristic) -> None:
        """Test PM1 concentration boundary values."""
        # Clean air
        data_min = bytearray([0x00, 0x00])
        assert characteristic.parse_value(data_min).value == 0.0

        # Maximum
        data_max = bytearray([0xFF, 0xFF])
        assert characteristic.parse_value(data_max).value == 65535.0

    def test_pm1_concentration_air_quality_levels(self, characteristic: PM1ConcentrationCharacteristic) -> None:
        """Test PM1 concentration air quality levels."""
        # Good (10 µg/m³)
        data_good = bytearray([0x0A, 0x00])
        assert characteristic.parse_value(data_good).value == 10.0

        # Moderate (50 µg/m³)
        data_moderate = bytearray([0x32, 0x00])
        assert characteristic.parse_value(data_moderate).value == 50.0

        # Unhealthy (150 µg/m³)
        data_unhealthy = bytearray([0x96, 0x00])
        assert characteristic.parse_value(data_unhealthy).value == 150.0

"""Test PM10 concentration characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PM10ConcentrationCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPM10ConcentrationCharacteristic(CommonCharacteristicTests):
    """Test PM10 Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> PM10ConcentrationCharacteristic:
        """Provide PM10 Concentration characteristic for testing."""
        return PM10ConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for PM10 Concentration characteristic."""
        return "2BD7"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData:
        """Valid PM10 concentration test data."""
        return CharacteristicTestData(
            input_data=bytearray([0x32, 0x00]), expected_value=50.0, description="50.0 µg/m³ PM10 concentration"
        )

    def test_pm10_concentration_parsing(self, characteristic: PM10ConcentrationCharacteristic) -> None:
        """Test PM10 concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "µg/m³"

        # Test normal parsing
        test_data = bytearray([0x32, 0x00])  # 50 µg/m³ little endian
        parsed = characteristic.decode_value(test_data)
        assert parsed == 50

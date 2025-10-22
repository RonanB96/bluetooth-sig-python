"""Test PM1 concentration characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PM1ConcentrationCharacteristic

from .test_characteristic_common import CommonCharacteristicTests


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
    def valid_test_data(self) -> tuple[bytearray, float]:
        """Valid PM1 concentration test data."""
        return bytearray([0x32, 0x00]), 50.0  # 50 µg/m³ little endian

    def test_pm1_concentration_parsing(self, characteristic: PM1ConcentrationCharacteristic) -> None:
        """Test PM1 concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "µg/m³"

        # Test normal parsing
        test_data = bytearray([0x32, 0x00])  # 50 µg/m³ little endian
        parsed = characteristic.decode_value(test_data)
        assert parsed == 50

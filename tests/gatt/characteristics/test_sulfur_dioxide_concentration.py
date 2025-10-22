"""Test sulfur dioxide concentration characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import SulfurDioxideConcentrationCharacteristic

from .test_characteristic_common import CommonCharacteristicTests


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
    def valid_test_data(self) -> tuple[bytearray, float]:
        """Valid sulfur dioxide concentration test data."""
        return bytearray([0x64, 0x00]), 100.0  # 100 ppb little endian

    def test_sulfur_dioxide_concentration_parsing(
        self, characteristic: SulfurDioxideConcentrationCharacteristic
    ) -> None:
        """Test sulfur dioxide concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "ppb"

        # Test normal parsing
        test_data = bytearray([0x64, 0x00])  # 100 ppb little endian
        parsed = characteristic.decode_value(test_data)
        assert parsed == 100

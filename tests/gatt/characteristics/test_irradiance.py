"""Tests for Irradiance characteristic (0x2A77)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import IrradianceCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIrradianceCharacteristic(CommonCharacteristicTests):
    """Test suite for Irradiance characteristic."""

    @pytest.fixture
    def characteristic(self) -> IrradianceCharacteristic:
        """Return an Irradiance characteristic instance."""
        return IrradianceCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Irradiance characteristic."""
        return "2A77"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for irradiance.

        GSS: uint16, M=1 d=-1 b=0 (0.1 W/m² resolution).
        """
        return [
            CharacteristicTestData(input_data=bytearray([0, 0]), expected_value=0.0, description="No irradiance"),
            CharacteristicTestData(
                input_data=bytearray([100, 0]),  # 100 * 0.1 = 10.0 W/m²
                expected_value=10.0,
                description="10.0 W/m²",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]),  # 1000 * 0.1 = 100.0 W/m²
                expected_value=100.0,
                description="100.0 W/m²",
            ),
        ]

    def test_zero_irradiance(self) -> None:
        """Test zero irradiance."""
        char = IrradianceCharacteristic()
        result = char.parse_value(bytearray([0, 0]))
        assert result == 0.0

    def test_typical_irradiance(self) -> None:
        """Test typical irradiance value."""
        char = IrradianceCharacteristic()
        result = char.parse_value(bytearray([0xE8, 0x03]))  # 1000 * 0.1 = 100.0 W/m²
        assert result == 100.0

    def test_irradiance_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = IrradianceCharacteristic()
        for value in [0.0, 50.0, 100.0, 6553.5]:
            encoded = char.build_value(value)
            decoded = char.parse_value(encoded)
            assert abs(decoded - value) < 1e-9

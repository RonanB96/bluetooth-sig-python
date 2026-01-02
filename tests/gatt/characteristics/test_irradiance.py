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
        """Return valid test data for irradiance."""
        return [
            CharacteristicTestData(input_data=bytearray([0, 0]), expected_value=0, description="No irradiance"),
            CharacteristicTestData(input_data=bytearray([100, 0]), expected_value=100, description="Low irradiance"),
            CharacteristicTestData(
                input_data=bytearray([255, 255]), expected_value=65535, description="Maximum irradiance"
            ),
        ]

    def test_zero_irradiance(self) -> None:
        """Test zero irradiance."""
        char = IrradianceCharacteristic()
        result = char.decode_value(bytearray([0, 0]))
        assert result == 0

    def test_typical_irradiance(self) -> None:
        """Test typical irradiance value."""
        char = IrradianceCharacteristic()
        result = char.decode_value(bytearray([0xE8, 0x03]))  # 1000 W/m²
        assert result == 1000

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = IrradianceCharacteristic()
        for value in [0, 500, 1000, 65535]:
            encoded = char.encode_value(value)
            decoded = char.decode_value(encoded)
            assert decoded == value

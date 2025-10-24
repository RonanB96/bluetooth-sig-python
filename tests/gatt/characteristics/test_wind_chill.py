"""Test wind chill characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.wind_chill import WindChillCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestWindChillCharacteristic(CommonCharacteristicTests):
    """Test Wind Chill characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> WindChillCharacteristic:
        """Provide Wind Chill characteristic for testing."""
        return WindChillCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Wind Chill characteristic."""
        return "2A79"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData:
        """Valid wind chill test data."""
        return CharacteristicTestData(
            input_data=bytearray([256 - 15]), expected_value=-15.0, description="-15°C wind chill"
        )

    def test_wind_chill_parsing(self, characteristic: WindChillCharacteristic) -> None:
        """Test wind chill characteristic parsing."""
        # Test negative temperature
        data = bytearray([256 - 15])  # -15°C
        assert characteristic.decode_value(data) == -15.0

        # Test positive temperature
        data = bytearray([5])  # 5°C
        assert characteristic.decode_value(data) == 5.0

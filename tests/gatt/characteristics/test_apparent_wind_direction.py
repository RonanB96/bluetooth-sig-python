"""Test apparent wind direction characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.apparent_wind_direction import ApparentWindDirectionCharacteristic

from .test_characteristic_common import CommonCharacteristicTests, CharacteristicTestData


class TestApparentWindDirectionCharacteristic(CommonCharacteristicTests):
    """Test Apparent Wind Direction characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> ApparentWindDirectionCharacteristic:
        """Provide Apparent Wind Direction characteristic for testing."""
        return ApparentWindDirectionCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Apparent Wind Direction characteristic."""
        return "2A73"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData:
        """Valid apparent wind direction test data."""
        return CharacteristicTestData(
            input_data=bytearray([0x10, 0x27]),
            expected_value=100.0,  # 10000 * 0.01 = 100.0°
            description="100° wind direction"
        )

    def test_apparent_wind_direction_parsing(self, characteristic: ApparentWindDirectionCharacteristic) -> None:
        """Test apparent wind direction characteristic parsing."""
        direction_data = bytearray([0x10, 0x27])  # 10000 * 0.01 = 100.0°
        assert characteristic.decode_value(direction_data) == 100.0

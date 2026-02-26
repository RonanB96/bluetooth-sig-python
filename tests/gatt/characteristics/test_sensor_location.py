"""Tests for SensorLocation characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import SensorLocationCharacteristic
from bluetooth_sig.gatt.characteristics.sensor_location import SensorLocationValue
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestSensorLocationCharacteristic(CommonCharacteristicTests):
    """Test suite for SensorLocation characteristic."""

    @pytest.fixture
    def characteristic(self) -> SensorLocationCharacteristic:
        """Provide SensorLocation characteristic."""
        return SensorLocationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for SensorLocation."""
        return "2A5D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for SensorLocation."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=SensorLocationValue.OTHER,
                description="other",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03]),
                expected_value=SensorLocationValue.HIP,
                description="hip",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0E]),
                expected_value=SensorLocationValue.CHEST,
                description="chest",
            ),
        ]

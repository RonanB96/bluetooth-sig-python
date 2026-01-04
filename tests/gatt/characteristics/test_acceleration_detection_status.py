"""Tests for Acceleration Detection Status characteristic (0x2BE4)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AccelerationDetectionStatusCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAccelerationDetectionStatusCharacteristic(CommonCharacteristicTests):
    """Test suite for Acceleration Detection Status characteristic."""

    @pytest.fixture
    def characteristic(self) -> AccelerationDetectionStatusCharacteristic:
        """Return an Acceleration Detection Status characteristic instance."""
        return AccelerationDetectionStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Acceleration Detection Status characteristic."""
        return "2C1F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for acceleration detection status."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=0, description="No acceleration detected"),
            CharacteristicTestData(input_data=bytearray([1]), expected_value=1, description="Acceleration detected"),
        ]

    def test_no_acceleration(self) -> None:
        """Test no acceleration detected."""
        char = AccelerationDetectionStatusCharacteristic()
        result = char.parse_value(bytearray([0]))
        assert result.value == 0

    def test_acceleration_detected(self) -> None:
        """Test acceleration detected."""
        char = AccelerationDetectionStatusCharacteristic()
        result = char.parse_value(bytearray([1]))
        assert result.value == 1

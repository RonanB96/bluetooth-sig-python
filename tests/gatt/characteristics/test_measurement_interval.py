"""Tests for Measurement Interval characteristic (0x2A21)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import MeasurementIntervalCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMeasurementIntervalCharacteristic(CommonCharacteristicTests):
    """Test suite for Measurement Interval characteristic."""

    @pytest.fixture
    def characteristic(self) -> MeasurementIntervalCharacteristic:
        """Return a Measurement Interval characteristic instance."""
        return MeasurementIntervalCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Measurement Interval characteristic."""
        return "2A21"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for measurement interval."""
        return [
            CharacteristicTestData(input_data=bytearray([0, 0]), expected_value=0, description="Disabled"),
            CharacteristicTestData(input_data=bytearray([1, 0]), expected_value=1, description="1 second"),
            CharacteristicTestData(input_data=bytearray([60, 0]), expected_value=60, description="1 minute"),
            CharacteristicTestData(
                input_data=bytearray([255, 255]), expected_value=65535, description="Maximum interval"
            ),
        ]

    def test_disabled_interval(self) -> None:
        """Test disabled measurement interval."""
        char = MeasurementIntervalCharacteristic()
        result = char.parse_value(bytearray([0, 0]))
        assert result == 0

    def test_one_minute_interval(self) -> None:
        """Test 1 minute measurement interval."""
        char = MeasurementIntervalCharacteristic()
        result = char.parse_value(bytearray([60, 0]))
        assert result == 60

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = MeasurementIntervalCharacteristic()
        for value in [0, 1, 60, 3600, 65535]:
            encoded = char.build_value(value)
            decoded = char.parse_value(encoded)
            assert decoded == value

"""Tests for Time Source characteristic (0x2A13)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import TimeSourceCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTimeSourceCharacteristic(CommonCharacteristicTests):
    """Test suite for Time Source characteristic."""

    @pytest.fixture
    def characteristic(self) -> TimeSourceCharacteristic:
        """Return a Time Source characteristic instance."""
        return TimeSourceCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Time Source characteristic."""
        return "2A13"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for time source."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=0, description="Unknown"),
            CharacteristicTestData(input_data=bytearray([1]), expected_value=1, description="Network Time Protocol"),
            CharacteristicTestData(input_data=bytearray([2]), expected_value=2, description="GPS"),
            CharacteristicTestData(input_data=bytearray([3]), expected_value=3, description="Radio Time Signal"),
            CharacteristicTestData(input_data=bytearray([4]), expected_value=4, description="Manual"),
            CharacteristicTestData(input_data=bytearray([5]), expected_value=5, description="Atomic Clock"),
            CharacteristicTestData(input_data=bytearray([6]), expected_value=6, description="Cellular Network"),
        ]

    def test_unknown_source(self) -> None:
        """Test unknown time source."""
        char = TimeSourceCharacteristic()
        result = char.parse_value(bytearray([0]))
        assert result == 0

    def test_gps_source(self) -> None:
        """Test GPS time source."""
        char = TimeSourceCharacteristic()
        result = char.parse_value(bytearray([2]))
        assert result == 2

    def test_atomic_clock_source(self) -> None:
        """Test atomic clock time source."""
        char = TimeSourceCharacteristic()
        result = char.parse_value(bytearray([5]))
        assert result == 5

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = TimeSourceCharacteristic()
        for source in range(7):
            encoded = char.build_value(source)
            decoded = char.parse_value(encoded)
            assert decoded == source

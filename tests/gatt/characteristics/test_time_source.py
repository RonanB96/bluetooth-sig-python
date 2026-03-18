"""Tests for Time Source characteristic (0x2A13)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import TimeSourceCharacteristic
from bluetooth_sig.gatt.characteristics.time_source import TimeSource
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
            CharacteristicTestData(input_data=bytearray([0]), expected_value=TimeSource.UNKNOWN, description="Unknown"),
            CharacteristicTestData(
                input_data=bytearray([1]),
                expected_value=TimeSource.NETWORK_TIME_PROTOCOL,
                description="Network Time Protocol",
            ),
            CharacteristicTestData(input_data=bytearray([2]), expected_value=TimeSource.GPS, description="GPS"),
            CharacteristicTestData(
                input_data=bytearray([3]), expected_value=TimeSource.RADIO_TIME_SIGNAL, description="Radio Time Signal"
            ),
            CharacteristicTestData(input_data=bytearray([4]), expected_value=TimeSource.MANUAL, description="Manual"),
            CharacteristicTestData(
                input_data=bytearray([5]), expected_value=TimeSource.ATOMIC_CLOCK, description="Atomic Clock"
            ),
            CharacteristicTestData(
                input_data=bytearray([6]), expected_value=TimeSource.CELLULAR_NETWORK, description="Cellular Network"
            ),
        ]

    def test_unknown_source(self) -> None:
        """Test unknown time source."""
        char = TimeSourceCharacteristic()
        result = char.parse_value(bytearray([0]))
        assert result == TimeSource.UNKNOWN

    def test_gps_source(self) -> None:
        """Test GPS time source."""
        char = TimeSourceCharacteristic()
        result = char.parse_value(bytearray([2]))
        assert result == TimeSource.GPS

    def test_atomic_clock_source(self) -> None:
        """Test atomic clock time source."""
        char = TimeSourceCharacteristic()
        result = char.parse_value(bytearray([5]))
        assert result == TimeSource.ATOMIC_CLOCK

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = TimeSourceCharacteristic()
        for source in TimeSource:
            encoded = char.build_value(source)
            decoded = char.parse_value(encoded)
            assert decoded == source

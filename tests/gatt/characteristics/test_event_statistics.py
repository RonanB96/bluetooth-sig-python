"""Tests for Event Statistics characteristic (0x2AF4)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import EventStatisticsCharacteristic
from bluetooth_sig.gatt.characteristics.event_statistics import EventStatisticsData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestEventStatisticsCharacteristic(CommonCharacteristicTests):
    """Test suite for Event Statistics characteristic."""

    @pytest.fixture
    def characteristic(self) -> EventStatisticsCharacteristic:
        return EventStatisticsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AF4"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=EventStatisticsData(
                    number_of_events=0,
                    average_event_duration=0,
                    time_elapsed_since_last_event=0.0,
                    sensing_duration=0.0,
                ),
                description="All zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0A, 0x00, 0x1E, 0x00, 0x40, 0x40]),
                expected_value=EventStatisticsData(
                    number_of_events=10,
                    average_event_duration=30,
                    time_elapsed_since_last_event=1.0,
                    sensing_duration=1.0,
                ),
                description="10 events, 30s avg, 1s elapsed/sensing",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = EventStatisticsCharacteristic()
        original = EventStatisticsData(
            number_of_events=100,
            average_event_duration=60,
            time_elapsed_since_last_event=0.0,
            sensing_duration=0.0,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_negative_count(self) -> None:
        """Negative event count is invalid."""
        with pytest.raises(ValueError, match="outside valid range"):
            EventStatisticsData(
                number_of_events=-1,
                average_event_duration=0,
                time_elapsed_since_last_event=0.0,
                sensing_duration=0.0,
            )

    def test_validation_rejects_negative_duration(self) -> None:
        """Negative sensing duration is invalid."""
        with pytest.raises(ValueError, match="cannot be negative"):
            EventStatisticsData(
                number_of_events=0,
                average_event_duration=0,
                time_elapsed_since_last_event=0.0,
                sensing_duration=-1.0,
            )

"""Tests for DST Offset characteristic (0x2A0D)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import DstOffsetCharacteristic
from bluetooth_sig.gatt.characteristics.dst_offset import DSTOffset
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDstOffsetCharacteristic(CommonCharacteristicTests):
    """Test suite for DST Offset characteristic."""

    @pytest.fixture
    def characteristic(self) -> DstOffsetCharacteristic:
        """Return a DST Offset characteristic instance."""
        return DstOffsetCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for DST Offset characteristic."""
        return "2A0D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for DST offset."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0]), expected_value=DSTOffset.STANDARD_TIME, description="Standard time"
            ),
            CharacteristicTestData(
                input_data=bytearray([2]), expected_value=DSTOffset.HALF_HOUR_DAYLIGHT, description="Half daylight time"
            ),
            CharacteristicTestData(
                input_data=bytearray([4]), expected_value=DSTOffset.DAYLIGHT_TIME, description="Daylight time"
            ),
            CharacteristicTestData(
                input_data=bytearray([8]), expected_value=DSTOffset.DOUBLE_DAYLIGHT, description="Double daylight time"
            ),
        ]

    def test_standard_time(self) -> None:
        """Test standard time (no DST offset)."""
        char = DstOffsetCharacteristic()
        result = char.parse_value(bytearray([0]))
        assert result.value == DSTOffset.STANDARD_TIME
        assert isinstance(result.value, DSTOffset)

    def test_daylight_time(self) -> None:
        """Test daylight saving time offset."""
        char = DstOffsetCharacteristic()
        result = char.parse_value(bytearray([4]))
        assert result.value == DSTOffset.DAYLIGHT_TIME
        assert isinstance(result.value, DSTOffset)

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = DstOffsetCharacteristic()
        for value in [
            DSTOffset.STANDARD_TIME,
            DSTOffset.HALF_HOUR_DAYLIGHT,
            DSTOffset.DAYLIGHT_TIME,
            DSTOffset.DOUBLE_DAYLIGHT,
        ]:
            encoded = char.build_value(value)
            decoded = char.parse_value(encoded)
            assert decoded.value == value
            assert isinstance(decoded.value, DSTOffset)

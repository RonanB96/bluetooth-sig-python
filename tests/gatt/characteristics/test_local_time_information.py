"""Test local time information characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.local_time_information import (
    DSTOffsetInfo,
    LocalTimeInformationCharacteristic,
    LocalTimeInformationData,
    TimezoneInfo,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLocalTimeInformationCharacteristic(CommonCharacteristicTests):
    """Test Local Time Information characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> LocalTimeInformationCharacteristic:
        """Provide Local Time Information characteristic for testing."""
        return LocalTimeInformationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Local Time Information characteristic."""
        return "2A0F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Returns valid test data for LocalTimeInformationCharacteristic."""
        return [
            CharacteristicTestData(
                input_data=bytearray([4, 4]),  # timezone=+1h (4*15min), dst=+1h (value 4)
                expected_value=LocalTimeInformationData(
                    timezone=TimezoneInfo(description="UTC+01:00", offset_hours=1.0, raw_value=4),
                    dst_offset=DSTOffsetInfo(description="Daylight Time", offset_hours=1.0, raw_value=4),
                    total_offset_hours=2.0,
                ),
                description="UTC+1 with DST (+1 hour) = total offset 2 hours",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFC, 0]),  # timezone=-1h (-4*15min), dst=standard time (value 0)
                expected_value=LocalTimeInformationData(
                    timezone=TimezoneInfo(description="UTC-01:00", offset_hours=-1.0, raw_value=-4),
                    dst_offset=DSTOffsetInfo(description="Standard Time", offset_hours=0.0, raw_value=0),
                    total_offset_hours=-1.0,
                ),
                description="UTC-1 with standard time (no DST) = total offset -1 hour",
            ),
        ]

    def test_local_time_information_parsing(self, characteristic: LocalTimeInformationCharacteristic) -> None:
        """Test Local Time Information characteristic parsing."""
        # Test metadata
        assert characteristic.unit == ""

        # Test normal parsing: UTC+2 with DST (+1 hour)
        test_data = bytearray([8, 4])  # timezone=+2h (8*15min), dst=+1h (value 4)
        parsed = characteristic.parse_value(test_data)

        assert parsed.value is not None
        assert parsed.value.timezone.description == "UTC+02:00"
        assert parsed.value.timezone.offset_hours == 2.0
        assert parsed.value.dst_offset.description == "Daylight Time"
        assert parsed.value.dst_offset.offset_hours == 1.0
        assert parsed.value.total_offset_hours == 3.0

        # Test unknown values
        unknown_data = bytearray([0x80, 0xFF])  # unknown timezone and DST
        parsed_unknown = characteristic.parse_value(unknown_data)
        assert parsed_unknown.value is not None
        assert parsed_unknown.value.timezone.description == "Unknown"
        assert parsed_unknown.value.dst_offset.description == "DST offset unknown"

    def test_local_time_information_encode_value(self, characteristic: LocalTimeInformationCharacteristic) -> None:
        """Test encoding LocalTimeInformationData back to bytes."""
        from bluetooth_sig.gatt.characteristics.local_time_information import (
            DSTOffsetInfo,
            LocalTimeInformationData,
            TimezoneInfo,
        )

        # Create test data for UTC+2 with DST
        test_data = LocalTimeInformationData(
            timezone=TimezoneInfo(
                description="UTC+02:00",
                offset_hours=2.0,
                raw_value=8,  # 8 * 15min = 120min = 2h
            ),
            dst_offset=DSTOffsetInfo(
                description="Daylight Time",
                offset_hours=1.0,
                raw_value=4,  # DST value 4 = +1h
            ),
            total_offset_hours=3.0,
        )

        # Encode the data
        encoded = characteristic.build_value(test_data)

        # Should produce the correct bytes
        assert len(encoded) == 2
        assert encoded == bytearray([8, 4])

    def test_local_time_information_round_trip(self, characteristic: LocalTimeInformationCharacteristic) -> None:
        """Test that parsing and encoding preserve data."""
        # Test with UTC+2 and DST
        original_data = bytearray([8, 4])

        # Parse the data
        parsed = characteristic.parse_value(original_data)

        # Encode it back
        encoded = characteristic.build_value(parsed.value)

        # Should match the original
        assert encoded == original_data

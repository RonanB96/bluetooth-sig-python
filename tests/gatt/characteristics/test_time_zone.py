"""Test time zone characteristic."""

from __future__ import annotations

import struct

import pytest

from bluetooth_sig.gatt.characteristics import TimeZoneCharacteristic

from .test_characteristic_common import CommonCharacteristicTests


class TestTimeZoneCharacteristic(CommonCharacteristicTests):
    """Test Time Zone characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> TimeZoneCharacteristic:
        """Provide Time Zone characteristic for testing."""
        return TimeZoneCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Time Zone characteristic."""
        return "2A0E"

    @pytest.fixture
    def valid_test_data(self) -> tuple[bytearray, str]:
        """Valid time zone test data."""
        return bytearray(struct.pack("b", 4)), "UTC+01:00"  # +1 hour (4 * 15 minutes)

    def test_time_zone_parsing(self, characteristic: TimeZoneCharacteristic) -> None:
        """Test Time Zone characteristic parsing."""
        # Test metadata
        assert characteristic.unit == ""

        # Test normal time zones
        test_cases = [
            (0, "UTC+00:00"),  # UTC
            (4, "UTC+01:00"),  # +1 hour (4 * 15 minutes)
            (-4, "UTC-01:00"),  # -1 hour
            (2, "UTC+00:30"),  # +30 minutes
            (32, "UTC+08:00"),  # +8 hours (Asia)
            (-20, "UTC-05:00"),  # -5 hours (US East)
        ]

        for offset, expected in test_cases:
            test_data = bytearray(struct.pack("b", offset))  # signed byte
            parsed = characteristic.decode_value(test_data)
            assert parsed == expected

        # Test unknown value
        unknown_data = bytearray([0x80])  # SINT8_MIN
        parsed = characteristic.decode_value(unknown_data)
        assert parsed == "Unknown"

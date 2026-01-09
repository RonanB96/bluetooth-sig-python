"""Tests for Reference Time Information characteristic (0x2A14)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.reference_time_information import (
    ReferenceTimeInformationCharacteristic,
    ReferenceTimeInformationData,
    TimeSource,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestReferenceTimeInformationCharacteristic(CommonCharacteristicTests):
    """Test suite for Reference Time Information characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Adds reference time information-specific validation and edge cases.
    """

    @pytest.fixture
    def characteristic(self) -> ReferenceTimeInformationCharacteristic:
        """Return a Reference Time Information characteristic instance."""
        return ReferenceTimeInformationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Reference Time Information characteristic."""
        return "2A14"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for reference time information."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x02, 0x05, 0x03]),  # NTP, 250ms accuracy, 5 days + 3 hours
                expected_value=ReferenceTimeInformationData(
                    time_source=TimeSource.NETWORK_TIME_PROTOCOL,
                    time_accuracy=2,
                    days_since_update=5,
                    hours_since_update=3,
                ),
                description="NTP, 250ms accuracy, 5 days + 3 hours since update",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x01, 0x01, 0x12]),  # GPS, 125ms accuracy, 1 day + 18 hours
                expected_value=ReferenceTimeInformationData(
                    time_source=TimeSource.GPS,
                    time_accuracy=1,
                    days_since_update=1,
                    hours_since_update=18,
                ),
                description="GPS, 125ms accuracy, 1 day + 18 hours since update",
            ),
        ]

    # === Reference Time Information-Specific Tests ===
    @pytest.mark.parametrize(
        "time_source,expected_enum",
        [
            (0, TimeSource.UNKNOWN),
            (1, TimeSource.NETWORK_TIME_PROTOCOL),
            (2, TimeSource.GPS),
            (3, TimeSource.RADIO_TIME_SIGNAL),
            (4, TimeSource.MANUAL),
            (5, TimeSource.ATOMIC_CLOCK),
            (6, TimeSource.CELLULAR_NETWORK),
            (7, TimeSource.NOT_SYNCHRONIZED),
        ],
    )
    def test_reference_time_information_time_source_values(
        self, characteristic: ReferenceTimeInformationCharacteristic, time_source: int, expected_enum: TimeSource
    ) -> None:
        """Test all valid time source values."""
        data = bytearray([time_source, 0x00, 0x00, 0x00])
        result = characteristic.parse_value(data)
        assert result is not None
        assert result.time_source == expected_enum

    def test_reference_time_information_time_accuracy_boundary_values(
        self, characteristic: ReferenceTimeInformationCharacteristic
    ) -> None:
        """Test time accuracy boundary values."""
        # Minimum accuracy (0 = 0ms drift)
        data_min = bytearray([0x01, 0x00, 0x00, 0x00])
        result_min = characteristic.parse_value(data_min)
        assert result_min is not None
        assert result_min.time_accuracy == 0

        # Maximum valid accuracy (253 = 31.625s drift)
        data_max_valid = bytearray([0x01, 0xFD, 0x00, 0x00])
        result_max_valid = characteristic.parse_value(data_max_valid)
        assert result_max_valid is not None
        assert result_max_valid.time_accuracy == 253

        # Out of range indicator (254 = >31.625s drift)
        data_out_of_range = bytearray([0x01, 0xFE, 0x00, 0x00])
        result_out_of_range = characteristic.parse_value(data_out_of_range)
        assert result_out_of_range is not None
        assert result_out_of_range.time_accuracy == 254

        # Unknown accuracy (255)
        data_unknown = bytearray([0x01, 0xFF, 0x00, 0x00])
        result_unknown = characteristic.parse_value(data_unknown)
        assert result_unknown is not None
        assert result_unknown.time_accuracy == 255

    def test_reference_time_information_days_since_update_boundary_values(
        self, characteristic: ReferenceTimeInformationCharacteristic
    ) -> None:
        """Test days since update boundary values."""
        # Minimum days (0)
        data_min = bytearray([0x01, 0x00, 0x00, 0x00])
        result_min = characteristic.parse_value(data_min)
        assert result_min is not None
        assert result_min.days_since_update == 0

        # Maximum valid days (254)
        data_max = bytearray([0x01, 0x00, 0xFE, 0x00])
        result_max = characteristic.parse_value(data_max)
        assert result_max is not None
        assert result_max.days_since_update == 254

        # Out of range indicator (255 = >=255 days)
        data_out_of_range = bytearray([0x01, 0x00, 0xFF, 0x00])
        result_out_of_range = characteristic.parse_value(data_out_of_range)
        assert result_out_of_range is not None
        assert result_out_of_range.days_since_update == 255

    def test_reference_time_information_hours_since_update_valid_values(
        self, characteristic: ReferenceTimeInformationCharacteristic
    ) -> None:
        """Test hours since update valid values."""
        # Minimum hours (0)
        data_min = bytearray([0x01, 0x00, 0x00, 0x00])
        result_min = characteristic.parse_value(data_min)
        assert result_min is not None
        assert result_min.hours_since_update == 0

        # Maximum valid hours (23)
        data_max = bytearray([0x01, 0x00, 0x00, 0x17])
        result_max = characteristic.parse_value(data_max)
        assert result_max is not None
        assert result_max.hours_since_update == 23

        # Out of range indicator (255 = >=255 days)
        data_out_of_range = bytearray([0x01, 0x00, 0x00, 0xFF])
        result_out_of_range = characteristic.parse_value(data_out_of_range)
        assert result_out_of_range is not None
        assert result_out_of_range.hours_since_update == 255

    def test_reference_time_information_invalid_hours_since_update(
        self, characteristic: ReferenceTimeInformationCharacteristic
    ) -> None:
        """Test that invalid hours since update values are rejected."""
        # Hours: 24 (invalid, should be 0-23 or 255)
        data_invalid = bytearray([0x01, 0x00, 0x00, 0x18])
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(data_invalid)
        assert "hours since update" in str(exc_info.value).lower()

    def test_reference_time_information_invalid_time_source(
        self, characteristic: ReferenceTimeInformationCharacteristic
    ) -> None:
        """Test that invalid time source values are rejected."""
        # Time source: 100 (reserved, should be 0-7)
        data_invalid = bytearray([0x64, 0x00, 0x00, 0x00])
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(data_invalid)
        assert "time source" in str(exc_info.value).lower()

    def test_reference_time_information_gps_zero_drift(
        self, characteristic: ReferenceTimeInformationCharacteristic
    ) -> None:
        """Test GPS time source with zero drift and no update."""
        data = bytearray([0x02, 0x00, 0x00, 0x00])  # GPS, 0ms accuracy, 0 days + 0 hours
        result = characteristic.parse_value(data)
        assert result is not None
        assert result.time_source == TimeSource.GPS
        assert result.time_accuracy == 0
        assert result.days_since_update == 0
        assert result.hours_since_update == 0

    def test_reference_time_information_not_synchronized_unknown_accuracy(
        self, characteristic: ReferenceTimeInformationCharacteristic
    ) -> None:
        """Test not synchronized time source with unknown accuracy."""
        data = bytearray([0x07, 0xFF, 0xFF, 0xFF])  # Not synchronized, unknown accuracy, >=255 days
        result = characteristic.parse_value(data)
        assert result is not None
        assert result.time_source == TimeSource.NOT_SYNCHRONIZED
        assert result.time_accuracy == 255  # Unknown
        assert result.days_since_update == 255  # >=255 days
        assert result.hours_since_update == 255  # >=255 days

    def test_reference_time_information_roundtrip(self, characteristic: ReferenceTimeInformationCharacteristic) -> None:
        """Test that encode/decode are inverse operations."""
        original = ReferenceTimeInformationData(
            time_source=TimeSource.CELLULAR_NETWORK,
            time_accuracy=50,  # 50 * 125ms = 6.25s
            days_since_update=100,
            hours_since_update=12,
        )

        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)

        assert decoded is not None
        assert decoded.time_source == original.time_source
        assert decoded.time_accuracy == original.time_accuracy
        assert decoded.days_since_update == original.days_since_update
        assert decoded.hours_since_update == original.hours_since_update

"""Tests for CGM Status characteristic (0x2AA9)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.cgm_status import (
    CGMStatusCharacteristic,
    CGMStatusData,
    CGMStatusFlags,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestCGMStatusCharacteristic(CommonCharacteristicTests):
    """Test CGM Status characteristic."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide characteristic instance."""
        return CGMStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID."""
        return "2AA9"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x0A,
                        0x00,  # time_offset: 10 minutes
                        0x00,
                        0x00,
                        0x00,  # status: no flags set
                    ]
                ),
                expected_value=CGMStatusData(
                    time_offset=10,
                    status=CGMStatusFlags(0),
                ),
                description="No status flags, no CRC",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x1E,
                        0x00,  # time_offset: 30 minutes
                        0x03,
                        0x00,
                        0x00,  # status: session stopped + battery low
                        0x34,
                        0x12,  # e2e_crc: 0x1234
                    ]
                ),
                expected_value=CGMStatusData(
                    time_offset=30,
                    status=CGMStatusFlags.SESSION_STOPPED | CGMStatusFlags.DEVICE_BATTERY_LOW,
                    e2e_crc=0x1234,
                ),
                description="Status flags with CRC",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x3C,
                        0x00,  # time_offset: 60 minutes
                        0x00,
                        0x01,
                        0x01,  # status: time sync req + patient low
                    ]
                ),
                expected_value=CGMStatusData(
                    time_offset=60,
                    status=CGMStatusFlags.TIME_SYNC_REQUIRED | CGMStatusFlags.RESULT_LOWER_THAN_PATIENT_LOW,
                ),
                description="Cal/temp and warning flags set",
            ),
        ]

    def test_all_octets_set(self) -> None:
        """Test with flags from all three octets."""
        char = CGMStatusCharacteristic()
        data = bytearray(
            [
                0x05,
                0x00,  # time_offset: 5
                0x01,  # status octet: session stopped
                0x04,  # cal/temp octet: calibration recommended
                0x10,  # warning octet: rate of decrease exceeded
            ]
        )
        result = char.parse_value(data)
        assert result.status & CGMStatusFlags.SESSION_STOPPED
        assert result.status & CGMStatusFlags.CALIBRATION_RECOMMENDED
        assert result.status & CGMStatusFlags.RATE_OF_DECREASE_EXCEEDED

    def test_round_trip_with_crc(self) -> None:
        """Test encode/decode round-trip with CRC."""
        char = CGMStatusCharacteristic()
        original = CGMStatusData(
            time_offset=45,
            status=CGMStatusFlags.SENSOR_MALFUNCTION | CGMStatusFlags.CALIBRATION_REQUIRED,
            e2e_crc=0xBEEF,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded.time_offset == original.time_offset
        assert decoded.status == original.status
        assert decoded.e2e_crc == original.e2e_crc

    def test_round_trip_without_crc(self) -> None:
        """Test encode/decode round-trip without CRC."""
        char = CGMStatusCharacteristic()
        original = CGMStatusData(
            time_offset=10,
            status=CGMStatusFlags(0),
        )
        encoded = char.build_value(original)
        assert len(encoded) == 5
        decoded = char.parse_value(encoded)
        assert decoded.time_offset == 10
        assert decoded.e2e_crc is None

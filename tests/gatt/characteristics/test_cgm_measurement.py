"""Tests for CGM Measurement characteristic (0x2AA7)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.cgm_measurement import (
    CGMCalTempOctet,
    CGMMeasurementCharacteristic,
    CGMMeasurementData,
    CGMMeasurementFlags,
    CGMMeasurementRecord,
    CGMSensorStatusOctet,
    CGMWarningOctet,
)
from bluetooth_sig.gatt.characteristics.utils import IEEE11073Parser
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


def _sfloat_bytes(value: float) -> list[int]:
    """Encode a float to SFLOAT and return as list of ints."""
    return list(IEEE11073Parser.encode_sfloat(value))


class TestCGMMeasurementCharacteristic(CommonCharacteristicTests):
    """Test CGM Measurement characteristic."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide characteristic instance."""
        return CGMMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID."""
        return "2AA7"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x06,  # size: 6 bytes
                        0x00,  # flags: nothing optional
                        *_sfloat_bytes(100.0),  # glucose concentration
                        0x0A,
                        0x00,  # time_offset: 10 minutes
                    ]
                ),
                expected_value=CGMMeasurementData(
                    records=(
                        CGMMeasurementRecord(
                            size=6,
                            flags=CGMMeasurementFlags(0x00),
                            glucose_concentration=100.0,
                            time_offset=10,
                        ),
                    ),
                ),
                description="Single record, no optional fields",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x0A,  # size: 10 bytes
                        0x03,  # flags: trend + quality present
                        *_sfloat_bytes(120.0),  # glucose
                        0x1E,
                        0x00,  # time_offset: 30
                        *_sfloat_bytes(2.0),  # trend: 2 mg/dL/min
                        *_sfloat_bytes(95.0),  # quality: 95%
                    ]
                ),
                expected_value=CGMMeasurementData(
                    records=(
                        CGMMeasurementRecord(
                            size=10,
                            flags=CGMMeasurementFlags(0x03),
                            glucose_concentration=120.0,
                            time_offset=30,
                            trend_information=2.0,
                            quality=95.0,
                        ),
                    ),
                ),
                description="Single record with trend and quality",
            ),
        ]

    def test_annunciation_octets(self) -> None:
        """Test parsing with all three annunciation octets."""
        char = CGMMeasurementCharacteristic()
        data = bytearray(
            [
                0x09,  # size: 9 bytes
                0xE0,  # flags: status + cal_temp + warning present
                *_sfloat_bytes(90.0),  # glucose
                0x05,
                0x00,  # time_offset: 5
                0x01,  # status_octet
                0x02,  # cal_temp_octet
                0x04,  # warning_octet
            ]
        )
        result = char.parse_value(data)
        assert len(result.records) == 1
        rec = result.records[0]
        assert rec.status_octet == 0x01
        assert rec.cal_temp_octet == 0x02
        assert rec.warning_octet == 0x04
        assert rec.trend_information is None
        assert rec.quality is None

    def test_multiple_records(self) -> None:
        """Test parsing multiple concatenated records."""
        char = CGMMeasurementCharacteristic()
        data = bytearray(
            [
                # Record 1: minimal
                0x06,
                0x00,
                *_sfloat_bytes(100.0),
                0x0A,
                0x00,
                # Record 2: minimal
                0x06,
                0x00,
                *_sfloat_bytes(110.0),
                0x14,
                0x00,
            ]
        )
        result = char.parse_value(data)
        assert len(result.records) == 2
        assert result.records[0].glucose_concentration == 100.0
        assert result.records[0].time_offset == 10
        assert result.records[1].glucose_concentration == 110.0
        assert result.records[1].time_offset == 20

    def test_round_trip_single_record(self) -> None:
        """Test encode/decode round-trip for a single record."""
        char = CGMMeasurementCharacteristic()
        original = CGMMeasurementData(
            records=(
                CGMMeasurementRecord(
                    size=10,
                    flags=CGMMeasurementFlags(0x03),
                    glucose_concentration=120.0,
                    time_offset=30,
                    trend_information=2.0,
                    quality=95.0,
                ),
            ),
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert len(decoded.records) == 1
        rec = decoded.records[0]
        assert rec.glucose_concentration == 120.0
        assert rec.time_offset == 30
        assert rec.trend_information == 2.0
        assert rec.quality == 95.0

    def test_round_trip_multiple_records(self) -> None:
        """Test encode/decode round-trip with multiple records."""
        char = CGMMeasurementCharacteristic()
        original = CGMMeasurementData(
            records=(
                CGMMeasurementRecord(
                    size=6,
                    flags=CGMMeasurementFlags(0x00),
                    glucose_concentration=100.0,
                    time_offset=10,
                ),
                CGMMeasurementRecord(
                    size=9,
                    flags=CGMMeasurementFlags(0xE0),
                    glucose_concentration=90.0,
                    time_offset=5,
                    status_octet=CGMSensorStatusOctet(0x01),
                    cal_temp_octet=CGMCalTempOctet(0x02),
                    warning_octet=CGMWarningOctet(0x04),
                ),
            ),
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert len(decoded.records) == 2
        assert decoded.records[0].glucose_concentration == 100.0
        assert decoded.records[1].status_octet == CGMSensorStatusOctet(0x01)
        assert decoded.records[1].warning_octet == CGMWarningOctet(0x04)

    def test_round_trip_with_all_fields(self) -> None:
        """Test round-trip with all optional fields present."""
        char = CGMMeasurementCharacteristic()
        original = CGMMeasurementData(
            records=(
                CGMMeasurementRecord(
                    size=13,
                    flags=CGMMeasurementFlags(0xE3),
                    glucose_concentration=150.0,
                    time_offset=60,
                    status_octet=CGMSensorStatusOctet(0x0F),
                    cal_temp_octet=CGMCalTempOctet(0x03),
                    warning_octet=CGMWarningOctet(0x01),
                    trend_information=1.0,
                    quality=98.0,
                ),
            ),
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        rec = decoded.records[0]
        assert rec.glucose_concentration == 150.0
        assert rec.status_octet == CGMSensorStatusOctet(0x0F)
        assert rec.cal_temp_octet == CGMCalTempOctet(0x03)
        assert rec.warning_octet == CGMWarningOctet(0x01)
        assert rec.trend_information == 1.0
        assert rec.quality == 98.0

"""Tests for Blood Pressure Record characteristic (0x2B36)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.blood_pressure_record import (
    BloodPressureRecordCharacteristic,
    BloodPressureRecordData,
)
from bluetooth_sig.types.uuid import BluetoothUUID
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestBloodPressureRecordCharacteristic(CommonCharacteristicTests):
    """Test Blood Pressure Record characteristic."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide characteristic instance."""
        return BloodPressureRecordCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID."""
        return "2B36"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x03,  # header: first + last segment, counter=0
                        0x01,
                        0x00,  # sequence_number: 1
                        0x34,
                        0x2B,  # uuid: 0x2B34 (enhanced BP measurement)
                        0xAA,
                        0xBB,
                        0xCC,  # recorded_data: 3 bytes
                    ]
                ),
                expected_value=BloodPressureRecordData(
                    first_segment=True,
                    last_segment=True,
                    segment_counter=0,
                    sequence_number=1,
                    uuid=BluetoothUUID(0x2B34),
                    recorded_data=b"\xaa\xbb\xcc",
                ),
                description="Single-segment record with 3 bytes payload",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x05,  # header: first segment, counter=1
                        0x00,
                        0x00,  # sequence_number: 0
                        0x35,
                        0x2B,  # uuid: 0x2B35
                    ]
                ),
                expected_value=BloodPressureRecordData(
                    first_segment=True,
                    last_segment=False,
                    segment_counter=1,
                    sequence_number=0,
                    uuid=BluetoothUUID(0x2B35),
                    recorded_data=b"",
                ),
                description="First segment, no recorded data",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xFA,  # header: last segment, counter=62 (0x3E << 2 | 0x02 = 0xFA)
                        0xFF,
                        0xFF,  # sequence_number: 65535
                        0x34,
                        0x2B,  # uuid: 0x2B34
                        0x01,
                        0x02,
                        0x03,
                        0x04,
                        0x05,  # recorded_data: 5 bytes
                    ]
                ),
                expected_value=BloodPressureRecordData(
                    first_segment=False,
                    last_segment=True,
                    segment_counter=62,
                    sequence_number=65535,
                    uuid=BluetoothUUID(0x2B34),
                    recorded_data=b"\x01\x02\x03\x04\x05",
                ),
                description="Last segment with high counter and sequence",
            ),
        ]

    def test_segment_counter_max(self) -> None:
        """Test maximum segment counter value (63)."""
        char = BloodPressureRecordCharacteristic()
        # counter=63 -> bits 2-7 = 0x3F << 2 = 0xFC
        data = bytearray([0xFC, 0x00, 0x00, 0x34, 0x2B])
        result = char.parse_value(data)
        assert result.segment_counter == 63
        assert result.first_segment is False
        assert result.last_segment is False

    def test_round_trip_record(self) -> None:
        """Test encode/decode round-trip."""
        char = BloodPressureRecordCharacteristic()
        original = BloodPressureRecordData(
            first_segment=True,
            last_segment=True,
            segment_counter=10,
            sequence_number=42,
            uuid=BluetoothUUID(0x2B34),
            recorded_data=b"\xde\xad\xbe\xef",
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded.first_segment == original.first_segment
        assert decoded.last_segment == original.last_segment
        assert decoded.segment_counter == original.segment_counter
        assert decoded.sequence_number == original.sequence_number
        assert decoded.uuid == original.uuid
        assert decoded.recorded_data == original.recorded_data

    def test_encode_with_e2e_crc(self) -> None:
        """Test encoding with E2E-CRC appended."""
        char = BloodPressureRecordCharacteristic()
        original = BloodPressureRecordData(
            first_segment=True,
            last_segment=True,
            segment_counter=0,
            sequence_number=1,
            uuid=BluetoothUUID(0x2B34),
            recorded_data=b"\xaa",
            e2e_crc=0x1234,
        )
        encoded = char.build_value(original)
        # header(1) + seq(2) + uuid(2) + data(1) + crc(2) = 8
        assert len(encoded) == 8
        # CRC should be at the end
        assert encoded[-2:] == bytearray([0x34, 0x12])

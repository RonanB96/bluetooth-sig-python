"""Tests for CGM Session Run Time characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cgm_session_run_time import (
    CGMSessionRunTimeCharacteristic,
    CGMSessionRunTimeData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCGMSessionRunTimeCharacteristic(CommonCharacteristicTests):
    """Test suite for CGMSessionRunTimeCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> CGMSessionRunTimeCharacteristic:
        return CGMSessionRunTimeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AAB"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"\xa8\x00"),
                expected_value=CGMSessionRunTimeData(run_time_hours=168),
                description="168 hours, no CRC",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x50\x01\xcd\xab"),
                expected_value=CGMSessionRunTimeData(run_time_hours=336, e2e_crc=0xABCD),
                description="336 hours with E2E-CRC",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x00\x00"),
                expected_value=CGMSessionRunTimeData(run_time_hours=0),
                description="zero run time",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\xff\xff"),
                expected_value=CGMSessionRunTimeData(run_time_hours=65535),
                description="maximum run time",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\x50\x01\x34\x12"),
                expected_value=CGMSessionRunTimeData(run_time_hours=336, e2e_crc=0x1234),
                description="336 hours with E2E-CRC 0x1234",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\xff\xff\xff\xff"),
                expected_value=CGMSessionRunTimeData(run_time_hours=65535, e2e_crc=0xFFFF),
                description="maximum run time with maximum CRC",
            ),
        ]

    # === Encode tests (not covered by base class) ===

    def test_encode_basic(self, characteristic: CGMSessionRunTimeCharacteristic) -> None:
        """Test encoding run time without CRC."""
        data = CGMSessionRunTimeData(run_time_hours=168)
        result = characteristic.build_value(data)
        assert result == bytearray(b"\xa8\x00")

    def test_encode_with_crc(self, characteristic: CGMSessionRunTimeCharacteristic) -> None:
        """Test encoding run time with E2E-CRC."""
        data = CGMSessionRunTimeData(run_time_hours=336, e2e_crc=0xABCD)
        result = characteristic.build_value(data)
        assert result == bytearray(b"\x50\x01\xcd\xab")

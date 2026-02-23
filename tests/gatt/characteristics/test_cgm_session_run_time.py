"""Tests for CGM Session Run Time characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cgm_session_run_time import (
    CGMSessionRunTimeCharacteristic,
    CGMSessionRunTimeData,
)


@pytest.fixture
def characteristic() -> CGMSessionRunTimeCharacteristic:
    """Create a CGMSessionRunTimeCharacteristic instance."""
    return CGMSessionRunTimeCharacteristic()


class TestCGMSessionRunTimeDecode:
    """Tests for CGM Session Run Time decoding."""

    def test_basic_run_time(self, characteristic: CGMSessionRunTimeCharacteristic) -> None:
        """Test decoding a basic run time without CRC."""
        # 168 hours = 0x00A8
        data = bytearray(b"\xa8\x00")
        result = characteristic.parse_value(data)
        assert isinstance(result, CGMSessionRunTimeData)
        assert result.run_time_hours == 168
        assert result.e2e_crc is None

    def test_run_time_with_crc(self, characteristic: CGMSessionRunTimeCharacteristic) -> None:
        """Test decoding run time with E2E-CRC."""
        # 336 hours = 0x0150, CRC = 0xABCD
        data = bytearray(b"\x50\x01\xcd\xab")
        result = characteristic.parse_value(data)
        assert isinstance(result, CGMSessionRunTimeData)
        assert result.run_time_hours == 336
        assert result.e2e_crc == 0xABCD

    def test_zero_run_time(self, characteristic: CGMSessionRunTimeCharacteristic) -> None:
        """Test decoding zero run time."""
        data = bytearray(b"\x00\x00")
        result = characteristic.parse_value(data)
        assert result.run_time_hours == 0
        assert result.e2e_crc is None

    def test_max_run_time(self, characteristic: CGMSessionRunTimeCharacteristic) -> None:
        """Test decoding maximum run time (65535 hours)."""
        data = bytearray(b"\xff\xff")
        result = characteristic.parse_value(data)
        assert result.run_time_hours == 65535
        assert result.e2e_crc is None


class TestCGMSessionRunTimeEncode:
    """Tests for CGM Session Run Time encoding."""

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


class TestCGMSessionRunTimeRoundTrip:
    """Round-trip tests for CGM Session Run Time."""

    @pytest.mark.parametrize(
        ("run_time", "crc"),
        [
            (0, None),
            (168, None),
            (336, 0x1234),
            (65535, 0xFFFF),
        ],
    )
    def test_round_trip(
        self,
        characteristic: CGMSessionRunTimeCharacteristic,
        run_time: int,
        crc: int | None,
    ) -> None:
        """Test encode → decode round-trip."""
        original = CGMSessionRunTimeData(run_time_hours=run_time, e2e_crc=crc)
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original

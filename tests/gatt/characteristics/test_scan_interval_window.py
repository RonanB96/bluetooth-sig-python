"""Tests for Scan Interval Window characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ScanIntervalWindowCharacteristic
from bluetooth_sig.types.scan_interval_window import ScanIntervalWindowData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestScanIntervalWindowCharacteristic(CommonCharacteristicTests):
    """Test suite for Scan Interval Window characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds scan interval window-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> ScanIntervalWindowCharacteristic:
        """Return a Scan Interval Window characteristic instance."""
        return ScanIntervalWindowCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Scan Interval Window characteristic."""
        return "2A4F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for scan interval window."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x04, 0x00, 0x04, 0x00]),
                expected_value=ScanIntervalWindowData(
                    scan_interval=ScanIntervalWindowData.SCAN_INTERVAL_MIN,
                    scan_window=ScanIntervalWindowData.SCAN_WINDOW_MIN,
                ),
                description="Minimum values (scan window = scan interval)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x40, 0x00, 0x20]),
                expected_value=ScanIntervalWindowData(
                    scan_interval=ScanIntervalWindowData.SCAN_INTERVAL_MAX,
                    scan_window=ScanIntervalWindowData.SCAN_INTERVAL_MAX // 2,
                ),
                description="Maximum range values (scan window < scan interval)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x20, 0x00, 0x10, 0x00]),
                expected_value=ScanIntervalWindowData(scan_interval=0x0020, scan_window=0x0010),
                description="Typical values",
            ),
        ]

    # === Scan Interval Window-Specific Tests ===

    @pytest.mark.parametrize(
        "scan_interval,scan_window",
        [
            (ScanIntervalWindowData.SCAN_INTERVAL_MIN, ScanIntervalWindowData.SCAN_WINDOW_MIN),  # Equal (minimum)
            (0x0006, ScanIntervalWindowData.SCAN_WINDOW_MIN),  # Window < interval
            (ScanIntervalWindowData.SCAN_INTERVAL_MAX, ScanIntervalWindowData.SCAN_INTERVAL_MAX // 2),  # Maximum values
            (0x1000, 0x0800),  # Typical values
        ],
    )
    def test_scan_interval_window_various_values(
        self, characteristic: ScanIntervalWindowCharacteristic, scan_interval: int, scan_window: int
    ) -> None:
        """Test scan interval window with various valid values."""
        # Create data: little-endian uint16 pairs
        data = bytearray()
        data.extend(scan_interval.to_bytes(2, byteorder="little"))
        data.extend(scan_window.to_bytes(2, byteorder="little"))

        result = characteristic.parse_value(data)
        expected = ScanIntervalWindowData(scan_interval=scan_interval, scan_window=scan_window)
        assert result.value == expected

    def test_scan_interval_window_boundary_values(self, characteristic: ScanIntervalWindowCharacteristic) -> None:
        """Test scan interval window boundary values."""
        # Test minimum values
        data = bytearray([0x04, 0x00, 0x04, 0x00])  # SCAN_INTERVAL_MIN, SCAN_WINDOW_MIN
        result = characteristic.parse_value(data)
        expected = ScanIntervalWindowData(
            scan_interval=ScanIntervalWindowData.SCAN_INTERVAL_MIN, scan_window=ScanIntervalWindowData.SCAN_WINDOW_MIN
        )
        assert result.value == expected

        # Test maximum values
        data = bytearray([0x00, 0x40, 0x00, 0x20])  # SCAN_INTERVAL_MAX, SCAN_INTERVAL_MAX//2
        result = characteristic.parse_value(data)
        expected = ScanIntervalWindowData(
            scan_interval=ScanIntervalWindowData.SCAN_INTERVAL_MAX,
            scan_window=ScanIntervalWindowData.SCAN_INTERVAL_MAX // 2,
        )
        assert result.value == expected

    def test_scan_interval_window_invalid_length(self, characteristic: ScanIntervalWindowCharacteristic) -> None:
        """Test that invalid data lengths are rejected."""
        # Too short
        result = characteristic.parse_value(bytearray([0x04, 0x00, 0x04]))  # 3 bytes
        assert not result.parse_success
        assert "4 bytes" in result.error_message

        # Too long
        result = characteristic.parse_value(bytearray([0x04, 0x00, 0x04, 0x00, 0xFF]))  # 5 bytes
        assert not result.parse_success

    def test_scan_interval_window_scan_window_too_large(self, characteristic: ScanIntervalWindowCharacteristic) -> None:
        """Test that scan window > scan interval is rejected."""
        # scan_window > scan_interval
        data = bytearray([0x04, 0x00, 0x06, 0x00])  # 0x0004, 0x0006
        result = characteristic.parse_value(data)
        assert not result.parse_success
        assert "must be <=" in result.error_message.lower()

    def test_scan_interval_window_out_of_range_values(self, characteristic: ScanIntervalWindowCharacteristic) -> None:
        """Test that out-of-range values are rejected."""
        # scan_interval too low
        data = bytearray([0x03, 0x00, 0x03, 0x00])  # SCAN_INTERVAL_MIN-1, SCAN_WINDOW_MIN-1
        result = characteristic.parse_value(data)
        assert not result.parse_success

        # scan_interval too high
        data = bytearray([0x01, 0x40, 0x00, 0x20])  # SCAN_INTERVAL_MAX+1, SCAN_WINDOW_MAX//2
        result = characteristic.parse_value(data)
        assert not result.parse_success

        # scan_window too low
        data = bytearray([0x04, 0x00, 0x03, 0x00])  # SCAN_INTERVAL_MIN, SCAN_WINDOW_MIN-1
        result = characteristic.parse_value(data)
        assert not result.parse_success

    def test_scan_interval_window_milliseconds_conversion(self) -> None:
        """Test millisecond conversion properties."""
        data = ScanIntervalWindowData(
            scan_interval=0x0008, scan_window=0x0004
        )  # 8*UNITS_TO_MS_FACTOR=5ms, 4*UNITS_TO_MS_FACTOR=2.5ms

        assert data.scan_interval_ms == 0x0008 * ScanIntervalWindowData.UNITS_TO_MS_FACTOR
        assert data.scan_window_ms == 0x0004 * ScanIntervalWindowData.UNITS_TO_MS_FACTOR

    def test_scan_interval_window_encode_decode_round_trip(
        self, characteristic: ScanIntervalWindowCharacteristic
    ) -> None:
        """Test that encoding and decoding preserve data."""
        original = ScanIntervalWindowData(scan_interval=0x0020, scan_window=0x0010)

        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)

        assert decoded.value == original

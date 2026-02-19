"""Tests for 3D Information Data AD type decode (AD 0x3D, CSS Part A §1.13).

Tests cover:
- Full decode with all flags set and cleared
- Boolean property accessors from IntFlag
- Truncated and empty data handling
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from bluetooth_sig.gatt.exceptions import InsufficientDataError
from bluetooth_sig.types.advertising.three_d_information import (
    ThreeDInformationData,
    ThreeDInformationFlags,
)


@dataclass
class ADTypeTestData:
    """Test data for AD type decode — mirrors CharacteristicTestData."""

    input_data: bytearray
    expected_value: Any
    description: str = ""


class TestThreeDInformationDecode:
    """Tests for ThreeDInformationData.decode()."""

    @pytest.fixture
    def valid_test_data(self) -> list[ADTypeTestData]:
        """Standard decode scenarios covering flag combinations."""
        return [
            ADTypeTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=ThreeDInformationData(
                    flags=ThreeDInformationFlags(0),
                    path_loss_threshold=0,
                ),
                description="No flags set, zero path loss threshold",
            ),
            ADTypeTestData(
                input_data=bytearray([0x87, 0x32]),
                expected_value=ThreeDInformationData(
                    flags=ThreeDInformationFlags(0x87),
                    path_loss_threshold=0x32,
                ),
                description="All flags set (0x01 | 0x02 | 0x04 | 0x80), path loss = 50",
            ),
            ADTypeTestData(
                input_data=bytearray([0x01, 0xFF]),
                expected_value=ThreeDInformationData(
                    flags=ThreeDInformationFlags.ASSOCIATION_NOTIFICATION,
                    path_loss_threshold=255,
                ),
                description="Association notification only, max path loss threshold",
            ),
        ]

    def test_decode_valid_data(self, valid_test_data: list[ADTypeTestData]) -> None:
        """Decode each valid test case and verify all fields match."""
        for case in valid_test_data:
            result = ThreeDInformationData.decode(case.input_data)
            assert result == case.expected_value, f"Failed: {case.description}"

    def test_decode_factory_test_mode_only(self) -> None:
        """Decode payload with only factory test mode flag set (bit 7)."""
        data = bytearray([0x80, 0x0A])
        result = ThreeDInformationData.decode(data)

        assert result.factory_test_mode is True
        assert result.association_notification is False
        assert result.battery_level_reporting is False
        assert result.send_battery_on_startup is False
        assert result.path_loss_threshold == 10

    def test_decode_extra_bytes_ignored(self) -> None:
        """Trailing bytes beyond the 2-byte payload are ignored."""
        data = bytearray([0x03, 0x14, 0xFF, 0xFE])
        result = ThreeDInformationData.decode(data)

        expected_flags = (
            ThreeDInformationFlags.ASSOCIATION_NOTIFICATION | ThreeDInformationFlags.BATTERY_LEVEL_REPORTING
        )
        assert result.flags == expected_flags
        assert result.path_loss_threshold == 20


class TestThreeDInformationErrors:
    """Error-path tests for ThreeDInformationData.decode()."""

    def test_decode_empty_data_raises(self) -> None:
        """Empty bytearray raises InsufficientDataError — no flags byte."""
        with pytest.raises(InsufficientDataError):
            ThreeDInformationData.decode(bytearray())

    def test_decode_single_byte_raises(self) -> None:
        """Only flags byte present, path_loss_threshold missing."""
        with pytest.raises(InsufficientDataError):
            ThreeDInformationData.decode(bytearray([0x01]))


class TestThreeDInformationProperties:
    """Tests for ThreeDInformationData boolean property accessors."""

    def test_association_notification_enabled(self) -> None:
        """association_notification is True when bit 0 set."""
        data = ThreeDInformationData(
            flags=ThreeDInformationFlags.ASSOCIATION_NOTIFICATION,
            path_loss_threshold=0,
        )
        assert data.association_notification is True

    def test_association_notification_disabled(self) -> None:
        """association_notification is False when bit 0 clear."""
        data = ThreeDInformationData(flags=ThreeDInformationFlags(0), path_loss_threshold=0)
        assert data.association_notification is False

    def test_battery_level_reporting_enabled(self) -> None:
        """battery_level_reporting is True when bit 1 set."""
        data = ThreeDInformationData(
            flags=ThreeDInformationFlags.BATTERY_LEVEL_REPORTING,
            path_loss_threshold=0,
        )
        assert data.battery_level_reporting is True

    def test_send_battery_on_startup_enabled(self) -> None:
        """send_battery_on_startup is True when bit 2 set."""
        data = ThreeDInformationData(
            flags=ThreeDInformationFlags.SEND_BATTERY_ON_STARTUP,
            path_loss_threshold=0,
        )
        assert data.send_battery_on_startup is True

    def test_factory_test_mode_enabled(self) -> None:
        """factory_test_mode is True when bit 7 set."""
        data = ThreeDInformationData(
            flags=ThreeDInformationFlags.FACTORY_TEST_MODE,
            path_loss_threshold=0,
        )
        assert data.factory_test_mode is True

    def test_all_flags_set_properties(self) -> None:
        """All boolean properties are True when all flags are set."""
        all_flags = (
            ThreeDInformationFlags.ASSOCIATION_NOTIFICATION
            | ThreeDInformationFlags.BATTERY_LEVEL_REPORTING
            | ThreeDInformationFlags.SEND_BATTERY_ON_STARTUP
            | ThreeDInformationFlags.FACTORY_TEST_MODE
        )
        data = ThreeDInformationData(flags=all_flags, path_loss_threshold=0)

        assert data.association_notification is True
        assert data.battery_level_reporting is True
        assert data.send_battery_on_startup is True
        assert data.factory_test_mode is True

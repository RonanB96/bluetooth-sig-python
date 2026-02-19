"""Tests for Channel Map Update Indication AD type decode (AD 0x28, Core Spec Vol 3, Part C §11).

Tests cover:
- Normal decode with channel map and instant
- is_channel_used boundary checks (channel 0, 36)
- Out-of-range channel numbers
- Truncated and empty data handling
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from bluetooth_sig.gatt.exceptions import InsufficientDataError
from bluetooth_sig.types.advertising.channel_map_update import (
    CHANNEL_MAP_INSTANT_OFFSET,
    CHANNEL_MAP_LENGTH,
    MAX_DATA_CHANNEL,
    ChannelMapUpdateIndication,
)


@dataclass
class ADTypeTestData:
    """Test data for AD type decode — mirrors CharacteristicTestData."""

    input_data: bytearray
    expected_value: Any
    description: str = ""


class TestChannelMapUpdateDecode:
    """Tests for ChannelMapUpdateIndication.decode()."""

    @pytest.fixture
    def valid_test_data(self) -> list[ADTypeTestData]:
        """Standard decode scenarios for channel map update indication."""
        return [
            ADTypeTestData(
                input_data=bytearray([
                    0xFF, 0xFF, 0xFF, 0xFF, 0x1F,  # all 37 channels used
                    0x64, 0x00,                      # instant = 100
                ]),
                expected_value=ChannelMapUpdateIndication(
                    channel_map=b"\xFF\xFF\xFF\xFF\x1F",
                    instant=100,
                ),
                description="All channels used, instant = 100",
            ),
            ADTypeTestData(
                input_data=bytearray([
                    0x00, 0x00, 0x00, 0x00, 0x00,  # no channels used
                    0x00, 0x00,                      # instant = 0
                ]),
                expected_value=ChannelMapUpdateIndication(
                    channel_map=b"\x00\x00\x00\x00\x00",
                    instant=0,
                ),
                description="No channels used, instant = 0",
            ),
            ADTypeTestData(
                input_data=bytearray([
                    0x01, 0x00, 0x00, 0x00, 0x00,  # only channel 0 used
                    0xFF, 0xFF,                      # instant = 65535 (max uint16)
                ]),
                expected_value=ChannelMapUpdateIndication(
                    channel_map=b"\x01\x00\x00\x00\x00",
                    instant=65535,
                ),
                description="Only channel 0, max instant",
            ),
        ]

    def test_decode_valid_data(self, valid_test_data: list[ADTypeTestData]) -> None:
        """Decode each valid test case and verify all fields match."""
        for case in valid_test_data:
            result = ChannelMapUpdateIndication.decode(case.input_data)
            assert result == case.expected_value, f"Failed: {case.description}"

    def test_decode_extra_bytes_ignored(self) -> None:
        """Trailing bytes beyond the 7-byte payload are ignored."""
        data = bytearray([
            0xFF, 0xFF, 0xFF, 0xFF, 0x1F,
            0x0A, 0x00,
            0xDE, 0xAD,  # extra
        ])
        result = ChannelMapUpdateIndication.decode(data)

        assert result.instant == 10
        assert result.channel_map == b"\xFF\xFF\xFF\xFF\x1F"


class TestChannelMapUpdateErrors:
    """Error-path tests for ChannelMapUpdateIndication.decode()."""

    def test_decode_empty_data_raises(self) -> None:
        """Empty bytearray raises InsufficientDataError — no channel map."""
        with pytest.raises(InsufficientDataError):
            ChannelMapUpdateIndication.decode(bytearray())

    def test_decode_truncated_instant_raises(self) -> None:
        """Channel map present but instant is truncated (only 1 of 2 bytes)."""
        data = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0x1F, 0x01])
        with pytest.raises(InsufficientDataError):
            ChannelMapUpdateIndication.decode(data)

    def test_decode_only_channel_map_raises(self) -> None:
        """Five-byte channel map with no instant bytes at all."""
        data = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0x1F])
        with pytest.raises(InsufficientDataError):
            ChannelMapUpdateIndication.decode(data)


class TestIsChannelUsed:
    """Tests for ChannelMapUpdateIndication.is_channel_used()."""

    @pytest.fixture
    def all_channels_indication(self) -> ChannelMapUpdateIndication:
        """Indication with all 37 data channels used."""
        return ChannelMapUpdateIndication(
            channel_map=b"\xFF\xFF\xFF\xFF\x1F",
            instant=0,
        )

    @pytest.fixture
    def no_channels_indication(self) -> ChannelMapUpdateIndication:
        """Indication with no channels used."""
        return ChannelMapUpdateIndication(
            channel_map=b"\x00\x00\x00\x00\x00",
            instant=0,
        )

    def test_channel_zero_used(self, all_channels_indication: ChannelMapUpdateIndication) -> None:
        """Channel 0 (lowest data channel) is used when all bits set."""
        assert all_channels_indication.is_channel_used(0) is True

    def test_channel_36_used(self, all_channels_indication: ChannelMapUpdateIndication) -> None:
        """Channel 36 (highest data channel) is used when all bits set."""
        assert all_channels_indication.is_channel_used(MAX_DATA_CHANNEL) is True

    def test_channel_zero_not_used(self, no_channels_indication: ChannelMapUpdateIndication) -> None:
        """Channel 0 is not used when all bits clear."""
        assert no_channels_indication.is_channel_used(0) is False

    def test_channel_36_not_used(self, no_channels_indication: ChannelMapUpdateIndication) -> None:
        """Channel 36 is not used when all bits clear."""
        assert no_channels_indication.is_channel_used(MAX_DATA_CHANNEL) is False

    def test_single_channel_set(self) -> None:
        """Only channel 8 (byte 1, bit 0) is used."""
        indication = ChannelMapUpdateIndication(
            channel_map=b"\x00\x01\x00\x00\x00",
            instant=0,
        )
        assert indication.is_channel_used(8) is True
        assert indication.is_channel_used(0) is False
        assert indication.is_channel_used(9) is False

    def test_channel_negative_raises(self) -> None:
        """Negative channel number raises ValueError."""
        indication = ChannelMapUpdateIndication(channel_map=b"\xFF\xFF\xFF\xFF\x1F", instant=0)
        with pytest.raises(ValueError, match="Channel must be 0-36"):
            indication.is_channel_used(-1)

    def test_channel_37_raises(self) -> None:
        """Channel 37 (first advertising channel) is out of data channel range."""
        indication = ChannelMapUpdateIndication(channel_map=b"\xFF\xFF\xFF\xFF\x1F", instant=0)
        with pytest.raises(ValueError, match="Channel must be 0-36"):
            indication.is_channel_used(37)

    def test_channel_255_raises(self) -> None:
        """Large channel number raises ValueError."""
        indication = ChannelMapUpdateIndication(channel_map=b"\xFF\xFF\xFF\xFF\x1F", instant=0)
        with pytest.raises(ValueError, match="Channel must be 0-36"):
            indication.is_channel_used(255)


class TestChannelMapConstants:
    """Tests for channel map layout constants."""

    def test_channel_map_length(self) -> None:
        """Channel map is 5 bytes (covers 40 bits for channels 0-36)."""
        assert CHANNEL_MAP_LENGTH == 5

    def test_instant_offset_follows_channel_map(self) -> None:
        """Instant field starts immediately after the 5-byte channel map."""
        assert CHANNEL_MAP_INSTANT_OFFSET == CHANNEL_MAP_LENGTH

    def test_max_data_channel(self) -> None:
        """Maximum data channel is 36 per Core Spec Vol 6, Part B §1.4.1."""
        assert MAX_DATA_CHANNEL == 36

"""Tests for Transport Discovery Data AD type decode (AD 0x26, CSS Part A §1.10).

Tests cover:
- Single and multiple transport block decoding
- TDS flag sub-fields: role, incomplete, transport state
- Empty and truncated data handling
- Partial trailing blocks (silently skipped per spec)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from bluetooth_sig.types.advertising.transport_discovery import (
    TDS_ROLE_MASK,
    TDS_STATE_MASK,
    TDSFlags,
    TransportBlock,
    TransportDiscoveryData,
)


@dataclass
class ADTypeTestData:
    """Test data for AD type decode — mirrors CharacteristicTestData."""

    input_data: bytearray
    expected_value: Any
    description: str = ""


class TestTransportDiscoveryDecode:
    """Tests for TransportDiscoveryData.decode()."""

    @pytest.fixture
    def valid_test_data(self) -> list[ADTypeTestData]:
        """Standard decode scenarios for transport discovery blocks."""
        return [
            ADTypeTestData(
                input_data=bytearray(
                    [
                        0x01,  # org_id = 1 (Bluetooth SIG)
                        0x02,  # flags = ROLE_PROVIDER
                        0x03,  # transport_data_length = 3
                        0xAA,
                        0xBB,
                        0xCC,  # transport_data
                    ]
                ),
                expected_value=TransportDiscoveryData(
                    blocks=[
                        TransportBlock(
                            organization_id=1,
                            flags=TDSFlags.ROLE_PROVIDER,
                            transport_data=b"\xaa\xbb\xcc",
                        ),
                    ]
                ),
                description="Single block, provider role, 3 bytes payload",
            ),
            ADTypeTestData(
                input_data=bytearray(
                    [
                        # Block 1
                        0x01,
                        0x03,
                        0x01,
                        0xFF,
                        # Block 2
                        0x02,
                        0x08,
                        0x02,
                        0x11,
                        0x22,
                    ]
                ),
                expected_value=TransportDiscoveryData(
                    blocks=[
                        TransportBlock(
                            organization_id=1,
                            flags=TDSFlags.ROLE_SEEKER_AND_PROVIDER,
                            transport_data=b"\xff",
                        ),
                        TransportBlock(
                            organization_id=2,
                            flags=TDSFlags.STATE_ON,
                            transport_data=b"\x11\x22",
                        ),
                    ]
                ),
                description="Two blocks with different roles and states",
            ),
            ADTypeTestData(
                input_data=bytearray(
                    [
                        0x01,
                        0x00,
                        0x00,  # org=1, flags=0, data_length=0
                    ]
                ),
                expected_value=TransportDiscoveryData(
                    blocks=[
                        TransportBlock(
                            organization_id=1,
                            flags=TDSFlags(0),
                            transport_data=b"",
                        ),
                    ]
                ),
                description="Single block with zero-length transport data",
            ),
        ]

    def test_decode_valid_data(self, valid_test_data: list[ADTypeTestData]) -> None:
        """Decode each valid test case and verify all fields match."""
        for case in valid_test_data:
            result = TransportDiscoveryData.decode(case.input_data)
            assert result == case.expected_value, f"Failed: {case.description}"

    def test_decode_empty_data_returns_no_blocks(self) -> None:
        """Empty payload produces zero blocks (no header bytes available)."""
        result = TransportDiscoveryData.decode(bytearray())
        assert result.blocks == []

    def test_decode_incomplete_trailing_header_skipped(self) -> None:
        """Fewer than 3 trailing bytes after a valid block are silently ignored."""
        data = bytearray(
            [
                0x01,
                0x02,
                0x00,  # valid block (0-length payload)
                0xFF,
                0xFE,  # 2 trailing bytes — not enough for a header
            ]
        )
        result = TransportDiscoveryData.decode(data)

        assert len(result.blocks) == 1
        assert result.blocks[0].organization_id == 1

    def test_decode_truncated_transport_data_clamped(self) -> None:
        """Transport data length exceeds remaining bytes — clamp to available."""
        data = bytearray(
            [
                0x01,
                0x00,
                0x05,  # header says 5 bytes of transport data
                0xAA,
                0xBB,  # only 2 available
            ]
        )
        result = TransportDiscoveryData.decode(data)

        assert len(result.blocks) == 1
        assert result.blocks[0].transport_data == b"\xaa\xbb"


class TestTransportBlockProperties:
    """Tests for TransportBlock flag property accessors."""

    def test_role_seeker(self) -> None:
        """Role bits return ROLE_SEEKER when bit 0 set."""
        block = TransportBlock(organization_id=1, flags=TDSFlags.ROLE_SEEKER)
        assert block.role == TDSFlags.ROLE_SEEKER

    def test_role_provider(self) -> None:
        """Role bits return ROLE_PROVIDER when bit 1 set."""
        block = TransportBlock(organization_id=1, flags=TDSFlags.ROLE_PROVIDER)
        assert block.role == TDSFlags.ROLE_PROVIDER

    def test_role_seeker_and_provider(self) -> None:
        """Role bits return ROLE_SEEKER_AND_PROVIDER when bits 0+1 set."""
        block = TransportBlock(organization_id=1, flags=TDSFlags.ROLE_SEEKER_AND_PROVIDER)
        assert block.role == TDSFlags.ROLE_SEEKER_AND_PROVIDER

    def test_role_not_specified(self) -> None:
        """Role bits return 0 when neither bit is set."""
        block = TransportBlock(organization_id=1, flags=TDSFlags(0))
        assert block.role == TDSFlags(0)

    def test_is_incomplete_true(self) -> None:
        """is_incomplete returns True when INCOMPLETE bit set."""
        block = TransportBlock(
            organization_id=1,
            flags=TDSFlags.ROLE_SEEKER | TDSFlags.INCOMPLETE,
        )
        assert block.is_incomplete is True

    def test_is_incomplete_false(self) -> None:
        """is_incomplete returns False when INCOMPLETE bit clear."""
        block = TransportBlock(organization_id=1, flags=TDSFlags.ROLE_SEEKER)
        assert block.is_incomplete is False

    def test_transport_state_on(self) -> None:
        """transport_state returns STATE_ON when bit 3 set."""
        block = TransportBlock(organization_id=1, flags=TDSFlags.STATE_ON)
        assert block.transport_state == TDSFlags.STATE_ON

    def test_transport_state_temporarily_unavailable(self) -> None:
        """transport_state returns STATE_TEMPORARILY_UNAVAILABLE when bit 4 set."""
        block = TransportBlock(
            organization_id=1,
            flags=TDSFlags.STATE_TEMPORARILY_UNAVAILABLE,
        )
        assert block.transport_state == TDSFlags.STATE_TEMPORARILY_UNAVAILABLE

    def test_transport_state_off(self) -> None:
        """transport_state returns 0 (off) when state bits are clear."""
        block = TransportBlock(organization_id=1, flags=TDSFlags.ROLE_PROVIDER)
        assert block.transport_state == TDSFlags(0)


class TestTDSFlagsMasks:
    """Tests for TDS flag mask constants."""

    def test_role_mask_covers_bits_0_and_1(self) -> None:
        """TDS_ROLE_MASK covers exactly bits 0-1."""
        assert int(TDS_ROLE_MASK) == 0x03

    def test_state_mask_covers_bits_3_and_4(self) -> None:
        """TDS_STATE_MASK covers exactly bits 3-4."""
        assert int(TDS_STATE_MASK) == 0x18

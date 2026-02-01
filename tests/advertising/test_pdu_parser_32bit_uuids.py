"""Tests for 32-bit UUID parsing in AdvertisingPDUParser.

Tests cover:
- Parsing incomplete 32-bit service UUIDs (AD type 0x04)
- Parsing complete 32-bit service UUIDs (AD type 0x05)
- Edge cases: empty data, malformed data, multiple UUIDs
"""

from __future__ import annotations

import pytest

from bluetooth_sig.advertising.pdu_parser import AdvertisingPDUParser
from bluetooth_sig.types.ad_types_constants import ADType
from bluetooth_sig.types.uuid import BluetoothUUID


class TestParse32BitServiceUUIDs:
    """Tests for 32-bit service UUID parsing."""

    @pytest.fixture
    def parser(self) -> AdvertisingPDUParser:
        """Create parser instance."""
        return AdvertisingPDUParser()

    def test_parse_single_complete_32bit_uuid(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing a single complete 32-bit service UUID.

        AD Type 0x05 = Complete List of 32-bit Service UUIDs
        """
        # Build advertising data: length + AD type + 4-byte UUID (little-endian)
        # Use test UUID value 0x12345678
        uuid_bytes = (0x12345678).to_bytes(4, byteorder="little")
        raw_data = bytes([5, ADType.COMPLETE_32BIT_SERVICE_UUIDS]) + uuid_bytes

        result = parser.parse_advertising_data(raw_data)

        assert len(result.ad_structures.core.service_uuids) == 1
        expected_uuid = BluetoothUUID(0x12345678)
        assert result.ad_structures.core.service_uuids[0] == expected_uuid

    def test_parse_single_incomplete_32bit_uuid(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing a single incomplete 32-bit service UUID.

        AD Type 0x04 = Incomplete List of 32-bit Service UUIDs
        """
        # Use test UUID value 0xABCD1234
        uuid_bytes = (0xABCD1234).to_bytes(4, byteorder="little")
        raw_data = bytes([5, ADType.INCOMPLETE_32BIT_SERVICE_UUIDS]) + uuid_bytes

        result = parser.parse_advertising_data(raw_data)

        assert len(result.ad_structures.core.service_uuids) == 1
        expected_uuid = BluetoothUUID(0xABCD1234)
        assert result.ad_structures.core.service_uuids[0] == expected_uuid

    def test_parse_multiple_32bit_uuids(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing multiple 32-bit service UUIDs in one AD structure."""
        # Two UUIDs: 0x11223344 and 0x55667788
        uuid1_bytes = (0x11223344).to_bytes(4, byteorder="little")
        uuid2_bytes = (0x55667788).to_bytes(4, byteorder="little")
        raw_data = bytes([9, ADType.COMPLETE_32BIT_SERVICE_UUIDS]) + uuid1_bytes + uuid2_bytes

        result = parser.parse_advertising_data(raw_data)

        assert len(result.ad_structures.core.service_uuids) == 2
        assert result.ad_structures.core.service_uuids[0] == BluetoothUUID(0x11223344)
        assert result.ad_structures.core.service_uuids[1] == BluetoothUUID(0x55667788)

    def test_parse_empty_32bit_uuid_data(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing empty 32-bit UUID data (length=1, only AD type).

        Edge case: AD structure with no UUID data.
        """
        raw_data = bytes([1, ADType.COMPLETE_32BIT_SERVICE_UUIDS])

        result = parser.parse_advertising_data(raw_data)

        # No UUIDs should be parsed from empty data
        assert len(result.ad_structures.core.service_uuids) == 0

    def test_parse_truncated_32bit_uuid(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing truncated 32-bit UUID (less than 4 bytes).

        Edge case: Malformed data with incomplete UUID.
        """
        # Only 3 bytes of UUID data (should be 4)
        raw_data = bytes([4, ADType.COMPLETE_32BIT_SERVICE_UUIDS, 0x12, 0x34, 0x56])

        result = parser.parse_advertising_data(raw_data)

        # Truncated UUID should not be parsed
        assert len(result.ad_structures.core.service_uuids) == 0

    def test_parse_32bit_uuid_with_partial_second_uuid(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing where second UUID is truncated.

        Edge case: First UUID complete, second UUID incomplete.
        """
        # First UUID complete (4 bytes), second UUID only 2 bytes
        uuid1_bytes = (0xDEADBEEF).to_bytes(4, byteorder="little")
        partial_uuid2 = bytes([0xAB, 0xCD])
        raw_data = bytes([7, ADType.COMPLETE_32BIT_SERVICE_UUIDS]) + uuid1_bytes + partial_uuid2

        result = parser.parse_advertising_data(raw_data)

        # Only the first complete UUID should be parsed
        assert len(result.ad_structures.core.service_uuids) == 1
        assert result.ad_structures.core.service_uuids[0] == BluetoothUUID(0xDEADBEEF)

    def test_parse_32bit_uuid_mixed_with_16bit(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing advertisement with both 16-bit and 32-bit UUIDs."""
        # 16-bit UUID: 0x180F (Battery Service)
        uuid_16bit = (0x180F).to_bytes(2, byteorder="little")
        ad_16bit = bytes([3, ADType.COMPLETE_16BIT_SERVICE_UUIDS]) + uuid_16bit

        # 32-bit UUID: 0x12345678
        uuid_32bit = (0x12345678).to_bytes(4, byteorder="little")
        ad_32bit = bytes([5, ADType.COMPLETE_32BIT_SERVICE_UUIDS]) + uuid_32bit

        raw_data = ad_16bit + ad_32bit

        result = parser.parse_advertising_data(raw_data)

        assert len(result.ad_structures.core.service_uuids) == 2
        assert BluetoothUUID(0x180F) in result.ad_structures.core.service_uuids
        assert BluetoothUUID(0x12345678) in result.ad_structures.core.service_uuids

    def test_parse_32bit_uuid_boundary_values(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing 32-bit UUIDs at boundary values (min/max)."""
        # Test minimum boundary value
        uuid_min = (0x00000000).to_bytes(4, byteorder="little")
        ad_min = bytes([5, ADType.COMPLETE_32BIT_SERVICE_UUIDS]) + uuid_min

        # Test maximum boundary value
        uuid_max = (0xFFFFFFFF).to_bytes(4, byteorder="little")
        ad_max = bytes([5, ADType.COMPLETE_32BIT_SERVICE_UUIDS]) + uuid_max

        result_min = parser.parse_advertising_data(ad_min)
        result_max = parser.parse_advertising_data(ad_max)

        assert len(result_min.ad_structures.core.service_uuids) == 1
        assert result_min.ad_structures.core.service_uuids[0] == BluetoothUUID(0x00000000)

        assert len(result_max.ad_structures.core.service_uuids) == 1
        assert result_max.ad_structures.core.service_uuids[0] == BluetoothUUID(0xFFFFFFFF)

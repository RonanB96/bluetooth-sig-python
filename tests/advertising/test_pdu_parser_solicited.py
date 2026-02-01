"""Tests for solicited UUID parsing in AdvertisingPDUParser.

Tests cover:
- Parsing solicited 16-bit service UUIDs (AD type 0x14)
- Parsing solicited 32-bit service UUIDs (AD type 0x1F)
- Parsing solicited 128-bit service UUIDs (AD type 0x15)
- Edge cases: empty data, malformed data, multiple UUIDs
"""

from __future__ import annotations

import pytest

from bluetooth_sig.advertising.pdu_parser import AdvertisingPDUParser
from bluetooth_sig.types.ad_types_constants import ADType
from bluetooth_sig.types.uuid import BluetoothUUID


class TestParseSolicited16BitUUIDs:
    """Tests for solicited 16-bit service UUID parsing (AD type 0x14)."""

    @pytest.fixture
    def parser(self) -> AdvertisingPDUParser:
        """Create parser instance."""
        return AdvertisingPDUParser()

    def test_parse_single_solicited_16bit_uuid(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing a single solicited 16-bit service UUID."""
        # UUID: 0x180D (Heart Rate Service)
        uuid_bytes = (0x180D).to_bytes(2, byteorder="little")
        raw_data = bytes([3, ADType.SOLICITED_SERVICE_UUIDS_16BIT]) + uuid_bytes

        result = parser.parse_advertising_data(raw_data)

        assert len(result.ad_structures.core.solicited_service_uuids) == 1
        assert result.ad_structures.core.solicited_service_uuids[0] == BluetoothUUID(0x180D)

    def test_parse_multiple_solicited_16bit_uuids(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing multiple solicited 16-bit service UUIDs."""
        # UUIDs: 0x180D (Heart Rate), 0x180F (Battery)
        uuid1_bytes = (0x180D).to_bytes(2, byteorder="little")
        uuid2_bytes = (0x180F).to_bytes(2, byteorder="little")
        raw_data = bytes([5, ADType.SOLICITED_SERVICE_UUIDS_16BIT]) + uuid1_bytes + uuid2_bytes

        result = parser.parse_advertising_data(raw_data)

        assert len(result.ad_structures.core.solicited_service_uuids) == 2
        assert BluetoothUUID(0x180D) in result.ad_structures.core.solicited_service_uuids
        assert BluetoothUUID(0x180F) in result.ad_structures.core.solicited_service_uuids

    def test_parse_empty_solicited_16bit_uuid_data(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing empty solicited 16-bit UUID data."""
        raw_data = bytes([1, ADType.SOLICITED_SERVICE_UUIDS_16BIT])

        result = parser.parse_advertising_data(raw_data)

        assert len(result.ad_structures.core.solicited_service_uuids) == 0

    def test_parse_truncated_solicited_16bit_uuid(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing truncated solicited 16-bit UUID (only 1 byte)."""
        raw_data = bytes([2, ADType.SOLICITED_SERVICE_UUIDS_16BIT, 0x0D])

        result = parser.parse_advertising_data(raw_data)

        # Truncated UUID should not be parsed
        assert len(result.ad_structures.core.solicited_service_uuids) == 0


class TestParseSolicited32BitUUIDs:
    """Tests for solicited 32-bit service UUID parsing (AD type 0x1F)."""

    @pytest.fixture
    def parser(self) -> AdvertisingPDUParser:
        """Create parser instance."""
        return AdvertisingPDUParser()

    def test_parse_single_solicited_32bit_uuid(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing a single solicited 32-bit service UUID."""
        # Use test UUID value 0x12345678
        uuid_bytes = (0x12345678).to_bytes(4, byteorder="little")
        raw_data = bytes([5, ADType.SOLICITED_SERVICE_UUIDS_32BIT]) + uuid_bytes

        result = parser.parse_advertising_data(raw_data)

        assert len(result.ad_structures.core.solicited_service_uuids) == 1
        assert result.ad_structures.core.solicited_service_uuids[0] == BluetoothUUID(0x12345678)

    def test_parse_multiple_solicited_32bit_uuids(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing multiple solicited 32-bit service UUIDs."""
        uuid1_bytes = (0xAABBCCDD).to_bytes(4, byteorder="little")
        uuid2_bytes = (0x11223344).to_bytes(4, byteorder="little")
        raw_data = bytes([9, ADType.SOLICITED_SERVICE_UUIDS_32BIT]) + uuid1_bytes + uuid2_bytes

        result = parser.parse_advertising_data(raw_data)

        assert len(result.ad_structures.core.solicited_service_uuids) == 2
        assert BluetoothUUID(0xAABBCCDD) in result.ad_structures.core.solicited_service_uuids
        assert BluetoothUUID(0x11223344) in result.ad_structures.core.solicited_service_uuids

    def test_parse_truncated_solicited_32bit_uuid(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing truncated solicited 32-bit UUID (only 3 bytes)."""
        raw_data = bytes([4, ADType.SOLICITED_SERVICE_UUIDS_32BIT, 0x12, 0x34, 0x56])

        result = parser.parse_advertising_data(raw_data)

        # Truncated UUID should not be parsed
        assert len(result.ad_structures.core.solicited_service_uuids) == 0


class TestParseSolicited128BitUUIDs:
    """Tests for solicited 128-bit service UUID parsing (AD type 0x15)."""

    @pytest.fixture
    def parser(self) -> AdvertisingPDUParser:
        """Create parser instance."""
        return AdvertisingPDUParser()

    def test_parse_single_solicited_128bit_uuid(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing a single solicited 128-bit service UUID."""
        # Custom 128-bit UUID
        uuid_bytes = bytes.fromhex("12345678123456781234567812345678")
        raw_data = bytes([17, ADType.SOLICITED_SERVICE_UUIDS_128BIT]) + uuid_bytes

        result = parser.parse_advertising_data(raw_data)

        assert len(result.ad_structures.core.solicited_service_uuids) == 1
        # 128-bit UUID is stored as hex string (uppercase)
        expected_uuid = BluetoothUUID("12345678123456781234567812345678")
        assert result.ad_structures.core.solicited_service_uuids[0] == expected_uuid

    def test_parse_multiple_solicited_128bit_uuids(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing multiple solicited 128-bit service UUIDs."""
        uuid1_bytes = bytes.fromhex("AABBCCDD112233445566778899AABBCC")
        uuid2_bytes = bytes.fromhex("11223344556677889900AABBCCDDEEFF")
        raw_data = bytes([33, ADType.SOLICITED_SERVICE_UUIDS_128BIT]) + uuid1_bytes + uuid2_bytes

        result = parser.parse_advertising_data(raw_data)

        assert len(result.ad_structures.core.solicited_service_uuids) == 2

    def test_parse_truncated_solicited_128bit_uuid(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing truncated solicited 128-bit UUID (only 15 bytes)."""
        # Only 15 bytes of UUID data (should be 16)
        uuid_bytes = bytes.fromhex("123456781234567812345678123456")  # 15 bytes
        raw_data = bytes([16, ADType.SOLICITED_SERVICE_UUIDS_128BIT]) + uuid_bytes

        result = parser.parse_advertising_data(raw_data)

        # Truncated UUID should not be parsed
        assert len(result.ad_structures.core.solicited_service_uuids) == 0


class TestSolicitedUUIDsMixedWithServiceUUIDs:
    """Tests for mixed solicited and service UUIDs in same advertisement."""

    @pytest.fixture
    def parser(self) -> AdvertisingPDUParser:
        """Create parser instance."""
        return AdvertisingPDUParser()

    def test_service_uuids_and_solicited_uuids_separate(self, parser: AdvertisingPDUParser) -> None:
        """Test that service UUIDs and solicited UUIDs are stored separately."""
        # Regular service UUID: 0x180F (Battery Service)
        service_uuid = (0x180F).to_bytes(2, byteorder="little")
        ad_service = bytes([3, ADType.COMPLETE_16BIT_SERVICE_UUIDS]) + service_uuid

        # Solicited UUID: 0x180D (Heart Rate Service)
        solicited_uuid = (0x180D).to_bytes(2, byteorder="little")
        ad_solicited = bytes([3, ADType.SOLICITED_SERVICE_UUIDS_16BIT]) + solicited_uuid

        raw_data = ad_service + ad_solicited

        result = parser.parse_advertising_data(raw_data)

        # Service UUIDs should only contain the advertised service
        assert len(result.ad_structures.core.service_uuids) == 1
        assert result.ad_structures.core.service_uuids[0] == BluetoothUUID(0x180F)

        # Solicited UUIDs should only contain the solicited service
        assert len(result.ad_structures.core.solicited_service_uuids) == 1
        assert result.ad_structures.core.solicited_service_uuids[0] == BluetoothUUID(0x180D)

    def test_all_solicited_uuid_sizes_together(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing 16-bit, 32-bit, and 128-bit solicited UUIDs together."""
        # 16-bit solicited
        solicited_16 = (0x180D).to_bytes(2, byteorder="little")
        ad_16 = bytes([3, ADType.SOLICITED_SERVICE_UUIDS_16BIT]) + solicited_16

        # 32-bit solicited
        solicited_32 = (0x12345678).to_bytes(4, byteorder="little")
        ad_32 = bytes([5, ADType.SOLICITED_SERVICE_UUIDS_32BIT]) + solicited_32

        # 128-bit solicited
        solicited_128 = bytes.fromhex("AABBCCDD112233445566778899AABBCC")
        ad_128 = bytes([17, ADType.SOLICITED_SERVICE_UUIDS_128BIT]) + solicited_128

        raw_data = ad_16 + ad_32 + ad_128

        result = parser.parse_advertising_data(raw_data)

        # All three solicited UUIDs should be parsed
        assert len(result.ad_structures.core.solicited_service_uuids) == 3

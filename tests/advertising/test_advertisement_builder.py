"""Tests for AdvertisementBuilder encoding functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.types.ad_types_constants import ADType
from bluetooth_sig.types.advertising.builder import (
    AD_STRUCTURE_MAX_DATA_SIZE,
    ADStructure,
    AdvertisementBuilder,
    encode_manufacturer_data,
    encode_service_uuids_16bit,
    encode_service_uuids_128bit,
)
from bluetooth_sig.types.advertising.flags import BLEAdvertisingFlags
from bluetooth_sig.types.company import CompanyIdentifier, ManufacturerData
from bluetooth_sig.types.uuid import BluetoothUUID


class TestADStructure:
    """Tests for ADStructure encoding."""

    def test_to_bytes_basic(self) -> None:
        """Test basic AD structure encoding."""
        structure = ADStructure(ad_type=ADType.FLAGS, data=b"\x06")
        encoded = structure.to_bytes()

        # Length byte (2 = 1 for type + 1 for data) + type + data
        assert encoded == bytes([0x02, ADType.FLAGS, 0x06])

    def test_to_bytes_with_name(self) -> None:
        """Test AD structure encoding with a name."""
        name = b"Test"
        structure = ADStructure(ad_type=ADType.COMPLETE_LOCAL_NAME, data=name)
        encoded = structure.to_bytes()

        assert encoded[0] == len(name) + 1  # Length includes type byte
        assert encoded[1] == ADType.COMPLETE_LOCAL_NAME
        assert encoded[2:] == name

    def test_len(self) -> None:
        """Test ADStructure __len__ returns total encoded length."""
        structure = ADStructure(ad_type=ADType.FLAGS, data=b"\x06")
        assert len(structure) == 3  # length byte + type byte + 1 byte data

    def test_data_too_long_raises(self) -> None:
        """Test that data exceeding max size raises ValueError."""
        long_data = bytes(AD_STRUCTURE_MAX_DATA_SIZE + 1)
        structure = ADStructure(ad_type=0x00, data=long_data)

        with pytest.raises(ValueError, match="AD structure data too long"):
            structure.to_bytes()


class TestAdvertisementBuilder:
    """Tests for AdvertisementBuilder fluent interface."""

    def test_empty_builder(self) -> None:
        """Test empty builder produces empty payload."""
        builder = AdvertisementBuilder()
        payload = builder.build()
        assert payload == b""

    def test_with_flags(self) -> None:
        """Test adding flags to advertisement."""
        builder = AdvertisementBuilder()
        builder = builder.with_flags(
            BLEAdvertisingFlags.LE_GENERAL_DISCOVERABLE_MODE | BLEAdvertisingFlags.BR_EDR_NOT_SUPPORTED
        )
        payload = builder.build()

        # Expect: length(2), type(0x01), flags(0x06)
        assert payload == bytes([0x02, ADType.FLAGS, 0x06])

    def test_with_complete_local_name(self) -> None:
        """Test adding complete local name."""
        builder = AdvertisementBuilder()
        builder = builder.with_complete_local_name("Test")
        payload = builder.build()

        expected = bytes([0x05, ADType.COMPLETE_LOCAL_NAME]) + b"Test"
        assert payload == expected

    def test_with_shortened_local_name(self) -> None:
        """Test adding shortened local name."""
        builder = AdvertisementBuilder()
        builder = builder.with_shortened_local_name("Tst")
        payload = builder.build()

        expected = bytes([0x04, ADType.SHORTENED_LOCAL_NAME]) + b"Tst"
        assert payload == expected

    def test_with_tx_power(self) -> None:
        """Test adding TX power level."""
        builder = AdvertisementBuilder()
        builder = builder.with_tx_power(-10)
        payload = builder.build()

        # TX power is signed byte, -10 is 0xF6 in two's complement
        expected = bytes([0x02, ADType.TX_POWER_LEVEL, 0xF6])
        assert payload == expected

    def test_with_16bit_service_uuids(self) -> None:
        """Test adding 16-bit service UUIDs."""
        builder = AdvertisementBuilder()
        builder = builder.with_service_uuids(["180F", "181A"])
        payload = builder.build()

        # Two 16-bit UUIDs in little-endian
        expected = bytes([0x05, ADType.COMPLETE_16BIT_SERVICE_UUIDS, 0x0F, 0x18, 0x1A, 0x18])
        assert payload == expected

    def test_with_128bit_service_uuid(self) -> None:
        """Test adding 128-bit service UUID."""
        builder = AdvertisementBuilder()
        # Non-SIG UUID (doesn't match SIG base)
        builder = builder.with_service_uuids(["12345678-1234-1234-1234-123456789abc"])
        payload = builder.build()

        # Should use 128-bit UUID type
        assert payload[1] == ADType.COMPLETE_128BIT_SERVICE_UUIDS
        assert len(payload) == 2 + 16  # length + type + 16-byte UUID

    def test_with_manufacturer_data(self) -> None:
        """Test adding manufacturer data."""
        builder = AdvertisementBuilder()
        builder = builder.with_manufacturer_data(0x004C, b"\x02\x15")
        payload = builder.build()

        # Length = 1(type) + 2(company ID) + 2(payload) = 5
        # Format: length, type, company_id_le, payload
        expected = bytes([0x05, ADType.MANUFACTURER_SPECIFIC_DATA, 0x4C, 0x00, 0x02, 0x15])
        assert payload == expected

    def test_with_manufacturer_data_company_identifier(self) -> None:
        """Test adding manufacturer data with CompanyIdentifier."""
        company = CompanyIdentifier.from_id(0x004C)
        builder = AdvertisementBuilder()
        builder = builder.with_manufacturer_data(company, b"\x01")
        payload = builder.build()

        assert payload[1] == ADType.MANUFACTURER_SPECIFIC_DATA
        assert payload[2:4] == b"\x4c\x00"  # Company ID little-endian

    def test_with_manufacturer_data_struct(self) -> None:
        """Test adding ManufacturerData struct."""
        mfr = ManufacturerData.from_id_and_payload(0x004C, b"\x01\x02\x03")
        builder = AdvertisementBuilder()
        builder = builder.with_manufacturer_data_struct(mfr)
        payload = builder.build()

        assert payload[1] == ADType.MANUFACTURER_SPECIFIC_DATA
        assert payload[2:4] == b"\x4c\x00"  # Company ID little-endian
        assert payload[4:] == b"\x01\x02\x03"  # Payload

    def test_chained_building(self) -> None:
        """Test chaining multiple builder methods."""
        payload = (
            AdvertisementBuilder()
            .with_flags(BLEAdvertisingFlags.LE_GENERAL_DISCOVERABLE_MODE)
            .with_complete_local_name("Sens")
            .with_service_uuids(["180F"])
            .build()
        )

        # Should have 3 AD structures
        assert len(payload) > 0
        # Decode and verify structure count
        structures = _decode_ad_structures(payload)
        assert len(structures) == 3

    def test_remaining_space(self) -> None:
        """Test remaining space calculation."""
        builder = AdvertisementBuilder()
        assert builder.remaining_space() == 31  # Legacy max

        builder = builder.with_flags(BLEAdvertisingFlags.LE_GENERAL_DISCOVERABLE_MODE)
        assert builder.remaining_space() == 28  # 31 - 3

    def test_current_size(self) -> None:
        """Test current payload size calculation."""
        builder = AdvertisementBuilder()
        assert builder.current_size() == 0

        builder = builder.with_flags(BLEAdvertisingFlags.LE_GENERAL_DISCOVERABLE_MODE)
        assert builder.current_size() == 3

    def test_extended_advertising(self) -> None:
        """Test extended advertising mode allows larger payloads."""
        builder = AdvertisementBuilder().with_extended_advertising()
        assert builder.remaining_space() == 254

        # Build a payload that exceeds legacy limit
        long_name = "A" * 50
        builder = builder.with_complete_local_name(long_name)
        payload = builder.build()

        assert len(payload) > 31

    def test_legacy_payload_too_large_raises(self) -> None:
        """Test that exceeding legacy limit raises error."""
        builder = AdvertisementBuilder()
        builder = builder.with_complete_local_name("A" * 40)  # Too long

        with pytest.raises(ValueError, match="Advertising payload too large"):
            builder.build()

    def test_immutability(self) -> None:
        """Test that builder operations return new instances."""
        builder1 = AdvertisementBuilder()
        builder2 = builder1.with_flags(BLEAdvertisingFlags.LE_GENERAL_DISCOVERABLE_MODE)

        assert builder1 is not builder2
        assert len(builder1.structures) == 0
        assert len(builder2.structures) == 1


class TestEncodingHelpers:
    """Tests for encoding helper functions."""

    def test_encode_manufacturer_data(self) -> None:
        """Test manufacturer data encoding."""
        encoded = encode_manufacturer_data(0x004C, b"\x02\x15")

        # Should be: company_id (2 bytes LE) + payload
        expected = b"\x4c\x00\x02\x15"
        assert encoded == expected

    def test_encode_service_uuids_16bit(self) -> None:
        """Test 16-bit service UUID encoding."""
        uuids = [BluetoothUUID("180F"), BluetoothUUID("181A")]
        encoded = encode_service_uuids_16bit(uuids)

        # Each UUID is 2 bytes little-endian
        expected = b"\x0f\x18\x1a\x18"
        assert encoded == expected

    def test_encode_service_uuids_128bit(self) -> None:
        """Test 128-bit service UUID encoding."""
        uuids = [BluetoothUUID("12345678-1234-1234-1234-123456789abc")]
        encoded = encode_service_uuids_128bit(uuids)

        assert len(encoded) == 16


class TestMixedUUIDs:
    """Tests for handling mixed 16-bit and 128-bit UUIDs."""

    def test_mixed_uuids_separate_structures(self) -> None:
        """Test that mixed UUIDs create separate AD structures."""
        builder = AdvertisementBuilder().with_extended_advertising()
        builder = builder.with_service_uuids(
            [
                "180F",  # 16-bit SIG UUID
                "12345678-1234-1234-1234-123456789abc",  # 128-bit custom
            ]
        )
        payload = builder.build()

        structures = _decode_ad_structures(payload)
        # Should have 2 structures: one for 16-bit, one for 128-bit
        assert len(structures) == 2

        types = [s[0] for s in structures]
        assert ADType.COMPLETE_16BIT_SERVICE_UUIDS in types
        assert ADType.COMPLETE_128BIT_SERVICE_UUIDS in types


def _decode_ad_structures(payload: bytes) -> list[tuple[int, bytes]]:
    """Decode AD structures from payload for testing.

    Returns list of (ad_type, data) tuples.
    """
    structures: list[tuple[int, bytes]] = []
    i = 0
    while i < len(payload):
        length = payload[i]
        if length == 0:
            break
        ad_type = payload[i + 1]
        data = payload[i + 2 : i + 1 + length]
        structures.append((ad_type, data))
        i += 1 + length
    return structures

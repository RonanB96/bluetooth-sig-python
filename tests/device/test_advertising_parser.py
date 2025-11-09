"""Tests for advertising data types and parsing utilities."""

from __future__ import annotations

from bluetooth_sig.device.advertising_parser import AdvertisingParser
from bluetooth_sig.types.advertising import (
    BLEAdvertisingFlags,
    BLEAdvertisingPDU,
    BLEExtendedHeader,
    ExtendedHeaderMode,
    ParsedADStructures,
    PDUType,
)


class TestPDUType:
    """Test PDU type enum and properties."""

    def test_extended_advertising_pdus(self) -> None:
        """Test identification of extended advertising PDU types."""
        assert PDUType.ADV_EXT_IND.is_extended_advertising is True
        assert PDUType.ADV_AUX_IND.is_extended_advertising is True
        assert PDUType.ADV_IND.is_extended_advertising is False
        assert PDUType.ADV_DIRECT_IND.is_extended_advertising is False

    def test_legacy_advertising_pdus(self) -> None:
        """Test identification of legacy advertising PDU types."""
        assert PDUType.ADV_IND.is_legacy_advertising is True
        assert PDUType.ADV_DIRECT_IND.is_legacy_advertising is True
        assert PDUType.ADV_NONCONN_IND.is_legacy_advertising is True
        assert PDUType.SCAN_REQ.is_legacy_advertising is True
        assert PDUType.SCAN_RSP.is_legacy_advertising is True
        assert PDUType.CONNECT_IND.is_legacy_advertising is True
        assert PDUType.ADV_SCAN_IND.is_legacy_advertising is True
        assert PDUType.ADV_EXT_IND.is_legacy_advertising is False
        assert PDUType.ADV_AUX_IND.is_legacy_advertising is False


class TestBLEExtendedHeader:
    """Test extended header functionality."""

    def test_extended_header_properties(self) -> None:
        """Test extended header property methods."""
        # Test with no flags set
        header = BLEExtendedHeader(adv_mode=0)
        assert header.has_extended_advertiser_address is False
        assert header.has_extended_target_address is False
        assert header.has_cte_info is False
        assert header.has_advertising_data_info is False
        assert header.has_auxiliary_pointer is False
        assert header.has_sync_info is False
        assert header.has_tx_power is False
        assert header.has_additional_controller_data is False

        # Test with all flags set
        header = BLEExtendedHeader(adv_mode=0xFF)
        assert header.has_extended_advertiser_address is True
        assert header.has_extended_target_address is True
        assert header.has_cte_info is True
        assert header.has_advertising_data_info is True
        assert header.has_auxiliary_pointer is True
        assert header.has_sync_info is True
        assert header.has_tx_power is True
        assert header.has_additional_controller_data is True

        # Test individual flags
        header = BLEExtendedHeader(adv_mode=ExtendedHeaderMode.ADV_ADDR)
        assert header.has_extended_advertiser_address is True
        assert header.has_extended_target_address is False

        header = BLEExtendedHeader(adv_mode=ExtendedHeaderMode.TARGET_ADDR)
        assert header.has_extended_advertiser_address is False
        assert header.has_extended_target_address is True


class TestBLEAdvertisingPDU:
    """Test BLE advertising PDU functionality."""

    def test_pdu_creation(self) -> None:
        """Test PDU creation and basic properties."""
        pdu = BLEAdvertisingPDU(
            pdu_type=PDUType.ADV_IND,
            tx_add=True,
            rx_add=False,
            length=10,
            payload=b"test_data",
        )

        assert pdu.pdu_type == PDUType.ADV_IND
        assert pdu.tx_add is True
        assert pdu.rx_add is False
        assert pdu.length == 10
        assert pdu.payload == b"test_data"

    def test_extended_advertising_detection(self) -> None:
        """Test detection of extended advertising PDUs."""
        extended_pdu = BLEAdvertisingPDU(pdu_type=PDUType.ADV_EXT_IND, tx_add=False, rx_add=False, length=5)
        assert extended_pdu.is_extended_advertising is True
        assert extended_pdu.is_legacy_advertising is False

        legacy_pdu = BLEAdvertisingPDU(pdu_type=PDUType.ADV_IND, tx_add=False, rx_add=False, length=5)
        assert legacy_pdu.is_extended_advertising is False
        assert legacy_pdu.is_legacy_advertising is True

    def test_pdu_name_property(self) -> None:
        """Test PDU name resolution."""
        pdu = BLEAdvertisingPDU(pdu_type=PDUType.ADV_IND, tx_add=False, rx_add=False, length=5)
        assert pdu.pdu_name == "ADV_IND"

        pdu = BLEAdvertisingPDU(pdu_type=PDUType.ADV_EXT_IND, tx_add=False, rx_add=False, length=5)
        assert pdu.pdu_name == "ADV_EXT_IND"


class TestParsedADStructures:
    """Test parsed advertising data structures."""

    def test_dataclass_creation(self) -> None:
        """Test creation of ParsedADStructures dataclass."""
        parsed = ParsedADStructures()
        assert parsed.manufacturer_data == {}
        assert parsed.manufacturer_name is None
        assert parsed.service_uuids == []
        assert parsed.local_name == ""
        assert parsed.tx_power == 0
        assert parsed.flags == 0

    def test_dataclass_with_data(self) -> None:
        """Test ParsedADStructures with populated data."""
        parsed = ParsedADStructures(
            manufacturer_data={0x1234: b"test_data"},
            manufacturer_name="Test Company",
            service_uuids=["180F", "180A"],
            local_name="Test Device",
            tx_power=-50,
            flags=BLEAdvertisingFlags(0x06),
        )

        assert parsed.manufacturer_data == {0x1234: b"test_data"}
        assert parsed.manufacturer_name == "Test Company"
        assert parsed.service_uuids == ["180F", "180A"]
        assert parsed.local_name == "Test Device"
        assert parsed.tx_power == -50
        assert parsed.flags == BLEAdvertisingFlags(0x06)


class TestAdvertisingParserWithManufacturerData:
    """Test advertising parser with manufacturer data and company name resolution."""

    def test_parse_apple_manufacturer_data(self) -> None:
        """Test parsing advertising data with Apple manufacturer data."""
        parser = AdvertisingParser()

        # Construct advertising data with Apple manufacturer data (0x004C)
        # AD Structure: Length (1) + Type (1) + Company ID (2 little-endian) + Data
        # Apple company ID: 0x004C = [0x4C, 0x00] in little-endian
        ad_data = bytearray(
            [
                # Manufacturer Specific Data (Type 0xFF)
                0x07,  # Length: 7 bytes total (type + company_id + data)
                0xFF,  # AD Type: Manufacturer Specific Data
                0x4C,
                0x00,  # Company ID: 0x004C (Apple) - little-endian
                0x12,
                0x02,
                0x00,
                0x00,  # Arbitrary manufacturer data
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        # Verify manufacturer data was parsed
        assert 0x004C in result.manufacturer_data
        assert result.manufacturer_data[0x004C] == b"\x12\x02\x00\x00"

        # Verify company name was resolved (if YAML loaded)
        if result.manufacturer_name:
            assert result.manufacturer_name == "Apple, Inc."

    def test_parse_microsoft_manufacturer_data(self) -> None:
        """Test parsing advertising data with Microsoft manufacturer data."""
        parser = AdvertisingParser()

        # Construct advertising data with Microsoft manufacturer data (0x0006)
        ad_data = bytearray(
            [
                0x05,  # Length: 5 bytes total
                0xFF,  # AD Type: Manufacturer Specific Data
                0x06,
                0x00,  # Company ID: 0x0006 (Microsoft) - little-endian
                0xAA,
                0xBB,  # Arbitrary manufacturer data
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        # Verify manufacturer data was parsed
        assert 0x0006 in result.manufacturer_data
        assert result.manufacturer_data[0x0006] == b"\xaa\xbb"

        # Verify company name was resolved (if YAML loaded)
        if result.manufacturer_name:
            assert result.manufacturer_name == "Microsoft"

    def test_parse_google_manufacturer_data(self) -> None:
        """Test parsing advertising data with Google manufacturer data."""
        parser = AdvertisingParser()

        # Construct advertising data with Google manufacturer data (0x00E0)
        ad_data = bytearray(
            [
                0x04,  # Length: 4 bytes total
                0xFF,  # AD Type: Manufacturer Specific Data
                0xE0,
                0x00,  # Company ID: 0x00E0 (Google) - little-endian
                0x01,  # Arbitrary manufacturer data
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        # Verify manufacturer data was parsed
        assert 0x00E0 in result.manufacturer_data
        assert result.manufacturer_data[0x00E0] == b"\x01"

        # Verify company name was resolved (if YAML loaded)
        if result.manufacturer_name:
            assert result.manufacturer_name == "Google"

    def test_parse_unknown_manufacturer_data(self) -> None:
        """Test parsing advertising data with unknown manufacturer ID."""
        parser = AdvertisingParser()

        # Construct advertising data with unknown manufacturer data (0xFFFF)
        ad_data = bytearray(
            [
                0x04,  # Length: 4 bytes total
                0xFF,  # AD Type: Manufacturer Specific Data
                0xFF,
                0xFF,  # Company ID: 0xFFFF (Unknown/Reserved)
                0x99,  # Arbitrary manufacturer data
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        # Verify manufacturer data was parsed
        assert 0xFFFF in result.manufacturer_data
        assert result.manufacturer_data[0xFFFF] == b"\x99"

        # Verify company name is None for unknown IDs
        assert result.manufacturer_name is None

    def test_parse_advertising_without_manufacturer_data(self) -> None:
        """Test parsing advertising data without manufacturer data."""
        parser = AdvertisingParser()

        # Construct advertising data with only local name (no manufacturer data)
        # Note: Length includes the type byte but not the length byte itself
        ad_data = bytearray(
            [
                0x09,  # Length: 9 bytes (type + 8 chars)
                0x09,  # AD Type: Complete Local Name
                ord("T"),
                ord("e"),
                ord("s"),
                ord("t"),
                ord("N"),
                ord("a"),
                ord("m"),
                ord("e"),
            ]
        )

        result = parser.parse_advertising_data(bytes(ad_data))

        # Verify no manufacturer data
        assert len(result.manufacturer_data) == 0
        assert result.manufacturer_name is None
        assert result.local_name == "TestName"

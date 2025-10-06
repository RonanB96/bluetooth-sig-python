"""Tests for advertising data types and parsing utilities."""

from __future__ import annotations

from bluetooth_sig.types.advertising import (
    BLEAdvertisingPDU,
    BLEExtendedHeader,
    ExtendedHeaderMode,
    ParsedADStructures,
    PDUType,
)


class TestPDUType:
    """Test PDU type enum and properties."""

    def test_extended_advertising_pdus(self):
        """Test identification of extended advertising PDU types."""
        assert PDUType.ADV_EXT_IND.is_extended_advertising is True
        assert PDUType.ADV_AUX_IND.is_extended_advertising is True
        assert PDUType.ADV_IND.is_extended_advertising is False
        assert PDUType.ADV_DIRECT_IND.is_extended_advertising is False

    def test_legacy_advertising_pdus(self):
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

    def test_extended_header_properties(self):
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

    def test_pdu_creation(self):
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

    def test_extended_advertising_detection(self):
        """Test detection of extended advertising PDUs."""
        extended_pdu = BLEAdvertisingPDU(pdu_type=PDUType.ADV_EXT_IND, tx_add=False, rx_add=False, length=5)
        assert extended_pdu.is_extended_advertising is True
        assert extended_pdu.is_legacy_advertising is False

        legacy_pdu = BLEAdvertisingPDU(pdu_type=PDUType.ADV_IND, tx_add=False, rx_add=False, length=5)
        assert legacy_pdu.is_extended_advertising is False
        assert legacy_pdu.is_legacy_advertising is True

    def test_pdu_name_property(self):
        """Test PDU name resolution."""
        pdu = BLEAdvertisingPDU(pdu_type=PDUType.ADV_IND, tx_add=False, rx_add=False, length=5)
        assert pdu.pdu_name == "ADV_IND"

        pdu = BLEAdvertisingPDU(pdu_type=PDUType.ADV_EXT_IND, tx_add=False, rx_add=False, length=5)
        assert pdu.pdu_name == "ADV_EXT_IND"


class TestParsedADStructures:
    """Test parsed advertising data structures."""

    def test_dataclass_creation(self):
        """Test creation of ParsedADStructures dataclass."""
        parsed = ParsedADStructures()
        assert parsed.manufacturer_data == {}
        assert parsed.service_uuids == []
        assert parsed.local_name == ""
        assert parsed.tx_power == 0
        assert parsed.flags == 0

    def test_dataclass_with_data(self):
        """Test ParsedADStructures with populated data."""
        parsed = ParsedADStructures(
            manufacturer_data={0x1234: b"test_data"},
            service_uuids=["180F", "180A"],
            local_name="Test Device",
            tx_power=-50,
            flags=0x06,
        )

        assert parsed.manufacturer_data == {0x1234: b"test_data"}
        assert parsed.service_uuids == ["180F", "180A"]
        assert parsed.local_name == "Test Device"
        assert parsed.tx_power == -50
        assert parsed.flags == 0x06

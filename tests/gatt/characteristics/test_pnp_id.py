"""Tests for PnP ID characteristic (0x2A50)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PnpIdCharacteristic, PnpIdData
from bluetooth_sig.gatt.characteristics.pnp_id import VendorIdSource
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPnpIdCharacteristic(CommonCharacteristicTests):
    """Test suite for PnP ID characteristic."""

    @pytest.fixture
    def characteristic(self) -> PnpIdCharacteristic:
        """Return a PnP ID characteristic instance."""
        return PnpIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for PnP ID characteristic."""
        return "2A50"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for PnP ID."""
        return [
            CharacteristicTestData(
                input_data=bytearray([1, 0x0A, 0x00, 0x0B, 0x00, 0x01, 0x00]),
                expected_value=PnpIdData(
                    vendor_id_source=VendorIdSource.BLUETOOTH_SIG,
                    vendor_id=0x000A,
                    product_id=0x000B,
                    product_version=0x0001,
                ),
                description="Bluetooth SIG vendor",
            ),
            CharacteristicTestData(
                input_data=bytearray([2, 0xAC, 0x05, 0x20, 0x02, 0x01, 0x00]),
                expected_value=PnpIdData(
                    vendor_id_source=VendorIdSource.USB_IF, vendor_id=0x05AC, product_id=0x0220, product_version=0x0001
                ),
                description="USB vendor device",
            ),
        ]

    def test_bluetooth_sig_vendor(self) -> None:
        """Test PnP ID with Bluetooth SIG vendor."""
        char = PnpIdCharacteristic()
        result = char.parse_value(bytearray([1, 0x0A, 0x00, 0x0B, 0x00, 0x01, 0x00]))
        assert result.vendor_id_source == VendorIdSource.BLUETOOTH_SIG
        assert result.vendor_id == 0x000A
        assert result.product_id == 0x000B
        assert result.product_version == 0x0001

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve data."""
        char = PnpIdCharacteristic()
        original = PnpIdData(
            vendor_id_source=VendorIdSource.USB_IF, vendor_id=0x1234, product_id=0x5678, product_version=0x0100
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

"""Tests for the Device class functionality."""

from __future__ import annotations

from bluetooth_sig import BluetoothSIGTranslator
from device import Device, DeviceEncryption


class TestDevice:
    """Test cases for the Device class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.translator = BluetoothSIGTranslator()
        self.device_address = "AA:BB:CC:DD:EE:FF"
        self.device = Device(self.device_address, self.translator)

    def test_device_initialization(self):
        """Test Device initialization."""
        assert self.device.address == self.device_address
        assert self.device.translator == self.translator
        assert self.device.name is None
        assert self.device.services == {}
        assert isinstance(self.device.encryption, DeviceEncryption)
        assert self.device.advertiser_data is None

    def test_device_string_representation(self):
        """Test Device string representation."""
        expected = (
            f"Device({self.device_address}, name=None, 0 services, 0 characteristics)"
        )
        assert str(self.device) == expected

        # Test with name and services
        self.device.name = "Test Device"
        expected = f"Device({self.device_address}, name=Test Device, 0 services, 0 characteristics)"
        assert str(self.device) == expected

    def test_parse_advertiser_data_basic(self):
        """Test basic advertiser data parsing."""
        # Sample advertisement data with local name
        adv_data = bytes(
            [
                0x02,
                0x01,
                0x06,  # Flags: 0x06
                0x0C,
                0x09,
                0x54,
                0x65,
                0x73,
                0x74,
                0x20,
                0x44,
                0x65,
                0x76,
                0x69,
                0x63,
                0x65,  # Complete Local Name: "Test Device"
            ]
        )

        self.device.parse_advertiser_data(adv_data)

        assert self.device.advertiser_data is not None
        assert self.device.advertiser_data.raw_data == adv_data
        assert self.device.advertiser_data.local_name == "Test Device"
        assert self.device.advertiser_data.flags == 0x06
        assert self.device.name == "Test Device"  # Should update device name

    def test_parse_advertiser_data_manufacturer(self):
        """Test advertiser data parsing with manufacturer data."""
        # Sample advertisement data with manufacturer data
        adv_data = bytes(
            [
                0x06,
                0xFF,
                0x4C,
                0x00,
                0x01,
                0x02,
                0x03,  # Manufacturer data: Company ID 0x004C (Apple), data [0x01, 0x02, 0x03]
            ]
        )

        self.device.parse_advertiser_data(adv_data)

        assert self.device.advertiser_data is not None
        assert self.device.advertiser_data.manufacturer_data[0x004C] == b"\x01\x02\x03"

    def test_parse_advertiser_data_service_uuids(self):
        """Test advertiser data parsing with service UUIDs."""
        # Sample advertisement data with 16-bit service UUIDs
        adv_data = bytes(
            [
                0x03,
                0x02,
                0x0F,
                0x18,  # Complete List of 16-bit Service UUIDs: 0x180F (Battery Service)
            ]
        )

        self.device.parse_advertiser_data(adv_data)

        assert self.device.advertiser_data is not None
        assert "180F" in self.device.advertiser_data.service_uuids

    def test_parse_advertiser_data_tx_power(self):
        """Test advertiser data parsing with TX power."""
        # Sample advertisement data with TX power
        adv_data = bytes(
            [
                0x02,
                0x0A,
                0xFC,  # TX Power Level: -4 dBm
            ]
        )

        self.device.parse_advertiser_data(adv_data)

        assert self.device.advertiser_data is not None
        assert self.device.advertiser_data.tx_power == -4

    def test_add_service_known_service(self):
        """Test adding a service with known service type."""
        # Battery service characteristics
        characteristics = {
            "2A19": b"\x64",  # Battery Level: 100%
        }

        self.device.add_service("180F", characteristics)

        assert "180F" in self.device.services
        service = self.device.services["180F"]
        assert len(service.characteristics) == 1
        assert "2A19" in service.characteristics

        # Check parsed data
        battery_data = service.characteristics["2A19"]
        assert battery_data.value == 100
        assert battery_data.name == "Battery Level"

    def test_add_service_unknown_service(self):
        """Test adding a service with unknown service type."""
        # Unknown service characteristics
        characteristics = {
            "1234": b"\x01\x02\x03",
        }

        self.device.add_service("ABCD", characteristics)

        assert "ABCD" in self.device.services
        service = self.device.services["ABCD"]
        assert len(service.characteristics) == 1
        assert "1234" in service.characteristics

    def test_get_characteristic_data(self):
        """Test retrieving characteristic data."""
        # Add a service first
        characteristics = {
            "2A19": b"\x64",  # Battery Level: 100%
        }
        self.device.add_service("180F", characteristics)

        # Retrieve the data
        data = self.device.get_characteristic_data("180F", "2A19")
        assert data is not None
        assert data.value == 100

        # Test non-existent service/characteristic
        assert self.device.get_characteristic_data("9999", "9999") is None
        assert self.device.get_characteristic_data("180F", "9999") is None

    def test_update_encryption_requirements(self):
        """Test encryption requirements tracking."""
        from bluetooth_sig.types import CharacteristicData

        # Create mock characteristic data with encryption properties
        char_data = CharacteristicData(
            uuid="2A19",
            name="Battery Level",
            value=100,
            properties=["read", "encrypt-read"],
        )

        self.device.update_encryption_requirements(char_data)

        assert self.device.encryption.requires_encryption is True

        # Test authentication requirement
        char_data_auth = CharacteristicData(
            uuid="2A19",
            name="Battery Level",
            value=100,
            properties=["read", "auth-read"],
        )

        self.device.update_encryption_requirements(char_data_auth)

        assert self.device.encryption.requires_authentication is True

    def test_device_with_advertiser_context(self):
        """Test device functionality with advertiser data context."""
        # Set up advertiser data first
        adv_data = bytes(
            [
                0x02,
                0x01,
                0x06,  # Flags
                0x0C,
                0x09,
                0x54,
                0x65,
                0x73,
                0x74,
                0x20,
                0x44,
                0x65,
                0x76,
                0x69,
                0x63,
                0x65,  # Local Name
                0x06,
                0xFF,
                0x4C,
                0x00,
                0x01,
                0x02,
                0x03,  # Manufacturer data
            ]
        )
        self.device.parse_advertiser_data(adv_data)

        # Add service - should use advertiser context
        characteristics = {
            "2A19": b"\x64",  # Battery Level
        }
        self.device.add_service("180F", characteristics)

        # Verify service was added and context was used
        assert "180F" in self.device.services
        assert self.device.name == "Test Device"

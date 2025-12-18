"""Integration tests for Class of Device parsing in advertising data."""

from __future__ import annotations

import pytest

from bluetooth_sig.advertising import AdvertisingPDUParser
from bluetooth_sig.types import AdvertisingData


class TestAdvertisingPDUParserClassOfDevice:
    """Test Class of Device parsing in advertising data."""

    @pytest.fixture
    def parser(self) -> AdvertisingPDUParser:
        """Create an advertising PDU parser instance."""
        return AdvertisingPDUParser()

    def test_parse_class_of_device_computer_laptop_networking(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing CoD for Computer: Laptop with Networking service.

        CoD 0x02010C breakdown:
        - Bits 23-13 (service): 0x020 = bit 17 set = Networking
        - Bits 12-8 (major): 0x01 = Computer
        - Bits 7-2 (minor): 0x03 = Laptop
        """
        # Build advertising data with CoD field
        # AD Structure: [length][type][data...]
        cod_value = 0x02010C
        cod_bytes = cod_value.to_bytes(3, byteorder="little")

        # AD Type 0x0D = Class of Device
        ad_data = bytes([4, 0x0D]) + cod_bytes

        result = parser.parse_advertising_data(ad_data)

        assert isinstance(result, AdvertisingData)
        assert result.ad_structures.properties.class_of_device is not None
        assert result.ad_structures.properties.class_of_device.raw_value == 0x02010C

        cod_info = result.ad_structures.properties.class_of_device
        assert cod_info.major_class and "Computer" in cod_info.major_class[0].name
        assert cod_info.minor_class and cod_info.minor_class[0].name == "Laptop"
        assert len(cod_info.service_classes) == 1
        assert any("Networking" in s for s in cod_info.service_classes)
        assert cod_info.raw_value == 0x02010C

        # Check full_description
        assert "Computer" in cod_info.full_description
        assert "Laptop" in cod_info.full_description
        assert "Networking" in cod_info.full_description

    def test_parse_class_of_device_phone_smartphone(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing CoD for Phone: Smartphone.

        CoD 0x00020C breakdown:
        - Bits 23-13: 0x000 = no services
        - Bits 12-8: 0x02 = Phone
        - Bits 7-2: 0x03 = Smartphone
        """
        cod_value = 0x00020C
        cod_bytes = cod_value.to_bytes(3, byteorder="little")
        ad_data = bytes([4, 0x0D]) + cod_bytes

        result = parser.parse_advertising_data(ad_data)

        assert result.ad_structures.properties.class_of_device is not None
        assert result.ad_structures.properties.class_of_device.raw_value == 0x00020C

        cod_info = result.ad_structures.properties.class_of_device
        assert cod_info.major_class and "Phone" in cod_info.major_class[0].name
        assert cod_info.minor_class and cod_info.minor_class[0].name == "Smartphone"
        assert cod_info.service_classes == []

    def test_parse_class_of_device_with_multiple_services(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing CoD with multiple service classes.

        CoD 0x22010C - Computer: Laptop with Networking + Audio services
        """
        cod_value = 0x22010C
        cod_bytes = cod_value.to_bytes(3, byteorder="little")
        ad_data = bytes([4, 0x0D]) + cod_bytes

        result = parser.parse_advertising_data(ad_data)

        assert result.ad_structures.properties.class_of_device is not None
        assert result.ad_structures.properties.class_of_device.raw_value == 0x22010C

        cod_info = result.ad_structures.properties.class_of_device
        assert cod_info.major_class and "Computer" in cod_info.major_class[0].name
        assert cod_info.minor_class and cod_info.minor_class[0].name == "Laptop"
        assert len(cod_info.service_classes) == 2
        assert any("Networking" in s for s in cod_info.service_classes)
        assert any("Audio" in s for s in cod_info.service_classes)

    def test_parse_no_class_of_device(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing advertising data without CoD field."""
        # Just a flags field
        ad_data = bytes([2, 0x01, 0x06])

        result = parser.parse_advertising_data(ad_data)

        assert result.ad_structures.properties.class_of_device is None

    def test_parse_class_of_device_with_other_fields(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing CoD alongside other advertising data fields."""
        # Multiple AD structures
        cod_value = 0x02010C
        cod_bytes = cod_value.to_bytes(3, byteorder="little")

        ad_data = (
            bytes([2, 0x01, 0x06])  # Flags
            + bytes([4, 0x0D])
            + cod_bytes  # CoD
            + bytes([8, 0x09])
            + b"TestDev"  # Name (length = 1 + 7 = 8)
        )

        result = parser.parse_advertising_data(ad_data)

        # All fields should be parsed
        assert result.ad_structures.properties.flags is not None
        assert result.ad_structures.core.local_name == "TestDev"
        assert result.ad_structures.properties.class_of_device is not None
        assert result.ad_structures.properties.class_of_device.raw_value == 0x02010C
        cod_info = result.ad_structures.properties.class_of_device
        assert cod_info.major_class and "Computer" in cod_info.major_class[0].name

    def test_parse_class_of_device_invalid_length(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing CoD with invalid length (should be ignored)."""
        # CoD should be 3 bytes, provide only 2
        ad_data = bytes([3, 0x0D, 0x0C, 0x01])

        result = parser.parse_advertising_data(ad_data)

        # Should not parse CoD if length is wrong
        assert result.ad_structures.properties.class_of_device is None

    def test_parse_class_of_device_health_device(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing CoD for Health: Blood Pressure Monitor.

        CoD for Health: Blood Pressure Monitor:
        - Bits 12-8: 0x09 = Health
        - Bits 7-2: 0x01 = Blood Pressure Monitor
        """
        cod_value = (0x09 << 8) | (0x01 << 2)
        cod_bytes = cod_value.to_bytes(3, byteorder="little")
        ad_data = bytes([4, 0x0D]) + cod_bytes

        result = parser.parse_advertising_data(ad_data)

        assert result.ad_structures.properties.class_of_device is not None
        cod_info = result.ad_structures.properties.class_of_device
        assert cod_info.major_class and "Health" in cod_info.major_class[0].name
        assert cod_info.minor_class is not None
        assert cod_info.minor_class and "Pressure" in cod_info.minor_class[0].name

    def test_parse_class_of_device_audio_headset(self, parser: AdvertisingPDUParser) -> None:
        """Test parsing CoD for Audio/Video: Wearable Headset with Audio service.

        CoD with Audio service (bit 21), Audio/Video major (0x04), Headset (0x01)
        """
        service_bits = 1 << (21 - 13)  # Bit 21 = Audio service
        major = 0x04  # Audio/Video
        minor = 0x01  # Wearable Headset
        cod_value = (service_bits << 13) | (major << 8) | (minor << 2)
        cod_bytes = cod_value.to_bytes(3, byteorder="little")
        ad_data = bytes([4, 0x0D]) + cod_bytes

        result = parser.parse_advertising_data(ad_data)

        assert result.ad_structures.properties.class_of_device is not None
        cod_info = result.ad_structures.properties.class_of_device
        assert (
            cod_info.major_class
            and "Audio" in cod_info.major_class[0].name
            or cod_info.major_class
            and "Video" in cod_info.major_class[0].name
        )
        assert cod_info.minor_class is not None
        assert cod_info.minor_class and "Headset" in cod_info.minor_class[0].name
        assert any("Audio" in s for s in cod_info.service_classes)

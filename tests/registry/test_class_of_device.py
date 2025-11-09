"""Tests for Class of Device registry functionality."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from bluetooth_sig.registry.core.class_of_device import ClassOfDeviceRegistry
from bluetooth_sig.types.class_of_device import ClassOfDeviceInfo


@pytest.fixture(scope="session")
def cod_registry() -> ClassOfDeviceRegistry:
    """Create a Class of Device registry once per test session."""
    return ClassOfDeviceRegistry()


class TestClassOfDeviceRegistry:
    """Test the ClassOfDeviceRegistry class."""

    def test_registry_initialization(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(cod_registry, ClassOfDeviceRegistry)

    def test_lazy_loading(self) -> None:
        """Test that registry loads data on first access."""
        # Create a new registry to test lazy loading
        new_registry = ClassOfDeviceRegistry()

        # First access should trigger loading
        result = new_registry.decode_class_of_device(0x02010C)
        assert isinstance(result, ClassOfDeviceInfo)

        # Subsequent calls should use cached data
        result2 = new_registry.decode_class_of_device(0x02010C)
        assert result.raw_value == result2.raw_value

    def test_decode_computer_laptop_networking(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test decoding Computer: Laptop with Networking service.

        CoD 0x02010C breakdown:
        - Bits 23-13 (service): 0x020 = bit 17 set = Networking
        - Bits 12-8 (major): 0x01 = Computer
        - Bits 7-2 (minor): 0x03 = Laptop
        """
        info = cod_registry.decode_class_of_device(0x02010C)

        assert isinstance(info, ClassOfDeviceInfo)
        assert "Computer" in info.major_class
        assert info.minor_class == "Laptop"
        # Service class names include full description from YAML
        assert len(info.service_classes) == 1
        assert any("Networking" in s for s in info.service_classes)
        assert info.raw_value == 0x02010C
        assert "Computer" in info.full_description
        assert "Laptop" in info.full_description
        assert "Networking" in info.full_description

    def test_decode_major_class_only(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test decoding major class without minor class.

        CoD 0x000100 (Computer with uncategorized minor class):
        - Bits 23-13: 0x000 = no services
        - Bits 12-8: 0x01 = Computer
        - Bits 7-2: 0x00 = Uncategorized
        """
        info = cod_registry.decode_class_of_device(0x000100)

        assert isinstance(info, ClassOfDeviceInfo)
        assert "Computer" in info.major_class
        # Minor class 0 might be "Uncategorized" or None depending on YAML
        assert info.service_classes == []
        assert info.raw_value == 0x000100

    def test_decode_phone_smartphone(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test decoding Phone: Smartphone.

        CoD 0x00020C breakdown:
        - Bits 23-13: 0x000 = no services
        - Bits 12-8: 0x02 = Phone
        - Bits 7-2: 0x03 = Smartphone
        """
        info = cod_registry.decode_class_of_device(0x00020C)

        assert isinstance(info, ClassOfDeviceInfo)
        assert "Phone" in info.major_class
        assert info.minor_class == "Smartphone"
        assert info.service_classes == []

    def test_decode_multiple_service_classes(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test decoding multiple service class bits.

        CoD with multiple service bits set:
        - Bit 17 (Networking) = position 4 in service field
        - Bit 21 (Audio) = position 8 in service field
        - Service bits = 0x110 (bits 4 and 8 set in 11-bit field)
        - CoD = (0x110 << 13) | (0x01 << 8) | (0x03 << 2) = 0x22010C
        """
        cod_value = 0x22010C  # Networking + Audio, Computer, Laptop
        info = cod_registry.decode_class_of_device(cod_value)

        assert isinstance(info, ClassOfDeviceInfo)
        assert "Computer" in info.major_class
        assert info.minor_class == "Laptop"
        # Should have both Networking and Audio (both contain descriptive text)
        assert len(info.service_classes) == 2
        assert any("Networking" in s for s in info.service_classes)
        assert any("Audio" in s for s in info.service_classes)

    def test_decode_audio_video_headset(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test decoding Audio/Video: Wearable Headset.

        CoD breakdown for Audio/Video device:
        - Bits 12-8: 0x04 = Audio/Video
        - Bits 7-2: 0x01 = Wearable Headset Device
        """
        cod_value = (0x04 << 8) | (0x01 << 2)  # Audio/Video, Wearable Headset
        info = cod_registry.decode_class_of_device(cod_value)

        assert isinstance(info, ClassOfDeviceInfo)
        assert "Audio" in info.major_class or "Video" in info.major_class
        assert info.minor_class is not None
        assert "Headset" in info.minor_class

    def test_decode_unknown_major_class(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test decoding unknown major class value."""
        # Use major class 0x1E which should be unknown
        cod_value = 0x1E << 8  # Unknown major class
        info = cod_registry.decode_class_of_device(cod_value)

        assert isinstance(info, ClassOfDeviceInfo)
        # Should return "Unknown (0xNN)" format
        assert "Unknown" in info.major_class or "0x1E" in info.major_class

    def test_decode_no_services(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test decoding CoD with no service classes."""
        cod_value = (0x01 << 8) | (0x03 << 2)  # Computer, Laptop, no services
        info = cod_registry.decode_class_of_device(cod_value)

        assert isinstance(info, ClassOfDeviceInfo)
        assert info.service_classes == []

    def test_full_description_property(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test the full_description property formatting."""
        # Computer: Laptop with Networking
        info = cod_registry.decode_class_of_device(0x02010C)

        desc = info.full_description
        assert isinstance(desc, str)
        assert "Computer" in desc
        assert "Laptop" in desc
        assert "Networking" in desc
        # Should have format: "Major: Minor (Service1, Service2)"
        assert ":" in desc
        assert "(" in desc
        assert ")" in desc

    def test_full_description_no_minor(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test full_description when minor class is not present."""
        # Networking service (bit 17), Phone (major 0x02), uncategorized (minor 0x00)
        cod_value = (0x010 << 13) | (0x02 << 8) | (0x00 << 2)
        info = cod_registry.decode_class_of_device(cod_value)

        desc = info.full_description
        # Should not have colon if no minor class or minor is "Uncategorized"
        # But should have service in parentheses
        assert any("Networking" in s for s in info.service_classes)
        assert "Networking" in desc

    def test_thread_safety_concurrent_decodes(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test thread safety with concurrent decode calls."""
        cod_values = [
            0x02010C,  # Computer: Laptop (Networking)
            0x00020C,  # Phone: Smartphone
            0x000400,  # Audio/Video
            0x000500,  # Peripheral
        ]

        def decode_cod(cod: int) -> ClassOfDeviceInfo:
            return cod_registry.decode_class_of_device(cod)

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(decode_cod, cod) for cod in cod_values]
            results = [future.result() for future in futures]

        # All results should be valid
        assert len(results) == 4
        for result in results:
            assert isinstance(result, ClassOfDeviceInfo)

    def test_decode_health_device(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test decoding Health device class.

        CoD for Health: Blood Pressure Monitor:
        - Bits 12-8: 0x09 = Health
        - Bits 7-2: 0x01 = Blood Pressure Monitor
        """
        cod_value = (0x09 << 8) | (0x01 << 2)  # Health, Blood Pressure Monitor
        info = cod_registry.decode_class_of_device(cod_value)

        assert isinstance(info, ClassOfDeviceInfo)
        assert "Health" in info.major_class
        assert info.minor_class is not None
        assert "Blood Pressure" in info.minor_class or "Pressure" in info.minor_class

    def test_bit_extraction_correctness(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test that bit extraction is done correctly.

        Create a CoD with known bit patterns and verify extraction:
        - Service: bit 13 (Limited Discoverable Mode)
        - Major: 0x01 (Computer)
        - Minor: 0x03 (Laptop)
        """
        # Bit 13 set = 0x2000, Major 0x01 = 0x100, Minor 0x03 = 0x0C
        cod_value = 0x2000 | 0x100 | 0x0C
        info = cod_registry.decode_class_of_device(cod_value)

        assert "Computer" in info.major_class
        assert info.minor_class == "Laptop"
        # Bit 13 should map to "Limited Discoverable Mode"
        assert len(info.service_classes) >= 1

    def test_decode_toy_robot(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test decoding Toy: Robot.

        CoD for Toy class:
        - Bits 12-8: 0x08 = Toy
        - Bits 7-2: 0x01 = Robot
        """
        cod_value = (0x08 << 8) | (0x01 << 2)  # Toy, Robot
        info = cod_registry.decode_class_of_device(cod_value)

        assert isinstance(info, ClassOfDeviceInfo)
        assert "Toy" in info.major_class
        assert info.minor_class is not None
        assert "Robot" in info.minor_class

    def test_decode_wearable_watch(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test decoding Wearable: Wristwatch.

        CoD for Wearable class:
        - Bits 12-8: 0x07 = Wearable
        - Bits 7-2: 0x01 = Wristwatch
        """
        cod_value = (0x07 << 8) | (0x01 << 2)  # Wearable, Wristwatch
        info = cod_registry.decode_class_of_device(cod_value)

        assert isinstance(info, ClassOfDeviceInfo)
        assert "Wearable" in info.major_class
        assert info.minor_class is not None
        assert "watch" in info.minor_class.lower() or "Wristwatch" in info.minor_class

    def test_raw_value_preserved(self, cod_registry: ClassOfDeviceRegistry) -> None:
        """Test that raw CoD value is preserved in the result."""
        test_values = [0x02010C, 0x00020C, 0x000400, 0x123456 & 0xFFFFFF]

        for cod_value in test_values:
            info = cod_registry.decode_class_of_device(cod_value)
            assert info.raw_value == cod_value

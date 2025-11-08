from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AppearanceCharacteristic
from bluetooth_sig.types.appearance import AppearanceData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAppearanceCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> AppearanceCharacteristic:
        return AppearanceCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A01"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        # Create AppearanceData objects as expected values
        from bluetooth_sig.registry import appearance_values_registry

        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=AppearanceData(raw_value=0, info=appearance_values_registry.get_appearance_info(0)),
                description="Unknown appearance (0x0000)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x40, 0x00]),
                expected_value=AppearanceData(raw_value=64, info=appearance_values_registry.get_appearance_info(64)),
                description="Phone (0x0040)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x41, 0x03]),
                expected_value=AppearanceData(raw_value=833, info=appearance_values_registry.get_appearance_info(833)),
                description="Heart Rate Sensor Belt (0x0341)",
            ),
        ]

    def test_decode_value_returns_appearance_data(self, characteristic: AppearanceCharacteristic) -> None:
        """Test that decode_value returns AppearanceData."""
        data = bytearray([0x40, 0x00])  # Phone (64)
        result = characteristic.decode_value(data)

        assert isinstance(result, AppearanceData)
        assert result.raw_value == 64

    def test_decode_with_known_appearance(self, characteristic: AppearanceCharacteristic) -> None:
        """Test decoding appearance with registry lookup."""
        # Heart Rate Sensor: Heart Rate Belt (833 = 0x0341)
        data = bytearray([0x41, 0x03])
        result = characteristic.decode_value(data)

        assert result.raw_value == 833
        # If registry is loaded, should have info
        if result.info:
            assert result.category == "Heart Rate Sensor"
            assert result.subcategory == "Heart Rate Belt"
            assert result.full_name == "Heart Rate Sensor: Heart Rate Belt"

    def test_decode_category_only_appearance(self, characteristic: AppearanceCharacteristic) -> None:
        """Test decoding appearance with category only (no subcategory)."""
        # Phone (64 = 0x0040)
        data = bytearray([0x40, 0x00])
        result = characteristic.decode_value(data)

        assert result.raw_value == 64
        if result.info:
            assert result.category == "Phone"
            assert result.subcategory is None
            assert result.full_name == "Phone"

    def test_decode_unknown_appearance(self, characteristic: AppearanceCharacteristic) -> None:
        """Test decoding unknown appearance code."""
        # Unknown (0 = 0x0000)
        data = bytearray([0x00, 0x00])
        result = characteristic.decode_value(data)

        assert result.raw_value == 0
        # Should still return AppearanceData even if unknown
        if result.info:
            assert result.category == "Unknown"

    def test_int_conversion(self, characteristic: AppearanceCharacteristic) -> None:
        """Test that AppearanceData can be converted to int."""
        data = bytearray([0x41, 0x03])
        result = characteristic.decode_value(data)

        assert int(result) == 833
        assert result.raw_value == 833

    def test_encode_value_with_appearance_data(self, characteristic: AppearanceCharacteristic) -> None:
        """Test encoding AppearanceData back to bytes."""
        data = bytearray([0x41, 0x03])
        appearance_data = characteristic.decode_value(data)

        # Encode it back
        encoded = characteristic.encode_value(appearance_data)
        assert encoded == data

    def test_properties_with_no_info(self, characteristic: AppearanceCharacteristic) -> None:
        """Test that properties return None when no registry info available."""
        # Use a code unlikely to be in registry
        data = bytearray([0xFF, 0xFF])
        result = characteristic.decode_value(data)

        assert result.raw_value == 65535
        # Properties should handle None gracefully
        if result.info is None:
            assert result.category is None
            assert result.subcategory is None
            assert result.full_name is None

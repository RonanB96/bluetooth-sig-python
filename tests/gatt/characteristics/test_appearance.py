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
        # Create AppearanceData objects directly with raw values to avoid registry dependency
        # This makes tests deterministic and independent of registry state
        from bluetooth_sig.types.registry.appearance_info import AppearanceInfo, AppearanceSubcategoryInfo

        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=AppearanceData(
                    raw_value=0,
                    info=AppearanceInfo(
                        category="Unknown",
                        category_value=0,
                        subcategory=None,
                    ),
                ),
                description="Unknown appearance (0x0000)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x40, 0x00]),
                expected_value=AppearanceData(
                    raw_value=64,
                    info=AppearanceInfo(
                        category="Phone",
                        category_value=1,
                        subcategory=None,
                    ),
                ),
                description="Phone (0x0040)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x41, 0x03]),
                expected_value=AppearanceData(
                    raw_value=833,
                    info=AppearanceInfo(
                        category="Heart Rate Sensor",
                        category_value=13,
                        subcategory=AppearanceSubcategoryInfo(name="Heart Rate Belt", value=1),
                    ),
                ),
                description="Heart Rate Sensor Belt (0x0341)",
            ),
        ]

    def test_decode_value_returns_appearance_data(self, characteristic: AppearanceCharacteristic) -> None:
        """Test that decode_value returns AppearanceData."""
        data = bytearray([0x40, 0x00])  # Phone (64)
        result = characteristic.parse_value(data)

        assert result.parse_success
        assert isinstance(result.value, AppearanceData)
        assert result.value.raw_value == 64

    def test_decode_with_known_appearance(self, characteristic: AppearanceCharacteristic) -> None:
        """Test decoding appearance with registry lookup."""
        # Heart Rate Sensor: Heart Rate Belt (833 = 0x0341)
        data = bytearray([0x41, 0x03])
        result = characteristic.parse_value(data)

        assert result.parse_success
        assert result.value is not None
        assert result.value.raw_value == 833
        # If registry is loaded, should have info
        if result.value.info:
            assert result.value.category == "Heart Rate Sensor"
            assert result.value.subcategory == "Heart Rate Belt"
            assert result.value.full_name == "Heart Rate Sensor: Heart Rate Belt"

    def test_decode_category_only_appearance(self, characteristic: AppearanceCharacteristic) -> None:
        """Test decoding appearance with category only (no subcategory)."""
        # Phone (64 = 0x0040)
        data = bytearray([0x40, 0x00])
        result = characteristic.parse_value(data)

        assert result.parse_success
        assert result.value is not None
        assert result.value.raw_value == 64
        if result.value.info:
            assert result.value.category == "Phone"
            assert result.value.subcategory is None
            assert result.value.full_name == "Phone"

    def test_decode_unknown_appearance(self, characteristic: AppearanceCharacteristic) -> None:
        """Test decoding unknown appearance code."""
        # Unknown (0 = 0x0000)
        data = bytearray([0x00, 0x00])
        result = characteristic.parse_value(data)

        assert result.parse_success
        assert result.value is not None
        assert result.value.raw_value == 0
        # Should still return AppearanceData even if unknown
        if result.value.info:
            assert result.value.category == "Unknown"

    def test_int_conversion(self, characteristic: AppearanceCharacteristic) -> None:
        """Test that AppearanceData can be converted to int."""
        data = bytearray([0x41, 0x03])
        result = characteristic.parse_value(data)

        assert result.parse_success
        assert result.value is not None
        assert int(result.value) == 833
        assert result.value.raw_value == 833

    def test_encode_value_with_appearance_data(self, characteristic: AppearanceCharacteristic) -> None:
        """Test encoding AppearanceData back to bytes."""
        data = bytearray([0x41, 0x03])
        result = characteristic.parse_value(data)
        assert result.value is not None
        appearance_data = result.value

        # Encode it back
        encoded = characteristic.build_value(appearance_data)
        assert encoded == data

    def test_from_category_helper(self, characteristic: AppearanceCharacteristic) -> None:
        """Test creating AppearanceData from human-readable category strings."""
        # Create from category only
        phone_data = AppearanceData.from_category("Phone")
        assert phone_data.raw_value == 64
        assert phone_data.category == "Phone"
        assert phone_data.subcategory is None

        # Create from category + subcategory
        hr_belt_data = AppearanceData.from_category("Heart Rate Sensor", "Heart Rate Belt")
        assert hr_belt_data.raw_value == 833
        assert hr_belt_data.category == "Heart Rate Sensor"
        assert hr_belt_data.subcategory == "Heart Rate Belt"

        # Encode and decode round-trip with human-readable data
        encoded = characteristic.build_value(hr_belt_data)
        result = characteristic.parse_value(encoded)
        assert result.parse_success
        assert result.value is not None
        assert result.value.full_name == hr_belt_data.full_name
        assert result.value.raw_value == hr_belt_data.raw_value

    def test_from_category_invalid(self) -> None:
        """Test that from_category raises ValueError for invalid categories."""
        with pytest.raises(ValueError, match="Unknown appearance"):
            AppearanceData.from_category("NonexistentCategory")

        with pytest.raises(ValueError, match="Unknown appearance"):
            AppearanceData.from_category("Phone", "NonexistentSubcategory")

    def test_properties_with_no_info(self, characteristic: AppearanceCharacteristic) -> None:
        """Test that properties return None when no registry info available."""
        # Use a code unlikely to be in registry
        data = bytearray([0xFF, 0xFF])
        result = characteristic.parse_value(data)

        assert result.parse_success
        assert result.value is not None
        assert result.value.raw_value == 65535
        # Properties should handle None gracefully
        if result.value.info is None:
            assert result.value.category is None
            assert result.value.subcategory is None
            assert result.value.full_name is None

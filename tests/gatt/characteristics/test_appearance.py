from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AppearanceCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
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
        # Note: expected_value is now AppearanceData, but we compare by raw_value
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]), expected_value=0, description="Unknown appearance (0x0000)"
            ),
            CharacteristicTestData(input_data=bytearray([0x40, 0x00]), expected_value=64, description="Phone (0x0040)"),
            CharacteristicTestData(
                input_data=bytearray([0x41, 0x03]),
                expected_value=833,
                description="Heart Rate Sensor Belt (0x0341)",
            ),
        ]

    # Override the common test to handle AppearanceData return type
    def test_valid_data_parsing(
        self, characteristic: AppearanceCharacteristic, valid_test_data: list[CharacteristicTestData]
    ) -> None:
        """Test that valid data is parsed correctly - overridden for AppearanceData."""
        for test_case in valid_test_data:
            result = characteristic.decode_value(test_case.input_data)
            # Compare by raw_value since result is AppearanceData
            assert isinstance(result, AppearanceData), f"Failed for {test_case.description}"
            assert result.raw_value == test_case.expected_value, f"Failed for {test_case.description}"

    def test_parse_valid_data_succeeds(
        self, characteristic: BaseCharacteristic, valid_test_data: list[CharacteristicTestData]
    ) -> None:
        """Test parsing valid data succeeds - overridden for AppearanceData."""
        for test_case in valid_test_data:
            result = characteristic.parse_value(test_case.input_data)
            assert not result.field_errors, f"Should not have errors for {test_case.description}"
            # Value should be AppearanceData with correct raw_value
            assert isinstance(result.value, AppearanceData), f"Failed for {test_case.description}"
            assert result.value.raw_value == test_case.expected_value, f"Failed for {test_case.description}"

    def test_decode_valid_data_returns_expected_value(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData | list[CharacteristicTestData]
    ) -> None:
        """Test raw decoding returns expected value - overridden for AppearanceData."""
        test_cases = valid_test_data if isinstance(valid_test_data, list) else [valid_test_data]
        for test_case in test_cases:
            result = characteristic.decode_value(test_case.input_data)
            assert isinstance(result, AppearanceData), f"Failed for {test_case.description}"
            assert result.raw_value == test_case.expected_value, f"Failed for {test_case.description}"

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

    def test_encode_value_with_int(self, characteristic: AppearanceCharacteristic) -> None:
        """Test encoding integer appearance value."""
        encoded = characteristic.encode_value(833)
        assert encoded == bytearray([0x41, 0x03])

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

"""Tests for the shared SIG resolver utilities.

This module tests the name normalization, variant generation, and registry search
strategies that are shared between characteristic and service resolution.
"""

import pytest

from bluetooth_sig.gatt.resolver import (
    CharacteristicRegistrySearch,
    NameNormalizer,
    NameVariantGenerator,
    ServiceRegistrySearch,
)
from bluetooth_sig.types import CharacteristicInfo, ServiceInfo
from bluetooth_sig.types.gatt_enums import ValueType


class TestNameNormalizer:
    """Tests for NameNormalizer utility class."""

    def test_camel_case_to_display_name_simple(self):
        """Test simple camelCase conversion."""
        assert NameNormalizer.camel_case_to_display_name("BatteryLevel") == "Battery Level"
        assert NameNormalizer.camel_case_to_display_name("Temperature") == "Temperature"
        assert NameNormalizer.camel_case_to_display_name("DeviceInformation") == "Device Information"

    def test_camel_case_to_display_name_with_acronyms(self):
        """Test camelCase conversion with acronyms."""
        assert NameNormalizer.camel_case_to_display_name("VOCConcentration") == "VOC Concentration"
        assert NameNormalizer.camel_case_to_display_name("CO2Concentration") == "CO2 Concentration"
        assert NameNormalizer.camel_case_to_display_name("PM25Concentration") == "PM25 Concentration"

    def test_camel_case_to_display_name_with_numbers(self):
        """Test camelCase conversion with numbers."""
        assert NameNormalizer.camel_case_to_display_name("NO2Concentration") == "NO2 Concentration"
        assert NameNormalizer.camel_case_to_display_name("PM10Concentration") == "PM10 Concentration"

    def test_camel_case_to_display_name_edge_cases(self):
        """Test edge cases for camelCase conversion."""
        assert NameNormalizer.camel_case_to_display_name("A") == "A"
        assert NameNormalizer.camel_case_to_display_name("AB") == "AB"
        assert NameNormalizer.camel_case_to_display_name("ABC") == "ABC"
        assert NameNormalizer.camel_case_to_display_name("") == ""

    def test_remove_suffix_characteristic(self):
        """Test removing 'Characteristic' suffix."""
        assert NameNormalizer.remove_suffix("BatteryLevelCharacteristic", "Characteristic") == "BatteryLevel"
        assert NameNormalizer.remove_suffix("TemperatureCharacteristic", "Characteristic") == "Temperature"
        assert NameNormalizer.remove_suffix("BatteryLevel", "Characteristic") == "BatteryLevel"

    def test_remove_suffix_service(self):
        """Test removing 'Service' suffix."""
        assert NameNormalizer.remove_suffix("BatteryService", "Service") == "Battery"
        assert NameNormalizer.remove_suffix("DeviceInformationService", "Service") == "DeviceInformation"
        assert NameNormalizer.remove_suffix("Battery", "Service") == "Battery"

    def test_remove_suffix_empty(self):
        """Test removing suffix from empty string."""
        assert NameNormalizer.remove_suffix("", "Characteristic") == ""

    def test_to_org_format_characteristic(self):
        """Test org format generation for characteristics."""
        words = ["Battery", "Level"]
        result = NameNormalizer.to_org_format(words, "characteristic")
        assert result == "org.bluetooth.characteristic.battery_level"

    def test_to_org_format_service(self):
        """Test org format generation for services."""
        words = ["Device", "Information"]
        result = NameNormalizer.to_org_format(words, "service")
        assert result == "org.bluetooth.service.device_information"

    def test_to_org_format_single_word(self):
        """Test org format with single word."""
        words = ["Battery"]
        result = NameNormalizer.to_org_format(words, "service")
        assert result == "org.bluetooth.service.battery"

    def test_to_org_format_with_acronyms(self):
        """Test org format with acronyms."""
        words = ["VOC", "Concentration"]
        result = NameNormalizer.to_org_format(words, "characteristic")
        assert result == "org.bluetooth.characteristic.voc_concentration"


class TestNameVariantGenerator:
    """Tests for NameVariantGenerator utility class."""

    def test_generate_characteristic_variants_basic(self):
        """Test characteristic variant generation for basic names."""
        variants = NameVariantGenerator.generate_characteristic_variants("BatteryLevelCharacteristic")

        # Should include all expected formats
        assert "Battery Level" in variants  # Space-separated display name
        assert "BatteryLevel" in variants  # Without suffix
        assert "org.bluetooth.characteristic.battery_level" in variants  # Org format
        assert "BatteryLevelCharacteristic" in variants  # Original name

    def test_generate_characteristic_variants_with_explicit_name(self):
        """Test characteristic variant generation with explicit name override."""
        variants = NameVariantGenerator.generate_characteristic_variants(
            "BatteryLevelCharacteristic", explicit_name="Battery Level"
        )

        # Explicit name should be first
        assert variants[0] == "Battery Level"

    def test_generate_characteristic_variants_without_suffix(self):
        """Test characteristic variant generation when class name has no suffix."""
        variants = NameVariantGenerator.generate_characteristic_variants("Temperature")

        assert "Temperature" in variants
        # Should not have duplicates
        assert len(variants) == len(set(variants))

    def test_generate_characteristic_variants_with_acronym(self):
        """Test characteristic variant generation with acronyms."""
        variants = NameVariantGenerator.generate_characteristic_variants("VOCConcentrationCharacteristic")

        assert "VOC Concentration" in variants
        assert "VOCConcentration" in variants
        assert "org.bluetooth.characteristic.voc_concentration" in variants

    def test_generate_characteristic_variants_no_duplicates(self):
        """Test that variant generation removes duplicates."""
        variants = NameVariantGenerator.generate_characteristic_variants("Temperature")

        # Should not have duplicates
        assert len(variants) == len(set(variants))

    def test_generate_service_variants_basic(self):
        """Test service variant generation for basic names."""
        variants = NameVariantGenerator.generate_service_variants("BatteryService")

        assert "Battery" in variants  # Space-separated display name
        assert "Battery Service" in variants  # Display name with suffix
        assert "BatteryService" in variants  # Original name
        assert "org.bluetooth.service.battery" in variants  # Org format

    def test_generate_service_variants_with_explicit_name(self):
        """Test service variant generation with explicit name override."""
        variants = NameVariantGenerator.generate_service_variants("BatteryService", explicit_name="Battery Service")

        # Explicit name should be first
        assert variants[0] == "Battery Service"

    def test_generate_service_variants_multi_word(self):
        """Test service variant generation with multi-word names."""
        variants = NameVariantGenerator.generate_service_variants("DeviceInformationService")

        assert "Device Information" in variants
        assert "DeviceInformation" in variants
        assert "Device Information Service" in variants
        assert "org.bluetooth.service.device_information" in variants

    def test_generate_service_variants_no_duplicates(self):
        """Test that service variant generation removes duplicates."""
        variants = NameVariantGenerator.generate_service_variants("BatteryService")

        # Should not have duplicates
        assert len(variants) == len(set(variants))


# Mock classes for testing - these need to be actual classes with __name__
# We can't set __name__ as a class attribute, so we create classes with the right names
class BatteryLevelCharacteristic:
    """Mock characteristic class for testing."""

    example_uuid = "2A19"


class BatteryService:
    """Mock service class for testing."""

    example_uuid = "180F"


class TestCharacteristicRegistrySearch:
    """Tests for CharacteristicRegistrySearch strategy."""

    def test_search_finds_known_characteristic(self):
        """Test that search finds a known characteristic in the registry."""
        strategy = CharacteristicRegistrySearch()
        result = strategy.search(BatteryLevelCharacteristic, explicit_name=None)

        # Battery Level is a standard characteristic
        assert result is not None
        assert isinstance(result, CharacteristicInfo)
        assert result.name == "Battery Level"

    def test_search_with_explicit_name(self):
        """Test search with explicit name override."""
        strategy = CharacteristicRegistrySearch()

        class CustomClass:
            __name__ = "CustomCharacteristic"

        result = strategy.search(CustomClass, explicit_name="Battery Level")

        assert result is not None
        assert result.name == "Battery Level"

    def test_search_returns_none_for_unknown(self):
        """Test that search returns None for unknown characteristics."""
        strategy = CharacteristicRegistrySearch()

        class UnknownClass:
            __name__ = "CompletelyUnknownCharacteristic"

        result = strategy.search(UnknownClass, explicit_name=None)

        assert result is None

    def test_search_returns_characteristic_info(self):
        """Test that search returns properly structured CharacteristicInfo."""
        strategy = CharacteristicRegistrySearch()
        result = strategy.search(BatteryLevelCharacteristic, explicit_name=None)

        assert result is not None
        assert hasattr(result, "uuid")
        assert hasattr(result, "name")
        assert hasattr(result, "unit")
        assert hasattr(result, "value_type")
        assert isinstance(result.value_type, ValueType)


class TestServiceRegistrySearch:
    """Tests for ServiceRegistrySearch strategy."""

    def test_search_finds_known_service(self):
        """Test that search finds a known service in the registry."""
        strategy = ServiceRegistrySearch()
        result = strategy.search(BatteryService, explicit_name=None)

        # Battery Service is a standard service
        assert result is not None
        assert isinstance(result, ServiceInfo)
        assert "Battery" in result.name

    def test_search_with_explicit_name(self):
        """Test search with explicit name override."""
        strategy = ServiceRegistrySearch()

        class CustomClass:
            __name__ = "CustomService"

        # Use actual registry name "Battery" not "Battery Service"
        result = strategy.search(CustomClass, explicit_name="Battery")

        assert result is not None
        assert "Battery" in result.name

    def test_search_returns_none_for_unknown(self):
        """Test that search returns None for unknown services."""
        strategy = ServiceRegistrySearch()

        class UnknownClass:
            __name__ = "CompletelyUnknownService"

        result = strategy.search(UnknownClass, explicit_name=None)

        assert result is None

    def test_search_returns_service_info(self):
        """Test that search returns properly structured ServiceInfo."""
        strategy = ServiceRegistrySearch()
        result = strategy.search(BatteryService, explicit_name=None)

        assert result is not None
        assert hasattr(result, "uuid")
        assert hasattr(result, "name")
        assert hasattr(result, "description")


class TestResolverIntegration:
    """Integration tests for resolver utilities working together."""

    def test_characteristic_resolution_pipeline(self):
        """Test complete characteristic resolution pipeline."""
        # 1. Generate variants
        variants = NameVariantGenerator.generate_characteristic_variants("BatteryLevelCharacteristic")

        # 2. Verify expected variants exist
        assert "Battery Level" in variants

        # 3. Search using strategy
        strategy = CharacteristicRegistrySearch()

        result = strategy.search(BatteryLevelCharacteristic, None)

        assert result is not None
        assert "Battery Level" in result.name

    def test_service_resolution_pipeline(self):
        """Test complete service resolution pipeline."""
        # 1. Generate variants
        variants = NameVariantGenerator.generate_service_variants("BatteryService")

        # 2. Verify expected variants exist
        assert "Battery" in variants

        # 3. Search using strategy
        strategy = ServiceRegistrySearch()

        result = strategy.search(BatteryService, None)

        assert result is not None
        assert "Battery" in result.name

    def test_name_normalization_consistency(self):
        """Test that name normalization is consistent across different paths."""
        # Test characteristic path
        char_name = "BatteryLevelCharacteristic"
        base_name = NameNormalizer.remove_suffix(char_name, "Characteristic")
        display_name = NameNormalizer.camel_case_to_display_name(base_name)

        assert display_name == "Battery Level"

        # Test service path
        svc_name = "BatteryService"
        svc_base = NameNormalizer.remove_suffix(svc_name, "Service")
        svc_display = NameNormalizer.camel_case_to_display_name(svc_base)

        assert svc_display == "Battery"

    def test_variant_generation_order_preserved(self):
        """Test that variant generation preserves priority order."""
        variants = NameVariantGenerator.generate_characteristic_variants(
            "BatteryLevelCharacteristic", explicit_name="Custom Name"
        )

        # Explicit name should always be first
        assert variants[0] == "Custom Name"

        # Verify subsequent entries exist (order matters for hit rate optimization)
        assert len(variants) > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

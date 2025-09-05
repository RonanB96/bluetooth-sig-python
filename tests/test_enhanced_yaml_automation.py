"""Tests for enhanced YAML automation features in Phase 1.2."""

import pytest

from bluetooth_sig.gatt.characteristics.enhanced_temperature import (
    EnhancedTemperatureCharacteristic,
)
from bluetooth_sig.registry.yaml_cross_reference import (
    YAMLCrossReferenceResolver,
    yaml_cross_reference,
)


class TestEnhancedYAMLAutomation:
    """Test enhanced YAML automation with cross-file references."""

    def test_yaml_cross_reference_resolver_initialization(self):
        """Test that YAMLCrossReferenceResolver initializes correctly."""
        resolver = YAMLCrossReferenceResolver()
        
        # Should have loaded YAML data
        assert len(resolver._characteristic_uuids) > 0, "Should load characteristic UUIDs"
        assert len(resolver._gss_specs) > 0, "Should load GSS specifications"
        
        # Should find Temperature characteristic
        assert "Temperature" in resolver._characteristic_uuids, "Should find Temperature UUID"
        assert resolver._characteristic_uuids["Temperature"] == "2A6E", "Temperature UUID should be 2A6E"

    def test_enhanced_spec_resolution(self):
        """Test enhanced specification resolution with cross-file references."""
        spec = yaml_cross_reference.resolve_characteristic_spec("Temperature")
        
        assert spec is not None, "Should resolve Temperature specification"
        assert spec.uuid == "2A6E", "Should resolve correct UUID"
        assert spec.data_type == "sint16", "Should resolve data type from GSS YAML"
        assert spec.field_size == "2", "Should resolve field size from GSS YAML"
        assert spec.unit_symbol == "°C", "Should resolve unit symbol via cross-reference"
        assert "org.bluetooth.unit.thermodynamic_temperature.degree_celsius" in spec.unit_id, "Should resolve unit ID"

    def test_enhanced_characteristic_automation(self):
        """Test that enhanced characteristics use YAML automation correctly."""
        char = EnhancedTemperatureCharacteristic(uuid="", properties=set())
        
        # UUID resolution
        assert char.char_uuid == "2A6E", "Should auto-resolve UUID from YAML"
        
        # Unit symbol resolution via cross-file references
        assert char.unit == "°C", "Should auto-resolve unit symbol via cross-reference"
        
        # Enhanced metadata from GSS YAML
        assert char.get_enhanced_data_type() == "sint16", "Should resolve data type from GSS"
        assert char.get_enhanced_field_size() == 2, "Should resolve field size from GSS"
        assert char.is_signed_from_enhanced_yaml() is True, "Should detect signed from 'sint16'"
        assert char.get_byte_order_hint() == "little", "Should provide byte order hint"

    def test_enhanced_parsing_with_yaml_metadata(self):
        """Test that parsing uses enhanced YAML metadata correctly."""
        char = EnhancedTemperatureCharacteristic(uuid="", properties=set())
        
        # Test normal value parsing using enhanced metadata
        test_data = bytearray([0x90, 0x01])  # 400 in little-endian signed 16-bit
        result = char.parse_value(test_data)
        assert result == 4.0, "Should parse using enhanced YAML metadata"
        
        # Test negative temperature
        test_negative = bytearray([0x70, 0xFE])  # -400 in little-endian signed 16-bit
        result_negative = char.parse_value(test_negative)
        assert result_negative == -4.0, "Should handle negative values correctly"

    def test_manual_implementation_requirements(self):
        """Test that manual implementation is still required for non-automatable fields."""
        char = EnhancedTemperatureCharacteristic(uuid="", properties=set())
        
        # Resolution factor requires manual implementation
        resolution = char._get_resolution()
        assert resolution == 0.01, "Resolution factor requires manual implementation"
        
        # Special value handling requires manual implementation
        test_special = bytearray([0x00, 0x80])  # 0x8000 = value not known
        with pytest.raises(ValueError, match="Temperature value is not known"):
            char.parse_value(test_special)

    def test_unit_symbol_extraction(self):
        """Test unit symbol extraction from units.yaml."""
        resolver = YAMLCrossReferenceResolver()
        
        # Test common unit symbol extractions
        celsius_symbol = resolver._extract_unit_symbol("Celsius temperature (degree Celsius)")
        assert celsius_symbol == "°C", "Should extract °C from Celsius temperature"
        
        percentage_symbol = resolver._extract_unit_symbol("percentage")
        assert percentage_symbol == "%", "Should extract % from percentage"
        
        pressure_symbol = resolver._extract_unit_symbol("pressure (pascal)")
        assert pressure_symbol == "Pa", "Should extract Pa from pressure"

    def test_fallback_to_basic_registry(self):
        """Test that fallback to basic registry works when enhanced YAML unavailable."""
        # This tests the fallback mechanism in BaseCharacteristic
        # The actual characteristics should still work even without enhanced YAML
        char = EnhancedTemperatureCharacteristic(uuid="", properties=set())
        
        # Should still resolve basic information
        assert char.char_uuid == "2A6E", "Should resolve UUID via fallback"
        assert char.unit in ["°C", ""], "Should resolve unit via fallback or enhanced"

    def test_cross_file_yaml_references(self):
        """Test cross-file YAML reference system."""
        spec = yaml_cross_reference.resolve_characteristic_spec("Temperature")
        
        if spec and spec.unit_id:
            # Verify cross-file reference chain:
            # 1. GSS YAML provides unit_id
            assert "org.bluetooth.unit" in spec.unit_id, "GSS should provide unit ID"
            
            # 2. units.yaml provides symbol mapping 
            unit_mappings = yaml_cross_reference._unit_mappings
            if spec.unit_id in unit_mappings:
                assert unit_mappings[spec.unit_id] == "°C", "Cross-reference should map to °C"

    def test_data_type_to_signed_detection(self):
        """Test automatic signed/unsigned detection from GSS data types."""
        resolver = YAMLCrossReferenceResolver()
        
        assert resolver.get_signed_from_data_type("sint16") is True, "sint16 should be signed"
        assert resolver.get_signed_from_data_type("uint16") is False, "uint16 should be unsigned"
        assert resolver.get_signed_from_data_type("sint8") is True, "sint8 should be signed"
        assert resolver.get_signed_from_data_type("uint8") is False, "uint8 should be unsigned"
        assert resolver.get_signed_from_data_type(None) is False, "None should default to unsigned"

    def test_enhanced_automation_coverage(self):
        """Test that enhanced automation covers the specified fields from the issue."""
        spec = yaml_cross_reference.resolve_characteristic_spec("Temperature")
        
        if spec:
            # ✅ CAN be automated from YAML (according to issue requirements):
            assert spec.uuid is not None, "✅ UUIDs should be automated"
            assert spec.data_type is not None, "✅ Data types should be automated"
            assert spec.field_size is not None, "✅ Field sizes should be automated"
            assert spec.unit_id is not None, "✅ Unit identifiers should be automated"
            assert spec.unit_symbol is not None, "✅ Unit symbols should be automated"
            
            # ❌ Manual implementation still required (according to issue):
            # Resolution factors are in human text, cannot be fully automated
            assert "resolution" in spec.resolution_text.lower(), "❌ Resolution text requires manual parsing"
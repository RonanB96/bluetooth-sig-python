"""Tests for Characteristic Presentation Format descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import CharacteristicPresentationFormatDescriptor
from bluetooth_sig.gatt.descriptors.characteristic_presentation_format import CharacteristicPresentationFormatData


class TestCharacteristicPresentationFormatDescriptor:
    """Test Characteristic Presentation Format descriptor functionality."""

    def test_parse_presentation_format(self) -> None:
        """Test parsing presentation format data."""
        cpf = CharacteristicPresentationFormatDescriptor()
        # Format: UINT16 (0x06), Exponent: 0, Unit: Celsius (0x272F)
        # Namespace: Bluetooth SIG (0x01), Description: Temperature (0x0000)
        data = b"\x06\x00\x2f\x27\x01\x00\x00"

        result = cpf.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicPresentationFormatData)
        assert result.value.format == 0x06  # UINT16
        assert result.value.exponent == 0
        assert result.value.unit == 0x272F  # Celsius
        assert result.value.namespace == 0x01  # Bluetooth SIG
        assert result.value.description == 0x0000

    def test_parse_presentation_format_registry_resolution(self) -> None:
        """Test CPF auto-resolves format/unit names from registries."""
        cpf = CharacteristicPresentationFormatDescriptor()
        # Known values: UINT16 (0x06), Celsius (0x272F)
        known = cpf.parse_value(b"\x06\x00\x2f\x27\x01\x00\x00")
        assert known.parse_success and known.value is not None
        assert known.value.format_name == "uint16"
        assert known.value.unit_name is not None and "Celsius" in known.value.unit_name

        # Unknown values: 0xFF format, 0xFFFF unit
        unknown = cpf.parse_value(b"\xff\x00\xff\xff\x01\x00\x00")
        assert unknown.parse_success and unknown.value is not None
        assert unknown.value.format_name is None
        assert unknown.value.unit_name is None

    def test_parse_presentation_format_description_name_resolution(self) -> None:
        """Test CPF auto-resolves description_name from registry when namespace=0x01."""
        cpf = CharacteristicPresentationFormatDescriptor()

        # Test ordinal description: description=0x0001 -> "first"
        # Format: UINT16 (0x06), Exponent: 0, Unit: Celsius (0x272F)
        # Namespace: Bluetooth SIG (0x01), Description: 0x0001 (first)
        first_data = b"\x06\x00\x2f\x27\x01\x01\x00"
        result = cpf.parse_value(first_data)
        assert result.parse_success and result.value is not None
        assert result.value.description == 0x0001
        assert result.value.description_name == "first"

        # Test position description: description=0x010D -> "left"
        # Namespace: Bluetooth SIG (0x01), Description: 0x010D (left)
        left_data = b"\x06\x00\x2f\x27\x01\x0d\x01"
        result = cpf.parse_value(left_data)
        assert result.parse_success and result.value is not None
        assert result.value.description == 0x010D
        assert result.value.description_name == "left"

        # Test position description: description=0x010E -> "right"
        right_data = b"\x06\x00\x2f\x27\x01\x0e\x01"
        result = cpf.parse_value(right_data)
        assert result.parse_success and result.value is not None
        assert result.value.description == 0x010E
        assert result.value.description_name == "right"

        # Test unknown description value should return None for description_name
        unknown_data = b"\x06\x00\x2f\x27\x01\xff\xff"
        result = cpf.parse_value(unknown_data)
        assert result.parse_success and result.value is not None
        assert result.value.description == 0xFFFF
        assert result.value.description_name is None

        # Test non-Bluetooth SIG namespace should not resolve description
        # Namespace: Unknown (0x00), Description: 0x0001
        non_sig_data = b"\x06\x00\x2f\x27\x00\x01\x00"
        result = cpf.parse_value(non_sig_data)
        assert result.parse_success and result.value is not None
        assert result.value.description == 0x0001
        assert result.value.description_name is None  # Not resolved for non-SIG namespace

    def test_parse_invalid_length(self) -> None:
        """Test parsing presentation format with invalid length."""
        cpf = CharacteristicPresentationFormatDescriptor()
        data = b"\x06\x00\x2f\x27\x01\x00"  # Too short (6 bytes instead of 7)

        result = cpf.parse_value(data)
        assert not result.parse_success
        assert "Presentation Format data must be exactly 7 bytes" in result.error_message

    def test_helper_methods(self) -> None:
        """Test helper methods for accessing format components."""
        cpf = CharacteristicPresentationFormatDescriptor()
        data = b"\x06\x00\x2f\x27\x01\x00\x00"

        assert cpf.get_format_type(data) == 0x06
        assert cpf.get_exponent(data) == 0
        assert cpf.get_unit(data) == 0x272F
        assert cpf.get_namespace(data) == 0x01
        assert cpf.get_description(data) == 0x0000

    def test_uuid_resolution(self) -> None:
        """Test that Characteristic Presentation Format has correct UUID."""
        cpf = CharacteristicPresentationFormatDescriptor()
        assert str(cpf.uuid) == "00002904-0000-1000-8000-00805F9B34FB"

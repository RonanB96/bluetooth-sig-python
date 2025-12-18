"""Tests for descriptor writability checks."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import (
    CCCDDescriptor,
    CharacteristicExtendedPropertiesDescriptor,
    CharacteristicPresentationFormatDescriptor,
    CharacteristicUserDescriptionDescriptor,
    ServerCharacteristicConfigurationDescriptor,
    ValidRangeDescriptor,
)


class TestDescriptorWritability:
    """Test descriptor writability checks."""

    def test_cccd_is_writable(self) -> None:
        """CCCD should be marked as writable."""
        cccd = CCCDDescriptor()
        assert cccd.is_writable() is True

    def test_sccd_is_writable(self) -> None:
        """SCCD should be marked as writable."""
        sccd = ServerCharacteristicConfigurationDescriptor()
        assert sccd.is_writable() is True

    def test_user_description_not_writable(self) -> None:
        """User Description should be non-writable (conservative approach)."""
        user_desc = CharacteristicUserDescriptionDescriptor()
        assert user_desc.is_writable() is False

    def test_read_only_descriptors_not_writable(self) -> None:
        """Read-only descriptors should be marked as non-writable."""
        valid_range = ValidRangeDescriptor()
        assert valid_range.is_writable() is False

        presentation_format = CharacteristicPresentationFormatDescriptor()
        assert presentation_format.is_writable() is False

        extended_props = CharacteristicExtendedPropertiesDescriptor()
        assert extended_props.is_writable() is False

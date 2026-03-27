"""Tests for IMDS Descriptor Value Changed characteristic (0x2C0D)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.imds_descriptor_value_changed import (
    IMDSDescriptorChangeFlags,
    IMDSDescriptorValueChangedCharacteristic,
    IMDSDescriptorValueChangedData,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIMDSDescriptorValueChangedCharacteristic(CommonCharacteristicTests):
    """Test suite for IMDS Descriptor Value Changed characteristic."""

    @pytest.fixture
    def characteristic(self) -> IMDSDescriptorValueChangedCharacteristic:
        return IMDSDescriptorValueChangedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C0D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x19, 0x2A]),
                expected_value=IMDSDescriptorValueChangedData(
                    flags=IMDSDescriptorChangeFlags.SOURCE_OF_CHANGE,
                    characteristic_uuid=0x2A19,
                ),
                description="Source of change flag, Battery Level UUID",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x06, 0x00, 0x06, 0x2A]),
                expected_value=IMDSDescriptorValueChangedData(
                    flags=(
                        IMDSDescriptorChangeFlags.CHARACTERISTIC_VALUE_CHANGED
                        | IMDSDescriptorChangeFlags.DESCRIPTOR_VALUE_CHANGED
                    ),
                    characteristic_uuid=0x2A06,
                ),
                description="Value and descriptor changed, Alert Level UUID",
            ),
        ]

    def test_roundtrip(self, characteristic: IMDSDescriptorValueChangedCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = IMDSDescriptorValueChangedData(
            flags=IMDSDescriptorChangeFlags.ADDITIONAL_DESCRIPTORS_CHANGED,
            characteristic_uuid=0x2A37,
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original

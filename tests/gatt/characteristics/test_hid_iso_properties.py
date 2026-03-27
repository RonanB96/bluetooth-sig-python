"""Tests for HID ISO Properties characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.hid_iso_properties import (
    HIDISOProperties,
    HIDISOPropertiesCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHIDISOPropertiesCharacteristic(CommonCharacteristicTests):
    """Test suite for HID ISO Properties characteristic."""

    @pytest.fixture
    def characteristic(self) -> HIDISOPropertiesCharacteristic:
        return HIDISOPropertiesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C23"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=HIDISOProperties.INPUT_REPORT_SUPPORTED,
                description="Input report supported only",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03]),
                expected_value=HIDISOProperties.INPUT_REPORT_SUPPORTED | HIDISOProperties.OUTPUT_REPORT_SUPPORTED,
                description="Both input and output report supported",
            ),
        ]

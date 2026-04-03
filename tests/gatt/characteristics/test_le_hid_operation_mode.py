"""Tests for LE HID Operation Mode characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.le_hid_operation_mode import (
    LEHIDOperationModeCharacteristic,
    LEHIDOperationModeValue,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLEHIDOperationModeCharacteristic(CommonCharacteristicTests):
    """Test suite for LE HID Operation Mode characteristic."""

    @pytest.fixture
    def characteristic(self) -> LEHIDOperationModeCharacteristic:
        return LEHIDOperationModeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C24"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=LEHIDOperationModeValue.REPORT_MODE,
                description="Report mode (default)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=LEHIDOperationModeValue.BOOT_MODE,
                description="Boot mode",
            ),
        ]

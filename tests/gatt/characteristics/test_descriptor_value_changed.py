"""Tests for DescriptorValueChangedCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.descriptor_value_changed import (
    DescriptorValueChangedCharacteristic,
    DescriptorValueChangedData,
    DescriptorValueChangedFlags,
)
from bluetooth_sig.types.uuid import BluetoothUUID
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDescriptorValueChangedCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> DescriptorValueChangedCharacteristic:
        return DescriptorValueChangedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A7D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                # flags=0x0001 (SOURCE_OF_CHANGE_DEVICE), UUID=0x2A19 (Battery Level), no value
                input_data=bytearray([0x01, 0x00, 0x19, 0x2A]),
                expected_value=DescriptorValueChangedData(
                    flags=DescriptorValueChangedFlags.SOURCE_OF_CHANGE_DEVICE,
                    characteristic_uuid=BluetoothUUID(0x2A19),
                    value=b"",
                ),
                description="Device changed battery level descriptor, no value",
            ),
            CharacteristicTestData(
                # flags=0x0002 (SOURCE_OF_CHANGE_EXTERNAL), UUID=0x2A6E (Temperature), value=0x1234
                input_data=bytearray([0x02, 0x00, 0x6E, 0x2A, 0x12, 0x34]),
                expected_value=DescriptorValueChangedData(
                    flags=DescriptorValueChangedFlags.SOURCE_OF_CHANGE_EXTERNAL,
                    characteristic_uuid=BluetoothUUID(0x2A6E),
                    value=b"\x12\x34",
                ),
                description="External change to temperature descriptor with value",
            ),
            CharacteristicTestData(
                # flags=0x0003 (both flags), UUID=0x2A37 (Heart Rate Measurement), value bytes
                input_data=bytearray([0x03, 0x00, 0x37, 0x2A, 0xAA, 0xBB, 0xCC]),
                expected_value=DescriptorValueChangedData(
                    flags=DescriptorValueChangedFlags.SOURCE_OF_CHANGE_DEVICE
                    | DescriptorValueChangedFlags.SOURCE_OF_CHANGE_EXTERNAL,
                    characteristic_uuid=BluetoothUUID(0x2A37),
                    value=b"\xaa\xbb\xcc",
                ),
                description="Both change sources, heart rate descriptor with value",
            ),
        ]

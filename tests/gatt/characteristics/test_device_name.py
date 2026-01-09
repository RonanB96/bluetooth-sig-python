from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import DeviceNameCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDeviceNameCharacteristic(CommonCharacteristicTests):
    characteristic_cls = DeviceNameCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return DeviceNameCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A00"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"My Device"), expected_value="My Device", description="Simple ASCII device name"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Bluetooth Device"),
                expected_value="Bluetooth Device",
                description="Standard device name",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Test Device 123"),
                expected_value="Test Device 123",
                description="Device name with numbers",
            ),
            CharacteristicTestData(input_data=bytearray(b""), expected_value="", description="Empty device name"),
            CharacteristicTestData(
                input_data=bytearray(b"Special: @#$%"),
                expected_value="Special: @#$%",
                description="Device name with special characters",
            ),
        ]

"""Tests for Bluetooth SIG Data characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bluetooth_sig_data import (
    BluetoothSIGDataCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBluetoothSIGDataCharacteristic(CommonCharacteristicTests):
    """Test suite for Bluetooth SIG Data characteristic."""

    @pytest.fixture
    def characteristic(self) -> BluetoothSIGDataCharacteristic:
        return BluetoothSIGDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B39"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0xFF]),
                expected_value=b"\xff",
                description="Single byte SIG data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x02, 0x03, 0x04]),
                expected_value=b"\x01\x02\x03\x04",
                description="Multi-byte SIG data",
            ),
        ]

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import SerialNumberStringCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSerialNumberStringCharacteristic(CommonCharacteristicTests):
    characteristic_cls = SerialNumberStringCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return SerialNumberStringCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A25"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"F8L123456789"),
                expected_value="F8L123456789",
                description="Apple serial number format",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"SN-ABC123XYZ"),
                expected_value="SN-ABC123XYZ",
                description="Generic serial number",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"1234567890"),
                expected_value="1234567890",
                description="Numeric serial number",
            ),
            CharacteristicTestData(input_data=bytearray(b""), expected_value="", description="Empty serial number"),
        ]

    @pytest.fixture
    def invalid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"\xff\xfe\xfd"),  # Invalid UTF-8 sequence
                expected_value=None,
                description="Invalid UTF-8 bytes",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"\xc0\x80"),  # Overlong encoding
                expected_value=None,
                description="Overlong UTF-8 encoding",
            ),
        ]

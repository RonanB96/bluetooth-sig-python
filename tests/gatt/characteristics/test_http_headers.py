"""Tests for HTTPHeadersCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.http_headers import HTTPHeadersCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestHTTPHeadersCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> HTTPHeadersCharacteristic:
        return HTTPHeadersCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AB7"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"Content-Type: text/html"),
                expected_value="Content-Type: text/html",
                description="Single header",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Host: example.com\r\nAccept: */*"),
                expected_value="Host: example.com\r\nAccept: */*",
                description="Multiple headers",
            ),
        ]

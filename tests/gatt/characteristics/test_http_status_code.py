"""Tests for HTTPStatusCodeCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.http_status_code import (
    HTTPDataStatus,
    HTTPStatusCodeCharacteristic,
    HTTPStatusCodeData,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestHTTPStatusCodeCharacteristic(CommonCharacteristicTests):
    """Tests for HTTPStatusCodeCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> HTTPStatusCodeCharacteristic:
        return HTTPStatusCodeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AB8"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                # status_code=200 (0x00C8 LE), data_status=HEADERS_RECEIVED|BODY_RECEIVED (0x05)
                input_data=bytearray([0xC8, 0x00, 0x05]),
                expected_value=HTTPStatusCodeData(
                    status_code=200,
                    data_status=HTTPDataStatus.HEADERS_RECEIVED | HTTPDataStatus.BODY_RECEIVED,
                ),
                description="HTTP 200 with headers and body received",
            ),
            CharacteristicTestData(
                # status_code=404 (0x0194 LE), data_status=HEADERS_RECEIVED|HEADERS_TRUNCATED (0x03)
                input_data=bytearray([0x94, 0x01, 0x03]),
                expected_value=HTTPStatusCodeData(
                    status_code=404,
                    data_status=HTTPDataStatus.HEADERS_RECEIVED | HTTPDataStatus.HEADERS_TRUNCATED,
                ),
                description="HTTP 404 with headers received and truncated",
            ),
            CharacteristicTestData(
                # status_code=500 (0x01F4 LE), data_status=BODY_TRUNCATED (0x08)
                input_data=bytearray([0xF4, 0x01, 0x08]),
                expected_value=HTTPStatusCodeData(
                    status_code=500,
                    data_status=HTTPDataStatus.BODY_TRUNCATED,
                ),
                description="HTTP 500 with body truncated",
            ),
        ]

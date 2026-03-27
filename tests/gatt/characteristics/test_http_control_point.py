"""Tests for HTTP Control Point characteristic (0x2ABA)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.http_control_point import (
    HTTPControlPointCharacteristic,
    HTTPControlPointOpCode,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHTTPControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for HTTP Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> HTTPControlPointCharacteristic:
        return HTTPControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ABA"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=HTTPControlPointOpCode.HTTP_GET_REQUEST,
                description="HTTP GET request",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03]),
                expected_value=HTTPControlPointOpCode.HTTP_POST_REQUEST,
                description="HTTP POST request",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0B]),
                expected_value=HTTPControlPointOpCode.HTTP_REQUEST_CANCEL,
                description="HTTP request cancel",
            ),
        ]

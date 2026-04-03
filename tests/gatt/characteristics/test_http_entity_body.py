"""Tests for HTTP Entity Body characteristic (0x2AB9)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.http_entity_body import HTTPEntityBodyCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHTTPEntityBodyCharacteristic(CommonCharacteristicTests):
    """Test suite for HTTP Entity Body characteristic."""

    @pytest.fixture
    def characteristic(self) -> HTTPEntityBodyCharacteristic:
        return HTTPEntityBodyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AB9"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"Hello"),
                expected_value="Hello",
                description="Simple body text",
            ),
            CharacteristicTestData(
                input_data=bytearray(b'{"key":"value"}'),
                expected_value='{"key":"value"}',
                description="JSON body",
            ),
        ]

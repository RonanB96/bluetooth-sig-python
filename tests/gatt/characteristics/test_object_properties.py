"""Tests for ObjectPropertiesCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.object_properties import (
    ObjectProperties,
    ObjectPropertiesCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestObjectPropertiesCharacteristic(CommonCharacteristicTests):
    """Test Object Properties characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> ObjectPropertiesCharacteristic:
        return ObjectPropertiesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AC4"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x0C, 0x00, 0x00, 0x00]),
                expected_value=ObjectProperties.READ | ObjectProperties.WRITE,
                description="Object with READ and WRITE properties",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x95, 0x00, 0x00, 0x00]),
                expected_value=(
                    ObjectProperties.DELETE | ObjectProperties.READ | ObjectProperties.APPEND | ObjectProperties.MARK
                ),
                description="Object with DELETE, READ, APPEND, and MARK properties",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0x00, 0x00, 0x00]),
                expected_value=(
                    ObjectProperties.DELETE
                    | ObjectProperties.EXECUTE
                    | ObjectProperties.READ
                    | ObjectProperties.WRITE
                    | ObjectProperties.APPEND
                    | ObjectProperties.TRUNCATE
                    | ObjectProperties.PATCH
                    | ObjectProperties.MARK
                ),
                description="Object with all properties enabled",
            ),
        ]

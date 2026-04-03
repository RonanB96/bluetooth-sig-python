"""Tests for ObjectChangedCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.object_changed import (
    ObjectChangedCharacteristic,
    ObjectChangedData,
    ObjectChangedFlags,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestObjectChangedCharacteristic(CommonCharacteristicTests):
    """Test Object Changed characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> ObjectChangedCharacteristic:
        return ObjectChangedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AC8"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x04,  # flags: OBJECT_CONTENTS_CHANGED
                        0x01,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,  # object_id=1 (uint48 LE)
                    ]
                ),
                expected_value=ObjectChangedData(
                    flags=ObjectChangedFlags.OBJECT_CONTENTS_CHANGED,
                    object_id=1,
                ),
                description="Object contents changed for object ID 1",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x11,  # flags: SOURCE_OF_CHANGE | OBJECT_CREATION
                        0x00,
                        0x01,
                        0x00,
                        0x00,
                        0x00,
                        0x00,  # object_id=256 (uint48 LE)
                    ]
                ),
                expected_value=ObjectChangedData(
                    flags=ObjectChangedFlags.SOURCE_OF_CHANGE | ObjectChangedFlags.OBJECT_CREATION,
                    object_id=256,
                ),
                description="Object creation with source of change for object ID 256",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x20,  # flags: OBJECT_DELETION
                        0xFF,
                        0xFF,
                        0x00,
                        0x00,
                        0x00,
                        0x00,  # object_id=65535 (uint48 LE)
                    ]
                ),
                expected_value=ObjectChangedData(
                    flags=ObjectChangedFlags.OBJECT_DELETION,
                    object_id=65535,
                ),
                description="Object deletion for object ID 65535",
            ),
        ]

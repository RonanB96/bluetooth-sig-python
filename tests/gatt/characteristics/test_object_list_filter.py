"""Tests for ObjectListFilterCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.object_list_filter import (
    ObjectListFilterCharacteristic,
    ObjectListFilterData,
    ObjectListFilterType,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestObjectListFilterCharacteristic(CommonCharacteristicTests):
    """Test Object List Filter characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> ObjectListFilterCharacteristic:
        return ObjectListFilterCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AC7"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=ObjectListFilterData(
                    filter_type=ObjectListFilterType.NO_FILTER,
                    parameters=b"",
                ),
                description="No filter applied",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x41, 0x42, 0x43]),
                expected_value=ObjectListFilterData(
                    filter_type=ObjectListFilterType.NAME_STARTS_WITH,
                    parameters=b"ABC",
                ),
                description="Filter by name starts with 'ABC'",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0A]),
                expected_value=ObjectListFilterData(
                    filter_type=ObjectListFilterType.MARKED_OBJECTS,
                    parameters=b"",
                ),
                description="Filter for marked objects only",
            ),
        ]

"""Tests for PhysicalActivityCurrentSessionCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.physical_activity_current_session import (
    PAMActivityType,
    PAMSessionFlags,
    PhysicalActivityCurrentSessionCharacteristic,
    PhysicalActivityCurrentSessionData,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestPhysicalActivityCurrentSessionCharacteristic(CommonCharacteristicTests):
    """PhysicalActivityCurrentSessionCharacteristic test suite."""

    @pytest.fixture
    def characteristic(self) -> PhysicalActivityCurrentSessionCharacteristic:
        return PhysicalActivityCurrentSessionCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B44"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x05, 0x00]),
                expected_value=PhysicalActivityCurrentSessionData(
                    flags=PAMSessionFlags.SESSION_ACTIVE,
                    session_id=5,
                    activity_type=None,
                ),
                description="Session active, no activity type",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x0A, 0x00, 0x02]),
                expected_value=PhysicalActivityCurrentSessionData(
                    flags=PAMSessionFlags.SESSION_ACTIVE | PAMSessionFlags.ACTIVITY_TYPE_PRESENT,
                    session_id=10,
                    activity_type=PAMActivityType.RUNNING,
                ),
                description="Session active with running activity type",
            ),
        ]

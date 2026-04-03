"""Tests for PhysicalActivitySessionDescriptorCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.physical_activity_session_descriptor import (
    ActivityType,
    PAMSessionStatus,
    PhysicalActivitySessionDescriptorCharacteristic,
    PhysicalActivitySessionDescriptorData,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestPhysicalActivitySessionDescriptorCharacteristic(CommonCharacteristicTests):
    """PhysicalActivitySessionDescriptorCharacteristic test suite."""

    @pytest.fixture
    def characteristic(self) -> PhysicalActivitySessionDescriptorCharacteristic:
        return PhysicalActivitySessionDescriptorCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B45"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x05]),
                expected_value=PhysicalActivitySessionDescriptorData(
                    session_id=1,
                    session_status=PAMSessionStatus.COMPLETE,
                    activity_type=ActivityType.WALK,
                ),
                description="Completed walking session",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x00, 0x01, 0x07, 0xAB]),
                expected_value=PhysicalActivitySessionDescriptorData(
                    session_id=2,
                    session_status=PAMSessionStatus.IN_PROGRESS,
                    activity_type=ActivityType.RUN,
                    additional_data=b"\xab",
                ),
                description="In-progress running session with extra data",
            ),
        ]

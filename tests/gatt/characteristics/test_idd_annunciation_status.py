"""Tests for IDDAnnunciationStatusCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.idd_annunciation_status import (
    IDDAnnunciationStatus,
    IDDAnnunciationStatusCharacteristic,
    IDDAnnunciationStatusData,
    IDDAnnunciationType,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestIDDAnnunciationStatusCharacteristic(CommonCharacteristicTests):
    """Tests for IDDAnnunciationStatusCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> IDDAnnunciationStatusCharacteristic:
        return IDDAnnunciationStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B22"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                # instance_id=1 (0x0001 LE), type=ALERT (0x01), status=ACTIVE (0x01)
                input_data=bytearray([0x01, 0x00, 0x01, 0x01]),
                expected_value=IDDAnnunciationStatusData(
                    annunciation_instance_id=1,
                    annunciation_type=IDDAnnunciationType.ALERT,
                    annunciation_status=IDDAnnunciationStatus.ACTIVE,
                ),
                description="Alert annunciation, active",
            ),
            CharacteristicTestData(
                # instance_id=258 (0x0102 LE), type=REMINDER (0x02), status=PENDING (0x00)
                input_data=bytearray([0x02, 0x01, 0x02, 0x00]),
                expected_value=IDDAnnunciationStatusData(
                    annunciation_instance_id=258,
                    annunciation_type=IDDAnnunciationType.REMINDER,
                    annunciation_status=IDDAnnunciationStatus.PENDING,
                ),
                description="Reminder annunciation, pending",
            ),
            CharacteristicTestData(
                # instance_id=0 (0x0000 LE), type=STATUS_CHANGED (0x03), status=AUXILIARY (0x02)
                input_data=bytearray([0x00, 0x00, 0x03, 0x02]),
                expected_value=IDDAnnunciationStatusData(
                    annunciation_instance_id=0,
                    annunciation_type=IDDAnnunciationType.STATUS_CHANGED,
                    annunciation_status=IDDAnnunciationStatus.AUXILIARY,
                ),
                description="Status changed annunciation, auxiliary",
            ),
        ]

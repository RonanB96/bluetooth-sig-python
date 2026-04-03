"""Tests for IDDAnnunciationStatusCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.idd_annunciation_status import (
    IDDAnnunciationFlags,
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
                # Flags only, no annunciation present
                input_data=bytearray([0x00]),
                expected_value=IDDAnnunciationStatusData(
                    flags=IDDAnnunciationFlags(0),
                    annunciation_instance_id=None,
                    annunciation_type=None,
                    annunciation_status=None,
                    aux_info=[],
                ),
                description="Flags only, no annunciation",
            ),
            CharacteristicTestData(
                # Annunciation present: instance=1, type=SYSTEM_ISSUE(0x000F), status=PENDING(0x33)
                input_data=bytearray([0x01, 0x01, 0x00, 0x0F, 0x00, 0x33]),
                expected_value=IDDAnnunciationStatusData(
                    flags=IDDAnnunciationFlags.ANNUNCIATION_PRESENT,
                    annunciation_instance_id=1,
                    annunciation_type=IDDAnnunciationType.SYSTEM_ISSUE,
                    annunciation_status=IDDAnnunciationStatus.PENDING,
                    aux_info=[],
                ),
                description="Annunciation present, system issue, pending",
            ),
            CharacteristicTestData(
                # Annunciation + aux info 1: instance=1, type=MECHANICAL_ISSUE(0x0033),
                # status=UNDETERMINED(0x0F), aux_info=[100]
                input_data=bytearray([0x03, 0x01, 0x00, 0x33, 0x00, 0x0F, 0x64, 0x00]),
                expected_value=IDDAnnunciationStatusData(
                    flags=IDDAnnunciationFlags.ANNUNCIATION_PRESENT | IDDAnnunciationFlags.AUX_INFO_1_PRESENT,
                    annunciation_instance_id=1,
                    annunciation_type=IDDAnnunciationType.MECHANICAL_ISSUE,
                    annunciation_status=IDDAnnunciationStatus.UNDETERMINED,
                    aux_info=[100],
                ),
                description="Annunciation with aux info 1",
            ),
        ]

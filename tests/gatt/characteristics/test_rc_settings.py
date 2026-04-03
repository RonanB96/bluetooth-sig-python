"""Tests for RCSettingsCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.rc_settings import (
    AdvertisementMode,
    RCSettingsCharacteristic,
    RCSettingsData,
    RCSettingsFlags,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestRCSettingsCharacteristic(CommonCharacteristicTests):
    """RCSettingsCharacteristic test suite."""

    @pytest.fixture
    def characteristic(self) -> RCSettingsCharacteristic:
        return RCSettingsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B1E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x00, 0x00]),
                expected_value=RCSettingsData(
                    length=2,
                    settings_flags=RCSettingsFlags(0),
                    advertisement_mode=AdvertisementMode.ADV_IND,
                ),
                description="Empty settings, no E2E-CRC",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x12, 0x01]),
                expected_value=RCSettingsData(
                    length=2,
                    settings_flags=(RCSettingsFlags.LESC_ONLY | RCSettingsFlags.READY_FOR_DISCONNECT),
                    advertisement_mode=AdvertisementMode.ADV_SCAN_IND,
                ),
                description="LESC + Ready for Disconnect + ADV_SCAN_IND, no CRC",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x20, 0x00, 0xCD, 0xAB]),
                expected_value=RCSettingsData(
                    length=2,
                    settings_flags=RCSettingsFlags.LIMITED_ACCESS,
                    advertisement_mode=AdvertisementMode.ADV_IND,
                    e2e_crc=0xABCD,
                ),
                description="Limited Access with E2E-CRC",
            ),
        ]

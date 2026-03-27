"""Tests for HearingAidFeaturesCharacteristic (2BDA)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.hearing_aid_features import HearingAidFeatures, HearingAidFeaturesCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHearingAidFeatures(CommonCharacteristicTests):
    """Test suite for HearingAidFeaturesCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> HearingAidFeaturesCharacteristic:
        return HearingAidFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BDA"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), HearingAidFeatures(0), "No features"),
            CharacteristicTestData(bytearray([0x01]), HearingAidFeatures.PRESET_SYNCHRONIZATION_SUPPORT, "Preset sync"),
            CharacteristicTestData(
                bytearray([0x0F]),
                HearingAidFeatures.PRESET_SYNCHRONIZATION_SUPPORT
                | HearingAidFeatures.INDEPENDENT_PRESETS
                | HearingAidFeatures.DYNAMIC_PRESETS
                | HearingAidFeatures.WRITABLE_PRESETS,
                "All features",
            ),
        ]

    def test_roundtrip(self, characteristic: HearingAidFeaturesCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), HearingAidFeatures(0), "No features"),
            CharacteristicTestData(bytearray([0x01]), HearingAidFeatures.PRESET_SYNCHRONIZATION_SUPPORT, "Preset sync"),
            CharacteristicTestData(
                bytearray([0x0F]),
                HearingAidFeatures.PRESET_SYNCHRONIZATION_SUPPORT
                | HearingAidFeatures.INDEPENDENT_PRESETS
                | HearingAidFeatures.DYNAMIC_PRESETS
                | HearingAidFeatures.WRITABLE_PRESETS,
                "All features",
            ),
        ]

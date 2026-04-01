"""Tests for HearingAidFeaturesCharacteristic (2BDA)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.hearing_aid_features import (
    HearingAidFeaturesCharacteristic,
    HearingAidFeaturesData,
    HearingAidType,
)
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
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=HearingAidFeaturesData(
                    hearing_aid_type=HearingAidType.BINAURAL,
                    preset_synchronization_support=False,
                    independent_presets=False,
                    dynamic_presets=False,
                    writable_presets=False,
                ),
                description="Binaural, no features",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=HearingAidFeaturesData(
                    hearing_aid_type=HearingAidType.MONAURAL,
                    preset_synchronization_support=False,
                    independent_presets=False,
                    dynamic_presets=False,
                    writable_presets=False,
                ),
                description="Monaural, no features",
            ),
            CharacteristicTestData(
                # 0x3E = 0b00111110 -> type=BANDED(0x02), preset_sync=1, indep=1, dynamic=1, writable=1
                input_data=bytearray([0x3E]),
                expected_value=HearingAidFeaturesData(
                    hearing_aid_type=HearingAidType.BANDED,
                    preset_synchronization_support=True,
                    independent_presets=True,
                    dynamic_presets=True,
                    writable_presets=True,
                ),
                description="Banded, all features",
            ),
        ]

    def test_roundtrip(self, characteristic: HearingAidFeaturesCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = HearingAidFeaturesData(
            hearing_aid_type=HearingAidType.MONAURAL,
            preset_synchronization_support=True,
            independent_presets=False,
            dynamic_presets=True,
            writable_presets=False,
        )
        encoded = characteristic.build_value(original)
        result = characteristic.parse_value(encoded)
        assert result == original

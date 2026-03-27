"""Tests for IDDFeaturesCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.idd_features import (
    IDDFeatures,
    IDDFeaturesCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestIDDFeaturesCharacteristic(CommonCharacteristicTests):
    """Tests for IDDFeaturesCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> IDDFeaturesCharacteristic:
        return IDDFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B23"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                # flags=0x00000003 LE → E2E_PROTECTION_SUPPORTED | BASAL_RATE_DELIVERY_SUPPORTED
                input_data=bytearray([0x03, 0x00, 0x00, 0x00]),
                expected_value=(IDDFeatures.E2E_PROTECTION_SUPPORTED | IDDFeatures.BASAL_RATE_DELIVERY_SUPPORTED),
                description="E2E protection and basal rate delivery supported",
            ),
            CharacteristicTestData(
                # flags=0x00002030 LE → PROFILE_TEMPLATE_SUPPORTED | HISTORY_EVENTS_SUPPORTED
                input_data=bytearray([0x30, 0x20, 0x00, 0x00]),
                expected_value=(
                    IDDFeatures.TMR_DELIVERY_SUPPORTED
                    | IDDFeatures.PROFILE_TEMPLATE_SUPPORTED
                    | IDDFeatures.HISTORY_EVENTS_SUPPORTED
                ),
                description="TMR delivery, profile template, and history events supported",
            ),
            CharacteristicTestData(
                # flags=0x00000000 → no features
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=IDDFeatures(0),
                description="No features supported",
            ),
        ]

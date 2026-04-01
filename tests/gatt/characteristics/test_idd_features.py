"""Tests for IDDFeaturesCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.idd_features import (
    IDDFeatureFlags,
    IDDFeaturesCharacteristic,
    IDDFeaturesData,
)
from bluetooth_sig.gatt.characteristics.utils import IEEE11073Parser
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)

# Pre-compute SFLOAT encoding for 100.0 (exponent=0, mantissa=100 → 0x0064 LE → [0x64, 0x00])
_SFLOAT_100 = IEEE11073Parser.encode_sfloat(100.0)


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
                # No features, no E2E: CRC=0xFFFF, counter=0, conc=100.0, flags=0
                input_data=bytearray([0xFF, 0xFF, 0x00] + list(_SFLOAT_100) + [0x00, 0x00, 0x00]),
                expected_value=IDDFeaturesData(
                    e2e_crc=0xFFFF,
                    e2e_counter=0,
                    insulin_concentration=100.0,
                    flags=IDDFeatureFlags(0),
                ),
                description="No features, E2E not supported",
            ),
            CharacteristicTestData(
                # E2E + basal rate: CRC=0x1234, counter=5, conc=100.0, flags=0x03
                input_data=bytearray([0x34, 0x12, 0x05] + list(_SFLOAT_100) + [0x03, 0x00, 0x00]),
                expected_value=IDDFeaturesData(
                    e2e_crc=0x1234,
                    e2e_counter=5,
                    insulin_concentration=100.0,
                    flags=(IDDFeatureFlags.E2E_PROTECTION_SUPPORTED | IDDFeatureFlags.BASAL_RATE_SUPPORTED),
                ),
                description="E2E protection and basal rate supported",
            ),
            CharacteristicTestData(
                # Feature extension bit set: CRC=0xFFFF, counter=0, conc=100.0, flags=0x800000
                input_data=bytearray([0xFF, 0xFF, 0x00] + list(_SFLOAT_100) + [0x00, 0x00, 0x80]),
                expected_value=IDDFeaturesData(
                    e2e_crc=0xFFFF,
                    e2e_counter=0,
                    insulin_concentration=100.0,
                    flags=IDDFeatureFlags.FEATURE_EXTENSION,
                ),
                description="Feature extension bit set",
            ),
        ]

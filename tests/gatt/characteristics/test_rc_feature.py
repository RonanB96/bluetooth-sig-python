"""Tests for RC Feature characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import RCFeatureCharacteristic
from bluetooth_sig.gatt.characteristics.rc_feature import RCFeatureData, RCFeatureFlags
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRCFeatureCharacteristic(CommonCharacteristicTests):
    """Test suite for RC Feature characteristic."""

    @pytest.fixture
    def characteristic(self) -> RCFeatureCharacteristic:
        return RCFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B1D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0x00, 0x00, 0x00]),
                expected_value=RCFeatureData(
                    e2e_crc=0xFFFF,
                    features=RCFeatureFlags(0),
                ),
                description="No features, E2E-CRC=0xFFFF (not supported)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x03, 0x00, 0x00]),
                expected_value=RCFeatureData(
                    e2e_crc=0x0000,
                    features=(RCFeatureFlags.E2E_CRC_SUPPORTED | RCFeatureFlags.ENABLE_DISCONNECT_SUPPORTED),
                ),
                description="E2E-CRC + Disconnect features",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x34, 0x12, 0xFF, 0xFF, 0x03]),
                expected_value=RCFeatureData(
                    e2e_crc=0x1234,
                    features=RCFeatureFlags(0x03FFFF),
                ),
                description="All features supported, custom CRC",
            ),
        ]

    def test_minimum_length_enforced(self, characteristic: RCFeatureCharacteristic) -> None:
        """Test that data shorter than 5 bytes raises."""
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00, 0x00, 0x00, 0x00]))

    def test_extra_feature_bytes(self, characteristic: RCFeatureCharacteristic) -> None:
        """Test that extra bytes beyond 3 are accepted (variable length)."""
        data = bytearray([0x00, 0x00, 0x01, 0x00, 0x00, 0x00])
        result = characteristic.parse_value(data)
        assert RCFeatureFlags.E2E_CRC_SUPPORTED in result.features

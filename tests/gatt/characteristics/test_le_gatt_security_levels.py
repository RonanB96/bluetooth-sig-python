"""Tests for LEGATTSecurityLevelsCharacteristic (0x2BF5).

BT Core Spec v6.0, Vol 3, Part C, Section 12.7:
  Attribute Value is a sequence of Security Level Requirements,
  each uint8[2]: (security_mode, security_level).
  e.g. 0x01 0x04 = mode 1, level 4.
"""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.le_gatt_security_levels import (
    LEGATTSecurityLevelsCharacteristic,
    LESecurityMode,
    LESecurityModeLevel,
    SecurityLevelRequirement,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLEGATTSecurityLevels(CommonCharacteristicTests):
    """Test suite for LEGATTSecurityLevelsCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> LEGATTSecurityLevelsCharacteristic:
        return LEGATTSecurityLevelsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BF5"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray([0x01, 0x04]),
                [SecurityLevelRequirement(mode=1, level=4)],
                "Single: mode 1 level 4 (auth SC encryption)",
            ),
            CharacteristicTestData(
                bytearray([0x01, 0x02, 0x01, 0x04]),
                [
                    SecurityLevelRequirement(mode=1, level=2),
                    SecurityLevelRequirement(mode=1, level=4),
                ],
                "Two requirements: mode 1 level 2 + mode 1 level 4",
            ),
        ]

    def test_roundtrip(self, characteristic: LEGATTSecurityLevelsCharacteristic) -> None:
        """Test encode/decode roundtrip for single and multiple requirements."""
        cases = [
            [SecurityLevelRequirement(mode=1, level=4)],
            [SecurityLevelRequirement(mode=1, level=2), SecurityLevelRequirement(mode=1, level=4)],
            [SecurityLevelRequirement(mode=2, level=1)],
        ]
        for reqs in cases:
            encoded = characteristic.build_value(reqs)
            result = characteristic.parse_value(encoded)
            assert result == reqs

    def test_odd_length_data_rejected(self, characteristic: LEGATTSecurityLevelsCharacteristic) -> None:
        """Odd-length data cannot form complete uint8[2] pairs."""
        with pytest.raises((ValueError, Exception)):
            characteristic.parse_value(bytearray([0x01, 0x04, 0x02]))

    def test_mode_level_enum_access(self, characteristic: LEGATTSecurityLevelsCharacteristic) -> None:
        """Test that parsed requirements expose the combined LESecurityModeLevel enum."""
        result = characteristic.parse_value(bytearray([0x01, 0x04]))
        req = result[0]
        assert req.mode_level == LESecurityModeLevel.MODE1_AUTH_SC_ENCRYPTION
        assert req.mode_level.security_mode == LESecurityMode.ENCRYPTION
        assert req.mode_level.security_level == 4

    def test_all_defined_mode_levels(self, characteristic: LEGATTSecurityLevelsCharacteristic) -> None:
        """Verify all spec-defined mode+level combinations parse correctly."""
        expected = [
            (0x01, 0x01, LESecurityModeLevel.MODE1_NO_SECURITY),
            (0x01, 0x02, LESecurityModeLevel.MODE1_UNAUTH_ENCRYPTION),
            (0x01, 0x03, LESecurityModeLevel.MODE1_AUTH_ENCRYPTION),
            (0x01, 0x04, LESecurityModeLevel.MODE1_AUTH_SC_ENCRYPTION),
            (0x02, 0x01, LESecurityModeLevel.MODE2_UNAUTH_SIGNING),
            (0x02, 0x02, LESecurityModeLevel.MODE2_AUTH_SIGNING),
            (0x03, 0x01, LESecurityModeLevel.MODE3_NO_SECURITY),
            (0x03, 0x02, LESecurityModeLevel.MODE3_UNAUTH_BROADCAST_CODE),
            (0x03, 0x03, LESecurityModeLevel.MODE3_AUTH_BROADCAST_CODE),
        ]
        for mode_byte, level_byte, expected_ml in expected:
            result = characteristic.parse_value(bytearray([mode_byte, level_byte]))
            assert result[0].mode_level == expected_ml

"""Tests for CGM Feature characteristic (0x2AA8)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.cgm_feature import (
    CGMFeatureCharacteristic,
    CGMFeatureData,
    CGMFeatureFlags,
    CGMSampleLocation,
    CGMType,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestCGMFeatureCharacteristic(CommonCharacteristicTests):
    """Test CGM Feature characteristic."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide characteristic instance."""
        return CGMFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID."""
        return "2AA8"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,
                        0x00,
                        0x00,  # features: calibration supported
                        0x59,  # type=ISF (0x9), location=subcutaneous (0x5)
                        0xFF,
                        0xFF,  # e2e_crc
                    ]
                ),
                expected_value=CGMFeatureData(
                    features=CGMFeatureFlags.CALIBRATION_SUPPORTED,
                    cgm_type=CGMType.INTERSTITIAL_FLUID,
                    sample_location=CGMSampleLocation.SUBCUTANEOUS_TISSUE,
                    e2e_crc=0xFFFF,
                ),
                description="Calibration supported, ISF, subcutaneous",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xFF,
                        0xFF,
                        0x01,  # features: many bits set
                        0x11,  # type=capillary whole blood (0x1), location=finger (0x1)
                        0x34,
                        0x12,  # e2e_crc: 0x1234
                    ]
                ),
                expected_value=CGMFeatureData(
                    features=CGMFeatureFlags(0x01FFFF),
                    cgm_type=CGMType.CAPILLARY_WHOLE_BLOOD,
                    sample_location=CGMSampleLocation.FINGER,
                    e2e_crc=0x1234,
                ),
                description="Many features, finger, capillary whole blood",
            ),
        ]

    def test_all_features_enabled(self) -> None:
        """Test with all 17 feature bits set."""
        char = CGMFeatureCharacteristic()
        all_features = 0x01FFFF
        data = bytearray(
            [
                all_features & 0xFF,
                (all_features >> 8) & 0xFF,
                (all_features >> 16) & 0xFF,
                0x59,  # ISF, subcutaneous
                0x00,
                0x00,  # CRC
            ]
        )
        result = char.parse_value(data)
        assert result.features & CGMFeatureFlags.CALIBRATION_SUPPORTED
        assert result.features & CGMFeatureFlags.E2E_CRC_SUPPORTED
        assert result.features & CGMFeatureFlags.CGM_QUALITY_SUPPORTED

    def test_no_features(self) -> None:
        """Test with no features enabled."""
        char = CGMFeatureCharacteristic()
        data = bytearray([0x00, 0x00, 0x00, 0x11, 0x00, 0x00])
        result = char.parse_value(data)
        assert int(result.features) == 0
        assert result.cgm_type == CGMType.CAPILLARY_WHOLE_BLOOD
        assert result.sample_location == CGMSampleLocation.FINGER

    def test_round_trip_feature(self) -> None:
        """Test encode/decode round-trip."""
        char = CGMFeatureCharacteristic()
        original = CGMFeatureData(
            features=CGMFeatureFlags.CALIBRATION_SUPPORTED
            | CGMFeatureFlags.E2E_CRC_SUPPORTED
            | CGMFeatureFlags.CGM_TREND_INFORMATION_SUPPORTED,
            cgm_type=CGMType.INTERSTITIAL_FLUID,
            sample_location=CGMSampleLocation.SUBCUTANEOUS_TISSUE,
            e2e_crc=0xABCD,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded.features == original.features
        assert decoded.cgm_type == original.cgm_type
        assert decoded.sample_location == original.sample_location
        assert decoded.e2e_crc == original.e2e_crc

    def test_nibble_packing(self) -> None:
        """Test that type and sample location nibbles are packed correctly."""
        char = CGMFeatureCharacteristic()
        original = CGMFeatureData(
            features=CGMFeatureFlags(0),
            cgm_type=CGMType.CONTROL_SOLUTION,  # 0xA
            sample_location=CGMSampleLocation.NOT_AVAILABLE,  # 0xF
            e2e_crc=0,
        )
        encoded = char.build_value(original)
        # byte 3 should be (0xF << 4) | 0xA = 0xFA
        assert encoded[3] == 0xFA

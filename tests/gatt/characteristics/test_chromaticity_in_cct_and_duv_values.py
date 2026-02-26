from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ChromaticityInCCTAndDuvValuesCharacteristic
from bluetooth_sig.gatt.characteristics.chromaticity_in_cct_and_duv_values import (
    ChromaticityInCCTAndDuvData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests

_DUV_RESOLUTION = 1e-5


class TestChromaticityInCCTAndDuvValuesCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ChromaticityInCCTAndDuvValuesCharacteristic:
        return ChromaticityInCCTAndDuvValuesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AE5"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=ChromaticityInCCTAndDuvData(
                    correlated_color_temperature=0,
                    chromaticity_distance_from_planckian=0.0,
                ),
                description="Zero CCT and zero Duv",
            ),
            CharacteristicTestData(
                # CCT = 6500 K (0x1964), Duv = 0.003 → raw = 300 (0x012C)
                input_data=bytearray([0x64, 0x19, 0x2C, 0x01]),
                expected_value=ChromaticityInCCTAndDuvData(
                    correlated_color_temperature=6500,
                    chromaticity_distance_from_planckian=300 * _DUV_RESOLUTION,
                ),
                description="Typical daylight CCT with positive Duv",
            ),
            CharacteristicTestData(
                # CCT = 2700 K (0x0A8C), Duv = -0.002 → raw = -200 (0xFF38 signed)
                input_data=bytearray([0x8C, 0x0A, 0x38, 0xFF]),
                expected_value=ChromaticityInCCTAndDuvData(
                    correlated_color_temperature=2700,
                    chromaticity_distance_from_planckian=-200 * _DUV_RESOLUTION,
                ),
                description="Warm white CCT with negative Duv",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = ChromaticityInCCTAndDuvValuesCharacteristic()
        original = ChromaticityInCCTAndDuvData(
            correlated_color_temperature=4000,
            chromaticity_distance_from_planckian=0.001,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded.correlated_color_temperature == original.correlated_color_temperature
        assert (
            abs(decoded.chromaticity_distance_from_planckian - original.chromaticity_distance_from_planckian)
            < _DUV_RESOLUTION
        )

    def test_validation_rejects_negative_cct(self) -> None:
        """Negative CCT is invalid."""
        with pytest.raises(ValueError, match="CCT"):
            ChromaticityInCCTAndDuvData(
                correlated_color_temperature=-1,
                chromaticity_distance_from_planckian=0.0,
            )

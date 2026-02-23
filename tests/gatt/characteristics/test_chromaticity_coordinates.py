from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ChromaticityCoordinatesCharacteristic
from bluetooth_sig.gatt.characteristics.chromaticity_coordinates import (
    ChromaticityCoordinatesData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests

# Chromaticity coordinate resolution per BLE spec
_RESOLUTION = 2**-16


class TestChromaticityCoordinatesCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ChromaticityCoordinatesCharacteristic:
        return ChromaticityCoordinatesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AE4"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=ChromaticityCoordinatesData(x=0.0, y=0.0),
                description="Zero coordinates",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=ChromaticityCoordinatesData(x=0xFFFF * _RESOLUTION, y=0xFFFF * _RESOLUTION),
                description="Maximum coordinates",
            ),
            CharacteristicTestData(
                # x=0x8000 (32768), y=0x4000 (16384)
                input_data=bytearray([0x00, 0x80, 0x00, 0x40]),
                expected_value=ChromaticityCoordinatesData(x=0x8000 * _RESOLUTION, y=0x4000 * _RESOLUTION),
                description="Mid-range coordinates",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = ChromaticityCoordinatesCharacteristic()
        original = ChromaticityCoordinatesData(x=0.3127, y=0.3290)
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert abs(decoded.x - original.x) < _RESOLUTION
        assert abs(decoded.y - original.y) < _RESOLUTION

    def test_validation_rejects_negative(self) -> None:
        """Negative coordinates are invalid."""
        with pytest.raises(ValueError, match="outside valid range"):
            ChromaticityCoordinatesData(x=-0.1, y=0.5)

    def test_validation_rejects_overflow(self) -> None:
        """Coordinates exceeding 1.0 are invalid (uint16 cannot represent them)."""
        with pytest.raises(ValueError, match="outside valid range"):
            ChromaticityCoordinatesData(x=1.1, y=0.5)

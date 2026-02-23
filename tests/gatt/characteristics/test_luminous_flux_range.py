from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import LuminousFluxRangeCharacteristic
from bluetooth_sig.gatt.characteristics.luminous_flux_range import LuminousFluxRangeData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLuminousFluxRangeCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> LuminousFluxRangeCharacteristic:
        return LuminousFluxRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B00"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=LuminousFluxRangeData(minimum=0, maximum=0),
                description="Zero flux range",
            ),
            CharacteristicTestData(
                # min = 100 (0x0064), max = 800 (0x0320)
                input_data=bytearray([0x64, 0x00, 0x20, 0x03]),
                expected_value=LuminousFluxRangeData(minimum=100, maximum=800),
                description="Typical LED bulb range (100-800 lm)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=LuminousFluxRangeData(minimum=65535, maximum=65535),
                description="Maximum flux range",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = LuminousFluxRangeCharacteristic()
        original = LuminousFluxRangeData(minimum=200, maximum=1600)
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_inverted_range(self) -> None:
        """Minimum > maximum is invalid."""
        with pytest.raises(ValueError, match="cannot be greater"):
            LuminousFluxRangeData(minimum=800, maximum=100)

    def test_validation_rejects_negative(self) -> None:
        """Negative flux is invalid for uint16."""
        with pytest.raises(ValueError, match="outside valid range"):
            LuminousFluxRangeData(minimum=-1, maximum=100)

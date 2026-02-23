"""Tests for SupportedSpeedRangeCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import SupportedSpeedRangeCharacteristic
from bluetooth_sig.gatt.characteristics.supported_speed_range import SupportedSpeedRangeData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSupportedSpeedRangeCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> SupportedSpeedRangeCharacteristic:
        return SupportedSpeedRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AD4"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=SupportedSpeedRangeData(
                    minimum=0.0,
                    maximum=0.0,
                    minimum_increment=0.0,
                ),
                description="Zero speed range",
            ),
            CharacteristicTestData(
                # min=1.00 km/h (100=0x0064), max=20.00 km/h (2000=0x07D0),
                # inc=0.10 km/h (10=0x000A)
                input_data=bytearray([0x64, 0x00, 0xD0, 0x07, 0x0A, 0x00]),
                expected_value=SupportedSpeedRangeData(
                    minimum=1.0,
                    maximum=20.0,
                    minimum_increment=0.1,
                ),
                description="Walking/running treadmill range (1-20 km/h, 0.1 step)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=SupportedSpeedRangeData(
                    minimum=655.35,
                    maximum=655.35,
                    minimum_increment=655.35,
                ),
                description="Maximum speed range",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = SupportedSpeedRangeCharacteristic()
        original = SupportedSpeedRangeData(
            minimum=5.0,
            maximum=30.0,
            minimum_increment=0.5,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_inverted_range(self) -> None:
        """Minimum > maximum is invalid."""
        with pytest.raises(ValueError, match="cannot be greater"):
            SupportedSpeedRangeData(minimum=20.0, maximum=5.0, minimum_increment=0.1)

    def test_validation_rejects_negative(self) -> None:
        """Negative speed is invalid for uint16."""
        with pytest.raises(ValueError, match="outside valid range"):
            SupportedSpeedRangeData(minimum=-1.0, maximum=10.0, minimum_increment=0.1)

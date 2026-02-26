"""Tests for SupportedHeartRateRangeCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import SupportedHeartRateRangeCharacteristic
from bluetooth_sig.gatt.characteristics.supported_heart_rate_range import (
    SupportedHeartRateRangeData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSupportedHeartRateRangeCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> SupportedHeartRateRangeCharacteristic:
        return SupportedHeartRateRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AD7"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=SupportedHeartRateRangeData(
                    minimum=0,
                    maximum=0,
                    minimum_increment=0,
                ),
                description="Zero heart rate range",
            ),
            CharacteristicTestData(
                # min=60 BPM, max=200 BPM, inc=1 BPM
                input_data=bytearray([0x3C, 0xC8, 0x01]),
                expected_value=SupportedHeartRateRangeData(
                    minimum=60,
                    maximum=200,
                    minimum_increment=1,
                ),
                description="Typical heart rate range (60-200 BPM, 1 BPM step)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF]),
                expected_value=SupportedHeartRateRangeData(
                    minimum=255,
                    maximum=255,
                    minimum_increment=255,
                ),
                description="Maximum heart rate range",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = SupportedHeartRateRangeCharacteristic()
        original = SupportedHeartRateRangeData(
            minimum=60,
            maximum=180,
            minimum_increment=1,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_inverted_range(self) -> None:
        """Minimum > maximum is invalid."""
        with pytest.raises(ValueError, match="cannot be greater"):
            SupportedHeartRateRangeData(minimum=200, maximum=60, minimum_increment=1)

    def test_validation_rejects_negative(self) -> None:
        """Negative heart rate is invalid for uint8."""
        with pytest.raises(ValueError, match="outside valid range"):
            SupportedHeartRateRangeData(minimum=-1, maximum=200, minimum_increment=1)

    def test_integer_values(self) -> None:
        """Heart rate values are integers (no scaling)."""
        data = SupportedHeartRateRangeData(minimum=60, maximum=200, minimum_increment=1)
        assert isinstance(data.minimum, int)
        assert isinstance(data.maximum, int)
        assert isinstance(data.minimum_increment, int)

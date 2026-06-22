from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cooking_step_status import (  # type: ignore[import-untyped]
    CookingStepStatusCharacteristic,
    CookingStepStatusData,
    CookingStepStatusFlags,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCookingStepStatusCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> CookingStepStatusCharacteristic:
        return CookingStepStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C28"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray([0x00, 0x01, 0x00, 0x2C, 0x01]),
                CookingStepStatusData(
                    flags=CookingStepStatusFlags(0), cooking_step_index=1, remaining_time_seconds=300
                ),
                "step 1, 300s",
            ),
            CharacteristicTestData(
                bytearray([0x04, 0x02, 0x00, 0x00, 0x00]),
                CookingStepStatusData(
                    flags=CookingStepStatusFlags.COOKING_STEP_STARTED,
                    cooking_step_index=2,
                    remaining_time_seconds=0,
                ),
                "started and active",
            ),
        ]

    def test_short_payload_fails(self, characteristic: CookingStepStatusCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00, 0x01]))

    def test_oversized_payload_fails(self, characteristic: CookingStepStatusCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00, 0x01, 0x00, 0x2C, 0x01, 0x00]))

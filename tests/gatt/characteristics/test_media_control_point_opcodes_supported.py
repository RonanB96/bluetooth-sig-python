"""Tests for MediaControlPointOpcodesSupportedCharacteristic (2BA5)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.media_control_point_opcodes_supported import (
    MediaControlPointOpcodes,
    MediaControlPointOpcodesSupportedCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMediaControlPointOpcodesSupported(CommonCharacteristicTests):
    """Test suite for MediaControlPointOpcodesSupportedCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> MediaControlPointOpcodesSupportedCharacteristic:
        return MediaControlPointOpcodesSupportedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BA5"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00, 0x00, 0x00]), MediaControlPointOpcodes(0), "No opcodes"),
            CharacteristicTestData(bytearray([0x01, 0x00, 0x00, 0x00]), MediaControlPointOpcodes.PLAY, "Play"),
            CharacteristicTestData(
                bytearray([0x03, 0x00, 0x00, 0x00]),
                MediaControlPointOpcodes.PLAY | MediaControlPointOpcodes.PAUSE,
                "Play+Pause",
            ),
        ]

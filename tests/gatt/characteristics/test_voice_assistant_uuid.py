from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.voice_assistant_uuid import (  # type: ignore[import-untyped]
    VoiceAssistantUUIDCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVoiceAssistantUUIDCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> VoiceAssistantUUIDCharacteristic:
        return VoiceAssistantUUIDCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C32"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        value = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        value2 = bytes.fromhex("FFFFFFFF00000000AAAABBBBCCCCDDDD")
        return [
            CharacteristicTestData(bytearray(value), value, "uuid #1"),
            CharacteristicTestData(bytearray(value2), value2, "uuid #2"),
        ]

    def test_short_payload_fails(self, characteristic: VoiceAssistantUUIDCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00] * 15))

    def test_build_wrong_length_fails(self, characteristic: VoiceAssistantUUIDCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(b"\x01\x02")

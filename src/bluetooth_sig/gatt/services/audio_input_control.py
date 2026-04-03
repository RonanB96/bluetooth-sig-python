"""AudioInputControl Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class AudioInputControlService(BaseGattService):
    """Audio Input Control Service implementation (0x1843).

    Controls audio input devices including gain, mute state, and
    input type configuration.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.AUDIO_INPUT_STATE: True,
        CharacteristicName.AUDIO_INPUT_CONTROL_POINT: True,
        CharacteristicName.AUDIO_INPUT_DESCRIPTION: True,
        CharacteristicName.AUDIO_INPUT_STATUS: True,
        CharacteristicName.AUDIO_INPUT_TYPE: True,
        CharacteristicName.GAIN_SETTINGS_ATTRIBUTE: True,
    }

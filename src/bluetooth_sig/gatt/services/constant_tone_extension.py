"""ConstantToneExtension Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class ConstantToneExtensionService(BaseGattService):
    """Constant Tone Extension Service implementation (0x184A).

    Enables Constant Tone Extension (CTE) for direction finding
    and angle-of-arrival/departure measurements.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.CONSTANT_TONE_EXTENSION_ENABLE: False,
        CharacteristicName.ADVERTISING_CONSTANT_TONE_EXTENSION_MINIMUM_LENGTH: False,
        CharacteristicName.ADVERTISING_CONSTANT_TONE_EXTENSION_MINIMUM_TRANSMIT_COUNT: False,
        CharacteristicName.ADVERTISING_CONSTANT_TONE_EXTENSION_TRANSMIT_DURATION: False,
        CharacteristicName.ADVERTISING_CONSTANT_TONE_EXTENSION_INTERVAL: False,
        CharacteristicName.ADVERTISING_CONSTANT_TONE_EXTENSION_PHY: False,
    }

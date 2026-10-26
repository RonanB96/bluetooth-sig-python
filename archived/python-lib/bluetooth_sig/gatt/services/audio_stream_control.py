"""AudioStreamControl Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class AudioStreamControlService(BaseGattService):
    """Audio Stream Control Service implementation (0x184E).

    Manages LE Audio stream endpoints (ASEs) for unicast audio.
    Controls sink and source audio stream configurations.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.ASE_CONTROL_POINT: True,
        CharacteristicName.SINK_ASE: False,
        CharacteristicName.SOURCE_ASE: False,
    }

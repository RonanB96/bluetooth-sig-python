"""ElapsedTime Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class ElapsedTimeService(BaseGattService):
    """Elapsed Time Service implementation (0x183F).

    Provides elapsed time tracking for BLE devices without a
    real-time clock.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.CURRENT_ELAPSED_TIME: True,
    }

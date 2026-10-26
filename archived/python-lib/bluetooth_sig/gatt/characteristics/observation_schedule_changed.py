"""Observation Schedule Changed characteristic (0x2B89)."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class ObservationScheduleChangedCharacteristic(BaseCharacteristic[bool]):
    """Observation Schedule Changed characteristic (0x2B89).

    org.bluetooth.characteristic.observation_schedule_changed

    Notification-only characteristic. Presence of a notification
    indicates that the observation schedule has changed.
    """

    expected_length: int = 0

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bool:
        return True

    def _encode_value(self, data: bool) -> bytearray:
        return bytearray()

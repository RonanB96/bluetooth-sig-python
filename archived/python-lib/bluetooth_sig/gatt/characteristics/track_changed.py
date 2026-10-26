"""Track Changed characteristic (0x2B96)."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class TrackChangedCharacteristic(BaseCharacteristic[bool]):
    """Track Changed characteristic (0x2B96).

    org.bluetooth.characteristic.track_changed

    Notification-only characteristic. Presence of a notification
    indicates the current track has changed.
    """

    expected_length: int = 0

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bool:
        return True

    def _encode_value(self, data: bool) -> bytearray:
        return bytearray()

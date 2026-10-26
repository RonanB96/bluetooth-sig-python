"""Set Member Rank characteristic (0x2B87)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class SetMemberRankCharacteristic(BaseCharacteristic[int]):
    """Set Member Rank characteristic (0x2B87).

    org.bluetooth.characteristic.rank_characteristic

    The rank of a member within a coordinated set.
    """

    _template = Uint8Template()

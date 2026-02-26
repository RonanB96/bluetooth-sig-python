"""Global Trade Item Number characteristic (0x2AFA)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint48Template


class GlobalTradeItemNumberCharacteristic(BaseCharacteristic[int]):
    """Global Trade Item Number characteristic (0x2AFA).

    org.bluetooth.characteristic.global_trade_item_number

    An identifier for trade items, defined by GS1.
    Encoded as a 48-bit unsigned integer (6 bytes).
    A value of 0x000000000000 represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0x000000000000).
    """

    _template = Uint48Template()

"""True Wind Direction characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class TrueWindDirectionCharacteristic(BaseCharacteristic):
    """True Wind Direction measurement characteristic."""

    _template = ScaledUint16Template()

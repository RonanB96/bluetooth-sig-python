"""Wind Chill characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Sint8Template


class WindChillCharacteristic(BaseCharacteristic):
    """Wind Chill measurement characteristic."""

    _template = Sint8Template()

    _characteristic_name: str = "Wind Chill"

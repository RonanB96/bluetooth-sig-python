"""Coordinated Set Name characteristic (0x2C1A)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class CoordinatedSetNameCharacteristic(BaseCharacteristic[str]):
    """Coordinated Set Name characteristic (0x2C1A).

    org.bluetooth.characteristic.coordinated_set_name

    UTF-8 name shared by members of a coordinated set.
    """

    _template = Utf8StringTemplate(max_length=128)
    allow_variable_length = True

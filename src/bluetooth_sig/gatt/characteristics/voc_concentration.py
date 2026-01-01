"""VOC Concentration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class VOCConcentrationCharacteristic(BaseCharacteristic):
    """Volatile Organic Compounds concentration characteristic (0x2BE7).

    Uses uint16 format as per SIG specification.
    Unit: ppb (parts per billion)
    Range: 0-65535 (uint16)
    Special values per SIG spec: 0xFFFE (≥65534 ppb), 0xFFFF (value not known)
    """

    _template = Uint16Template()

    _manual_unit: str | None = "ppb"  # Unit as per SIG specification

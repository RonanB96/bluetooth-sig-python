"""Sound Pressure Level characteristic implementation."""

from .base import BaseCharacteristic
from .templates import ScaledSint16Template


class SoundPressureLevelCharacteristic(BaseCharacteristic):
    """Power Specification characteristic (0x2B06).

    Measures power specification values.
    Format: sint16 (2 bytes) with 0.1 resolution.
    """

    _template = ScaledSint16Template(scale_factor=0.1)

    _characteristic_name: str = "Power Specification"

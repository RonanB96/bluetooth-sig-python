"""Sound Pressure Level characteristic implementation."""

from dataclasses import dataclass

from .templates import SignedSoundPressureCharacteristic


@dataclass
class SoundPressureLevelCharacteristic(SignedSoundPressureCharacteristic):
    """Power Specification characteristic (0x2B06).

    Measures power specification values.
    """

    _characteristic_name: str = "Power Specification"

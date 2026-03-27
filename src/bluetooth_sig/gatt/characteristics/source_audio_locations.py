"""Source Audio Locations characteristic (0x2BCC)."""

from __future__ import annotations

from .audio_location import AudioLocation
from .base import BaseCharacteristic
from .templates import FlagTemplate


class SourceAudioLocationsCharacteristic(BaseCharacteristic[AudioLocation]):
    """Source Audio Locations characteristic (0x2BCC).

    org.bluetooth.characteristic.source_audio_locations

    Bitfield indicating the audio location channels for the source role.
    Reuses AudioLocation flags from the Audio Location characteristic.
    """

    _template = FlagTemplate.uint32(AudioLocation)

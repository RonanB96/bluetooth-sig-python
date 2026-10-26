"""Sink Audio Locations characteristic (0x2BCA)."""

from __future__ import annotations

from .audio_location import AudioLocation
from .base import BaseCharacteristic
from .templates import FlagTemplate


class SinkAudioLocationsCharacteristic(BaseCharacteristic[AudioLocation]):
    """Sink Audio Locations characteristic (0x2BCA).

    org.bluetooth.characteristic.sink_audio_locations

    Bitfield indicating the audio location channels for the sink role.
    Reuses AudioLocation flags from the Audio Location characteristic.
    """

    _template = FlagTemplate.uint32(AudioLocation)

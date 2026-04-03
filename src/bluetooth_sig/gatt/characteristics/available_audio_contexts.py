"""Available Audio Contexts characteristic (0x2BCD)."""

from __future__ import annotations

import msgspec

from bluetooth_sig.types.audio_context_type import AudioContextType

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class AvailableAudioContextsData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Available Audio Contexts characteristic.

    Contains the currently available sink and source audio contexts.
    """

    sink_audio_contexts: AudioContextType
    source_audio_contexts: AudioContextType


class AvailableAudioContextsCharacteristic(BaseCharacteristic[AvailableAudioContextsData]):
    """Available Audio Contexts characteristic (0x2BCD).

    org.bluetooth.characteristic.available_audio_contexts

    Reports the currently available audio contexts for sink and source.
    """

    expected_length = 4

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> AvailableAudioContextsData:
        """Parse Available Audio Contexts data.

        Format: sink_audio_contexts (uint16 LE) + source_audio_contexts (uint16 LE).
        """
        sink = AudioContextType(DataParser.parse_int16(data, 0, signed=False))
        source = AudioContextType(DataParser.parse_int16(data, 2, signed=False))
        return AvailableAudioContextsData(
            sink_audio_contexts=sink,
            source_audio_contexts=source,
        )

    def _encode_value(self, data: AvailableAudioContextsData) -> bytearray:
        """Encode Available Audio Contexts data to bytes."""
        result = bytearray()
        result += DataParser.encode_int16(int(data.sink_audio_contexts))
        result += DataParser.encode_int16(int(data.source_audio_contexts))
        return result

"""Audio context type definitions shared by audio context characteristics."""

from __future__ import annotations

from enum import IntFlag


class AudioContextType(IntFlag):
    """Audio context type flags (uint16 bitfield).

    Used by Available Audio Contexts and Supported Audio Contexts.
    """

    UNSPECIFIED = 0x0001
    CONVERSATIONAL = 0x0002
    MEDIA = 0x0004
    GAME = 0x0008
    INSTRUCTIONAL = 0x0010
    VOICE_ASSISTANTS = 0x0020
    LIVE = 0x0040
    SOUND_EFFECTS = 0x0080
    NOTIFICATIONS = 0x0100
    RINGTONE = 0x0200
    ALERTS = 0x0400
    EMERGENCY_ALARM = 0x0800

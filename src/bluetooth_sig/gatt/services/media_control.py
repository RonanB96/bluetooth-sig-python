"""MediaControl Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class MediaControlService(BaseGattService):
    """Media Control Service implementation (0x1848).

    Controls media playback including play/pause, track navigation,
    and media player state reporting.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.MEDIA_PLAYER_NAME: True,
        CharacteristicName.MEDIA_STATE: True,
        CharacteristicName.TRACK_CHANGED: True,
        CharacteristicName.TRACK_TITLE: True,
        CharacteristicName.TRACK_DURATION: True,
        CharacteristicName.TRACK_POSITION: True,
        CharacteristicName.CONTENT_CONTROL_ID: True,
        CharacteristicName.MEDIA_CONTROL_POINT: False,
        CharacteristicName.MEDIA_CONTROL_POINT_OPCODES_SUPPORTED: False,
        CharacteristicName.MEDIA_PLAYER_ICON_OBJECT_ID: False,
        CharacteristicName.MEDIA_PLAYER_ICON_URL: False,
        CharacteristicName.PLAYBACK_SPEED: False,
        CharacteristicName.SEEKING_SPEED: False,
        CharacteristicName.CURRENT_TRACK_SEGMENTS_OBJECT_ID: False,
        CharacteristicName.CURRENT_TRACK_OBJECT_ID: False,
        CharacteristicName.NEXT_TRACK_OBJECT_ID: False,
        CharacteristicName.CURRENT_GROUP_OBJECT_ID: False,
        CharacteristicName.PARENT_GROUP_OBJECT_ID: False,
        CharacteristicName.PLAYING_ORDER: False,
        CharacteristicName.PLAYING_ORDERS_SUPPORTED: False,
        CharacteristicName.SEARCH_CONTROL_POINT: False,
        CharacteristicName.SEARCH_RESULTS_OBJECT_ID: False,
    }

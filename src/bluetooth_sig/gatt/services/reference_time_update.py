"""Reference Time Update Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class ReferenceTimeUpdateService(BaseGattService):
    """Reference Time Update Service implementation.

    Allows clients to request time updates from reference time sources.

    Contains characteristics related to time updates:
    - Time Update Control Point - Required
    - Time Update State - Optional
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.TIME_UPDATE_CONTROL_POINT: True,  # required
        CharacteristicName.TIME_UPDATE_STATE: False,  # optional
    }

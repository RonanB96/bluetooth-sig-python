"""Next DST Change Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class NextDstChangeService(BaseGattService):
    """Next DST Change Service implementation.

    Exposes the date and time of the next Daylight Saving Time change.

    Contains characteristics related to DST changes:
    - Time with DST - Required
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.TIME_WITH_DST: True,  # required
    }

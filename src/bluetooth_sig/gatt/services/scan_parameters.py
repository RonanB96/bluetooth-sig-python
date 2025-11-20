"""Scan Parameters service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class ScanParametersService(BaseGattService):
    """Scan Parameters service implementation.

    Contains characteristics that control BLE scanning parameters:
    - Scan Interval Window - Required
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.SCAN_INTERVAL_WINDOW: True,  # required
    }

"""Scan Refresh characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class ScanRefreshCharacteristic(BaseCharacteristic[int]):
    """Scan Refresh characteristic (0x2A31).

    org.bluetooth.characteristic.scan_refresh

    Requests the server to refresh the scan.
    """

    _template = Uint8Template()

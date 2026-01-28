"""Utility helpers exposed by ``bluetooth_sig.utils``.

This module re-exports common RSSI utilities.
"""

from __future__ import annotations

from .rssi_utils import get_rssi_quality

__all__ = [
    "get_rssi_quality",
]

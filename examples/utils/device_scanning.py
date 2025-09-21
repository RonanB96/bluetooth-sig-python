#!/usr/bin/env python3
"""Device scanning utilities for BLE examples.

Note: Bleak scanning functions removed - only bleak-retry-connector supported.
This module now only provides device info extraction utilities.
"""

from __future__ import annotations

from typing import Any


def safe_get_device_info(device: Any) -> tuple[str, str, str | None]:
    """Safely extract device information from any BLE device object.

    Args:
        device: BLE device object from any library

    Returns:
        (name, address, rssi) tuple with safe fallbacks
    """
    name = getattr(device, "name", None) or "Unknown"
    address = getattr(device, "address", "Unknown")
    rssi = getattr(device, "rssi", None)
    return name, address, rssi

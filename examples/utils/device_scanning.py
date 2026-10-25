#!/usr/bin/env python3
"""Device scanning utilities for BLE examples.

Note: Bleak scanning functions removed - only bleak-retry-connector supported.
This module now only provides device info extraction utilities.
"""

from __future__ import annotations

from typing import Any


def safe_get_device_info(device: Any) -> tuple[str, str, str | None]:  # noqa: ANN401  # Works with any BLE library's device type
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


def scan_with_bluepy(timeout: float = 10.0) -> list[tuple[str, str, int | None]]:
    """Scan for BLE devices using BluePy.

    Args:
        timeout: Scan timeout in seconds

    Returns:
        List of (name, address, rssi) tuples for discovered devices

    Raises:
        ImportError: If BluePy is not available
        RuntimeError: If scan fails
    """
    try:
        from bluepy.btle import ScanEntry, Scanner
    except ImportError as e:
        raise ImportError("BluePy not available. Install with: pip install bluepy") from e

    try:
        scanner = Scanner()
        print(f"Scanning for BLE devices with BluePy (timeout: {timeout}s)...")
        devices = scanner.scan(int(timeout))  # type: ignore[misc]

        results: list[tuple[str, str, int | None]] = []
        for device in devices:  # type: ignore[misc]
            # BluePy ScanEntry has addr, rssi, and getValue methods for scan data
            address: str = device.addr  # type: ignore[misc]
            rssi_val: int = device.rssi  # type: ignore[misc]

            # Try to get device name from scan data using ScanEntry constants
            name = device.getValueText(ScanEntry.COMPLETE_LOCAL_NAME)  # type: ignore[misc]
            if not name:
                name = device.getValueText(ScanEntry.SHORT_LOCAL_NAME)  # type: ignore[misc]
            if not name:
                name = "Unknown"

            results.append((str(name), str(address), rssi_val))  # type: ignore[misc]

        print(f"Found {len(results)} devices")
        return results

    except Exception as e:
        raise RuntimeError(f"BluePy scan failed: {e}") from e

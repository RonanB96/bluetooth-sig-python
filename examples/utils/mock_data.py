#!/usr/bin/env python3
"""Mock data utilities for BLE examples.

This module provides mock BLE data for testing without hardware.
"""

from __future__ import annotations


def mock_ble_data() -> dict[str, bytes]:
    """Generate mock BLE data for testing without hardware.

    Returns:
        Dict mapping UUID to mock raw data
    """
    return {
        "2A19": bytes([0x64]),  # 100% battery
        "2A00": b"Mock Device",  # Device name
        "2A6E": bytes([0x64, 0x09]),  # Temperature: 24.04°C
        "2A6F": bytes([0x10, 0x27]),  # Humidity: 100.0%
        "2A6D": bytes([0x40, 0x9C, 0x00, 0x00]),  # Pressure: 40.0 kPa
        "2A29": b"Bluetooth SIG",  # Manufacturer name
    }


def get_default_characteristic_uuids() -> list[str]:
    """Get a default set of commonly available characteristics for testing.

    DEPRECATED: Use comprehensive_device_analysis() instead for real device discovery.
    This function only returns predefined UUIDs and misses actual device capabilities.
    """
    return [
        "2A19",  # Battery Level
        "2A00",  # Device Name
        "2A6E",  # Temperature
        "2A6F",  # Humidity
        "2A6D",  # Pressure
        "2A29",  # Manufacturer Name
    ]

"""RSSI utility functions for BLE operations."""

from __future__ import annotations


def get_rssi_quality(rssi: int) -> str:
    """Get human-readable RSSI signal quality description.

    Args:
        rssi: RSSI value in dBm

    Returns:
        Human-readable quality description

    """
    if rssi >= -30:
        return "Excellent"
    if rssi >= -50:
        return "Very Good"
    if rssi >= -60:
        return "Good"
    if rssi >= -70:
        return "Fair"
    if rssi >= -80:
        return "Weak"
    return "Very Weak"

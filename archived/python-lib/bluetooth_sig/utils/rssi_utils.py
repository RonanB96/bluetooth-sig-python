"""RSSI utility functions for BLE operations."""

from __future__ import annotations

# RSSI quality thresholds (in dBm)
RSSI_EXCELLENT = -30
RSSI_VERY_GOOD = -50
RSSI_GOOD = -60
RSSI_FAIR = -70
RSSI_WEAK = -80


def get_rssi_quality(rssi: int) -> str:
    """Get human-readable RSSI signal quality description.

    Args:
        rssi: RSSI value in dBm

    Returns:
        Human-readable quality description

    """
    if rssi >= RSSI_EXCELLENT:
        return "Excellent"
    if rssi >= RSSI_VERY_GOOD:
        return "Very Good"
    if rssi >= RSSI_GOOD:
        return "Good"
    if rssi >= RSSI_FAIR:
        return "Fair"
    if rssi >= RSSI_WEAK:
        return "Weak"
    return "Very Weak"

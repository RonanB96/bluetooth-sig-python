"""Device abstraction with advertising and connection subsystems.

The Device class provides a unified interface for BLE device operations.
Additional composition-based subsystems are available for focused use cases:

- DeviceAdvertising: Advertising packet interpretation
- DeviceConnected: GATT connection operations
"""

from __future__ import annotations

from bluetooth_sig.device.advertising import DeviceAdvertising
from bluetooth_sig.device.connected import (
    DeviceConnected,
    DeviceEncryption,
    DeviceService,
)
from bluetooth_sig.device.device import Device, SIGTranslatorProtocol

__all__ = [
    "Device",
    "DeviceAdvertising",
    "DeviceConnected",
    "DeviceEncryption",
    "DeviceService",
    "SIGTranslatorProtocol",
]

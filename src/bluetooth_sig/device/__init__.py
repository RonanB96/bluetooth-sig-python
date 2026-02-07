"""Device abstraction with advertising, connection, and peripheral subsystems.

The Device class provides a unified interface for BLE device operations.
Additional composition-based subsystems are available for focused use cases:

- DeviceAdvertising: Advertising packet interpretation
- DeviceConnected: GATT connection operations (client/central role)

For server/peripheral role, see PeripheralManagerProtocol.
"""

from __future__ import annotations

from bluetooth_sig.device.advertising import DeviceAdvertising
from bluetooth_sig.device.client import ClientManagerProtocol
from bluetooth_sig.device.connected import (
    DeviceConnected,
    DeviceEncryption,
    DeviceService,
)
from bluetooth_sig.device.device import Device, SIGTranslatorProtocol
from bluetooth_sig.device.peripheral import (
    CharacteristicDefinition,
    PeripheralManagerProtocol,
    ServiceDefinition,
)

__all__ = [
    "CharacteristicDefinition",
    "ClientManagerProtocol",
    "Device",
    "DeviceAdvertising",
    "DeviceConnected",
    "DeviceEncryption",
    "DeviceService",
    "PeripheralManagerProtocol",
    "ServiceDefinition",
    "SIGTranslatorProtocol",
]

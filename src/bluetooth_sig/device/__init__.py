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
from bluetooth_sig.device.dependency_resolver import DependencyResolutionMode
from bluetooth_sig.device.device import Device
from bluetooth_sig.device.peripheral import (
    CharacteristicDefinition,
    PeripheralManagerProtocol,
    ServiceDefinition,
)
from bluetooth_sig.device.peripheral_device import PeripheralDevice
from bluetooth_sig.device.protocols import SIGTranslatorProtocol

__all__ = [
    "CharacteristicDefinition",
    "ClientManagerProtocol",
    "DependencyResolutionMode",
    "Device",
    "DeviceAdvertising",
    "DeviceConnected",
    "DeviceEncryption",
    "DeviceService",
    "PeripheralDevice",
    "PeripheralManagerProtocol",
    "ServiceDefinition",
    "SIGTranslatorProtocol",
]

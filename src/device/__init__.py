"""Device package for Bluetooth GATT device abstraction.

This package contains the Device class which provides a high-level representation
of a BLE device with all its services, characteristics, encryption, and advertiser data.
"""

# Import the device components from the dedicated device module
from .device import (
    Device,
    SIGTranslatorProtocol,
    UnknownService,
)

__all__ = [
    "Device",
    "SIGTranslatorProtocol",
    "UnknownService",
]

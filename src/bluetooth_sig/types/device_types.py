"""Device-related data types for BLE device management."""

from __future__ import annotations

import msgspec

from ..gatt.services.base import BaseGattService
from .protocols import CharacteristicDataProtocol


class DeviceService(msgspec.Struct, kw_only=True):
    """Represents a service on a device with its characteristics."""

    service: BaseGattService
    characteristics: dict[str, CharacteristicDataProtocol] = msgspec.field(default_factory=dict)


class DeviceEncryption(msgspec.Struct, kw_only=True):
    """Encryption requirements and status for the device."""

    requires_authentication: bool = False
    requires_encryption: bool = False
    encryption_level: str = ""
    security_mode: int = 0
    key_size: int = 0

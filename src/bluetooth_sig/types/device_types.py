"""Device-related data types for BLE device management."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..gatt.services.base import BaseGattService
from .protocols import CharacteristicDataProtocol


@dataclass
class DeviceService:
    """Represents a service on a device with its characteristics."""

    service: BaseGattService
    characteristics: dict[str, CharacteristicDataProtocol] = field(default_factory=dict)


@dataclass
class DeviceEncryption:
    """Encryption requirements and status for the device."""

    requires_authentication: bool = False
    requires_encryption: bool = False
    encryption_level: str = ""
    security_mode: int | None = None
    key_size: int | None = None

"""Device-related data types for BLE device management."""

from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

from .advertising import AdvertisingData

if TYPE_CHECKING:
    from ..gatt.characteristics.base import BaseCharacteristic
    from ..gatt.services.base import BaseGattService


class ScannedDevice(msgspec.Struct, kw_only=True):
    """Minimal wrapper for a device discovered during BLE scanning.

    Attributes:
        address: Bluetooth MAC address or platform-specific identifier
        name: OS-provided device name (may be None)
        advertisement_data: Complete parsed advertising data (includes rssi, manufacturer_data, etc.)

    """

    address: str
    name: str | None = None
    advertisement_data: AdvertisingData | None = None


class DeviceService(msgspec.Struct, kw_only=True):
    r"""Represents a service on a device with its characteristics.

    The characteristics dictionary stores BaseCharacteristic instances.
    Access parsed data via characteristic.last_parsed property.

    This provides a single source of truth: BaseCharacteristic instances
    maintain their own last_parsed CharacteristicData.

    Example:
        ```python
        # After discover_services() and read()
        service = device.services["0000180f..."]  # Battery Service
        battery_char = service.characteristics["00002a19..."]  # BatteryLevelCharacteristic instance

        # Access last parsed result
        if battery_char.last_parsed:
            print(f"Battery: {battery_char.last_parsed.value}%")

        # Or decode new data
        parsed_value = battery_char.decode_value(raw_data)
        ```
    """

    service: BaseGattService
    characteristics: dict[str, BaseCharacteristic] = msgspec.field(default_factory=dict)


class DeviceEncryption(msgspec.Struct, kw_only=True):
    """Encryption requirements and status for the device."""

    requires_authentication: bool = False
    requires_encryption: bool = False
    encryption_level: str = ""
    security_mode: int = 0
    key_size: int = 0

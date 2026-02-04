"""Data structures for BLE peripheral/GATT server definitions.

This module provides the data structures used to define GATT services
and characteristics for peripheral devices. These are used by
PeripheralManagerProtocol implementations.

Analogous to device_types.py and connected.py structures on the client side.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.types.gatt_enums import GattProperty
from bluetooth_sig.types.uuid import BluetoothUUID


@dataclass
class CharacteristicDefinition:
    """Definition for a GATT characteristic to be hosted on a peripheral.

    This bridges bluetooth-sig characteristic classes with the peripheral backend.
    Use `from_characteristic()` to create from a BaseCharacteristic instance.

    Attributes:
        uuid: The UUID of the characteristic (16-bit short or 128-bit full).
        properties: GATT properties (read, write, notify, indicate, etc.).
        initial_value: Initial value to serve when clients read the characteristic.
        readable: Whether clients can read this characteristic.
        writable: Whether clients can write to this characteristic.
        on_read: Optional callback to dynamically generate value on read requests.
        on_write: Optional callback when clients write to this characteristic.

    """

    uuid: BluetoothUUID
    """The UUID of the characteristic (16-bit short or 128-bit full)."""

    properties: GattProperty
    """GATT properties (read, write, notify, indicate, etc.)."""

    initial_value: bytearray = field(default_factory=bytearray)
    """Initial value to serve when clients read the characteristic."""

    readable: bool = True
    """Whether clients can read this characteristic."""

    writable: bool = False
    """Whether clients can write to this characteristic."""

    on_read: Callable[[], bytearray] | None = None
    """Optional callback to dynamically generate value on read requests."""

    on_write: Callable[[bytearray], None] | None = None
    """Optional callback when clients write to this characteristic."""

    @classmethod
    def from_characteristic(
        cls,
        characteristic: BaseCharacteristic[Any],
        value: Any,  # noqa: ANN401
        *,
        properties: GattProperty | None = None,
        on_read: Callable[[], bytearray] | None = None,
        on_write: Callable[[bytearray], None] | None = None,
    ) -> CharacteristicDefinition:
        """Create a CharacteristicDefinition from a bluetooth-sig characteristic.

        This uses the characteristic's `build_value()` method to encode the
        initial value, demonstrating the library's encoding capabilities.

        Args:
            characteristic: The bluetooth-sig characteristic class instance
            value: The Python value to encode as the initial characteristic value
            properties: GATT properties. If None, defaults to READ + NOTIFY.
            on_read: Optional callback for dynamic value generation
            on_write: Optional callback for write handling

        Returns:
            CharacteristicDefinition ready for use with PeripheralManagerProtocol

        Example::
            >>> from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
            >>> char = BatteryLevelCharacteristic()
            >>> defn = CharacteristicDefinition.from_characteristic(char, 85)
            >>> defn.initial_value
            bytearray(b'U')  # 85 encoded as single byte

        """
        # Encode the value using the characteristic's build_value method
        encoded = characteristic.build_value(value)

        # Default properties: readable + notify
        if properties is None:
            properties = GattProperty.READ | GattProperty.NOTIFY

        # Determine read/write from properties
        readable = bool(properties & GattProperty.READ)
        writable = bool(properties & (GattProperty.WRITE | GattProperty.WRITE_WITHOUT_RESPONSE))

        return cls(
            uuid=BluetoothUUID(str(characteristic.uuid)),
            properties=properties,
            initial_value=encoded,
            readable=readable,
            writable=writable,
            on_read=on_read,
            on_write=on_write,
        )


@dataclass
class ServiceDefinition:
    """Definition for a GATT service to be hosted on a peripheral.

    Attributes:
        uuid: The UUID of the service (16-bit short or 128-bit full).
        characteristics: List of characteristics in this service.
        primary: Whether this is a primary service (vs secondary/included).

    """

    uuid: BluetoothUUID
    """The UUID of the service (16-bit short or 128-bit full)."""

    characteristics: list[CharacteristicDefinition] = field(default_factory=list)
    """List of characteristics in this service."""

    primary: bool = True
    """Whether this is a primary service (vs secondary/included)."""


__all__ = [
    "CharacteristicDefinition",
    "ServiceDefinition",
]

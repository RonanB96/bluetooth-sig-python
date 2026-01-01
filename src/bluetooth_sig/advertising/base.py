"""Base classes for advertising data interpreters.

Advertising data interpretation follows a two-layer architecture:

1. PDU Parsing (AdvertisingPDUParser): Raw bytes → AD structures
   - Extracts manufacturer_data, service_data, flags, local_name, etc.
   - Framework-agnostic, works with raw BLE PDU bytes

2. Data Interpretation (AdvertisingDataInterpreter): AD structures → typed results
   - Interprets vendor-specific protocols (BTHome, Xiaomi, RuuviTag, etc.)
   - Returns strongly-typed sensor data (temperature, humidity, etc.)
   - Maintains per-device state (encryption counters, packet IDs)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Generic, TypeVar

import msgspec

from bluetooth_sig.types.uuid import BluetoothUUID

# Generic type variable for interpreter result types
T = TypeVar("T")


class DataSource(Enum):
    """Primary data source for interpreter routing."""

    MANUFACTURER = "manufacturer"
    SERVICE = "service"
    LOCAL_NAME = "local_name"


class AdvertisingInterpreterInfo(msgspec.Struct, kw_only=True, frozen=True):
    """Interpreter metadata for routing and identification."""

    company_id: int | None = None
    service_uuid: BluetoothUUID | None = None
    name: str = ""
    data_source: DataSource = DataSource.MANUFACTURER


class AdvertisingDataInterpreter(ABC, Generic[T]):
    """Base class for vendor-specific advertising data interpretation.

    Interprets manufacturer_data and service_data from BLE advertisements
    into strongly-typed domain objects (sensor readings, device state, etc.).

    Workflow:
        1. Registry routes advertisement to interpreter class via supports()
        2. Device creates/reuses interpreter instance per (mac_address, interpreter_type)
        3. interpreter.interpret() decodes payload, returns typed result
        4. Interpreter maintains internal state (counters, flags) across calls

    Example:
        class BTHomeInterpreter(AdvertisingDataInterpreter[BTHomeData]):
            _info = AdvertisingInterpreterInfo(
                service_uuid=BluetoothUUID("0000fcd2-0000-1000-8000-00805f9b34fb"),
                name="BTHome",
                data_source=DataSource.SERVICE,
            )

            @classmethod
            def supports(cls, manufacturer_data, service_data, local_name):
                return "0000fcd2-0000-1000-8000-00805f9b34fb" in service_data

            def interpret(self, manufacturer_data, service_data, local_name, rssi):
                # Parse BTHome service data and return BTHomeData
                ...
    """

    _info: AdvertisingInterpreterInfo
    _is_base_class: bool = False

    def __init__(self, mac_address: str, bindkey: bytes | None = None) -> None:
        """Create interpreter instance for a specific device.

        Args:
            mac_address: BLE device address (used for encryption nonce)
            bindkey: Optional encryption key for encrypted advertisements

        """
        self._mac_address = mac_address
        self._bindkey = bindkey
        self._state: dict[str, Any] = {}

    @property
    def mac_address(self) -> str:
        """Device MAC address."""
        return self._mac_address

    @property
    def bindkey(self) -> bytes | None:
        """Encryption key for this device."""
        return self._bindkey

    @bindkey.setter
    def bindkey(self, value: bytes | None) -> None:
        """Set encryption key."""
        self._bindkey = value

    @property
    def state(self) -> dict[str, Any]:
        """Return the protocol-specific state dictionary."""
        return self._state

    @property
    def info(self) -> AdvertisingInterpreterInfo:
        """Interpreter metadata."""
        return self._info

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Auto-register interpreter subclasses with the registry."""
        super().__init_subclass__(**kwargs)

        if getattr(cls, "_is_base_class", False):
            return
        if not hasattr(cls, "_info"):
            return

        # pylint: disable-next=import-outside-toplevel,cyclic-import
        from bluetooth_sig.advertising.registry import advertising_interpreter_registry

        advertising_interpreter_registry.register(cls)

    @classmethod
    @abstractmethod
    def supports(
        cls,
        manufacturer_data: dict[int, bytes],
        service_data: dict[BluetoothUUID, bytes],
        local_name: str | None,
    ) -> bool:
        """Check if this interpreter handles the advertisement.

        Called by registry for fast routing. Should be a quick check
        based on company_id, service_uuid, or local_name pattern.
        """

    @abstractmethod
    def interpret(
        self,
        manufacturer_data: dict[int, bytes],
        service_data: dict[BluetoothUUID, bytes],
        local_name: str | None,
        rssi: int,
    ) -> T:
        """Interpret advertisement data and return typed result.

        Args:
            manufacturer_data: Company ID → payload bytes mapping
            service_data: Service UUID → payload bytes mapping
            local_name: Device local name (may contain protocol info)
            rssi: Signal strength in dBm

        Returns:
            Typed result specific to this interpreter (e.g., SensorData)

        """

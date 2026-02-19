"""High-level peripheral (GATT server) abstraction.

Provides :class:`PeripheralDevice`, the server-side counterpart to
:class:`Device`. Where ``Device`` connects TO remote peripherals and reads
GATT data, ``PeripheralDevice`` **hosts** GATT services and encodes values
for remote centrals to read.

Composes :class:`PeripheralManagerProtocol` with ``BaseCharacteristic``
instances that handle value encoding via ``build_value()``.
"""

from __future__ import annotations

import logging

# Any is required: BaseCharacteristic is generic over its value type (T), but
# PeripheralDevice hosts heterogeneous characteristics with different T types
# in a single dict, so the container must erase the type parameter to Any.
from typing import Any

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.types.gatt_enums import GattProperty
from bluetooth_sig.types.peripheral_types import CharacteristicDefinition, ServiceDefinition
from bluetooth_sig.types.uuid import BluetoothUUID

from .peripheral import PeripheralManagerProtocol

logger = logging.getLogger(__name__)


class HostedCharacteristic:
    """Tracks a hosted characteristic with its definition and class instance.

    Attributes:
        definition: The GATT characteristic definition registered on the peripheral.
        characteristic: The SIG characteristic class instance used for encoding/decoding.
        last_value: The last Python value that was encoded and set on this characteristic.

    """

    __slots__ = ("characteristic", "definition", "last_value")

    def __init__(
        self,
        definition: CharacteristicDefinition,
        characteristic: BaseCharacteristic[Any],
        initial_value: Any = None,  # noqa: ANN401
    ) -> None:
        """Initialise a hosted characteristic record.

        Args:
            definition: The GATT characteristic definition registered on the peripheral.
            characteristic: The SIG characteristic class instance for encoding/decoding.
            initial_value: Optional initial Python value set on this characteristic.

        """
        self.definition = definition
        self.characteristic = characteristic
        self.last_value: Any = initial_value  # noqa: ANN401


class PeripheralDevice:
    """High-level BLE peripheral abstraction using composition pattern.

    Coordinates between :class:`PeripheralManagerProtocol` (backend) and
    ``BaseCharacteristic`` instances (encoding) so callers work with typed
    Python values.

    Encoding is handled directly by the characteristic's ``build_value()``
    method — no translator is needed on the peripheral (server) side.

    The workflow mirrors :class:`Device` but for the server role:

    1. Create a ``PeripheralDevice`` wrapping a backend.
    2. Add services with :meth:`add_service` (typed helpers encode initial values).
    3. Start advertising with :meth:`start`.
    4. Update characteristic values with :meth:`update_value`.
    5. Stop with :meth:`stop`.

    Example::

        >>> from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
        >>> from bluetooth_sig.gatt.services import BatteryService
        >>>
        >>> peripheral = PeripheralDevice(backend)
        >>> battery_char = BatteryLevelCharacteristic()
        >>> peripheral.add_characteristic(
        ...     service_uuid=BatteryService.get_class_uuid(),
        ...     characteristic=battery_char,
        ...     initial_value=85,
        ... )
        >>> await peripheral.start()
        >>> await peripheral.update_value(battery_char, 72)

    """

    def __init__(
        self,
        peripheral_manager: PeripheralManagerProtocol,
    ) -> None:
        """Initialise PeripheralDevice.

        Args:
            peripheral_manager: Backend implementing PeripheralManagerProtocol.

        """
        self._manager = peripheral_manager

        # UUID (normalised upper-case) → HostedCharacteristic
        self._hosted: dict[str, HostedCharacteristic] = {}

        # Service UUID → ServiceDefinition (tracks services added via helpers)
        self._pending_services: dict[str, ServiceDefinition] = {}

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Advertised device name."""
        return self._manager.name

    @property
    def is_advertising(self) -> bool:
        """Whether the peripheral is currently advertising."""
        return self._manager.is_advertising

    @property
    def services(self) -> list[ServiceDefinition]:
        """Registered GATT services."""
        return self._manager.services

    @property
    def hosted_characteristics(self) -> dict[str, HostedCharacteristic]:
        """Map of UUID → HostedCharacteristic for all hosted characteristics."""
        return dict(self._hosted)

    # ------------------------------------------------------------------
    # Service & Characteristic Registration
    # ------------------------------------------------------------------

    def add_characteristic(
        self,
        service_uuid: str | BluetoothUUID,
        characteristic: BaseCharacteristic[Any],
        initial_value: Any,  # noqa: ANN401
        *,
        properties: GattProperty | None = None,
    ) -> CharacteristicDefinition:
        """Register a characteristic on a service, encoding the initial value.

        If the service has not been seen before, a new primary
        :class:`ServiceDefinition` is created automatically.

        Args:
            service_uuid: UUID of the parent service.
            characteristic: SIG characteristic class instance.
            initial_value: Python value to encode as the initial value.
            properties: GATT properties. Defaults to ``READ | NOTIFY``.

        Returns:
            The created :class:`CharacteristicDefinition`.

        Raises:
            RuntimeError: If the peripheral has already started advertising.

        """
        if self._manager.is_advertising:
            raise RuntimeError("Cannot add characteristics after peripheral has started")

        char_def = CharacteristicDefinition.from_characteristic(
            characteristic,
            initial_value,
            properties=properties,
        )

        svc_key = str(service_uuid).upper()
        if svc_key not in self._pending_services:
            self._pending_services[svc_key] = ServiceDefinition(
                uuid=BluetoothUUID(svc_key),
                characteristics=[],
            )
        self._pending_services[svc_key].characteristics.append(char_def)

        uuid_key = str(char_def.uuid).upper()
        self._hosted[uuid_key] = HostedCharacteristic(
            definition=char_def,
            characteristic=characteristic,
            initial_value=initial_value,
        )

        return char_def

    async def add_service(self, service: ServiceDefinition) -> None:
        """Register a pre-built service definition directly.

        For full control over the service definition. If you prefer typed
        helpers, use :meth:`add_characteristic` instead.

        Args:
            service: Complete service definition.

        Raises:
            RuntimeError: If the peripheral has already started advertising.

        """
        await self._manager.add_service(service)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Register pending services on the backend and start advertising.

        All services added via :meth:`add_characteristic` are flushed to the
        backend before ``start()`` is called on the manager.

        Raises:
            RuntimeError: If the peripheral has already started.

        """
        # Flush pending services to the backend
        for service_def in self._pending_services.values():
            await self._manager.add_service(service_def)
        self._pending_services.clear()

        await self._manager.start()

    async def stop(self) -> None:
        """Stop advertising and disconnect all clients."""
        await self._manager.stop()

    # ------------------------------------------------------------------
    # Value Updates
    # ------------------------------------------------------------------

    async def update_value(
        self,
        characteristic: BaseCharacteristic[Any] | str | BluetoothUUID,
        value: Any,  # noqa: ANN401
        *,
        notify: bool = True,
    ) -> None:
        """Encode a typed value and push it to the hosted characteristic.

        Args:
            characteristic: The characteristic instance, UUID string, or BluetoothUUID.
            value: Python value to encode via ``build_value()``.
            notify: Whether to notify subscribed centrals. Default ``True``.

        Raises:
            KeyError: If the characteristic is not hosted on this peripheral.
            RuntimeError: If the peripheral has not started.

        """
        uuid_key = self._resolve_uuid_key(characteristic)
        hosted = self._hosted.get(uuid_key)
        if hosted is None:
            raise KeyError(f"Characteristic {uuid_key} is not hosted on this peripheral")

        encoded = hosted.characteristic.build_value(value)
        hosted.last_value = value

        await self._manager.update_characteristic(uuid_key, encoded, notify=notify)

    async def update_raw(
        self,
        char_uuid: str | BluetoothUUID,
        raw_value: bytearray,
        *,
        notify: bool = True,
    ) -> None:
        """Push pre-encoded bytes to a hosted characteristic.

        Use this when you already have the encoded value or the
        characteristic does not have a SIG class registered.

        Args:
            char_uuid: UUID of the characteristic.
            raw_value: Pre-encoded bytes to set.
            notify: Whether to notify subscribed centrals.

        Raises:
            KeyError: If the characteristic UUID is not hosted.
            RuntimeError: If the peripheral has not started.

        """
        uuid_key = str(char_uuid).upper()
        await self._manager.update_characteristic(uuid_key, raw_value, notify=notify)

    async def get_current_value(
        self,
        characteristic: BaseCharacteristic[Any] | str | BluetoothUUID,
    ) -> Any:  # noqa: ANN401
        """Get the last Python value set for a hosted characteristic.

        Args:
            characteristic: The characteristic instance, UUID string, or BluetoothUUID.

        Returns:
            The last value passed to :meth:`update_value`, or the initial value.

        Raises:
            KeyError: If the characteristic is not hosted.

        """
        uuid_key = self._resolve_uuid_key(characteristic)
        hosted = self._hosted.get(uuid_key)
        if hosted is None:
            raise KeyError(f"Characteristic {uuid_key} is not hosted on this peripheral")
        return hosted.last_value

    # ------------------------------------------------------------------
    # Fluent Configuration Delegation
    # ------------------------------------------------------------------

    def with_manufacturer_data(self, company_id: int, payload: bytes) -> PeripheralDevice:
        """Configure manufacturer data for advertising.

        Args:
            company_id: Bluetooth SIG company identifier.
            payload: Manufacturer-specific payload bytes.

        Returns:
            Self for method chaining.

        """
        self._manager.with_manufacturer_id(company_id, payload)
        return self

    def with_tx_power(self, power_dbm: int) -> PeripheralDevice:
        """Set TX power level.

        Args:
            power_dbm: Transmission power in dBm.

        Returns:
            Self for method chaining.

        """
        self._manager.with_tx_power(power_dbm)
        return self

    def with_connectable(self, connectable: bool) -> PeripheralDevice:
        """Set whether the peripheral accepts connections.

        Args:
            connectable: True to accept connections.

        Returns:
            Self for method chaining.

        """
        self._manager.with_connectable(connectable)
        return self

    def with_discoverable(self, discoverable: bool) -> PeripheralDevice:
        """Set whether the peripheral is discoverable.

        Args:
            discoverable: True to be discoverable.

        Returns:
            Self for method chaining.

        """
        self._manager.with_discoverable(discoverable)
        return self

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _resolve_uuid_key(self, characteristic: BaseCharacteristic[Any] | str | BluetoothUUID) -> str:
        """Normalise a characteristic reference to an upper-case UUID string."""
        if isinstance(characteristic, BaseCharacteristic):
            return str(characteristic.uuid).upper()
        return str(characteristic).upper()

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        state = "advertising" if self.is_advertising else "stopped"
        return (
            f"PeripheralDevice(name={self.name!r}, "
            f"state={state}, "
            f"services={len(self.services)}, "
            f"characteristics={len(self._hosted)})"
        )


__all__ = [
    "HostedCharacteristic",
    "PeripheralDevice",
]

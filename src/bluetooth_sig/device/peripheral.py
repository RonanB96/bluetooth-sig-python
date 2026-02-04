"""Peripheral manager protocol for BLE GATT server adapters.

Defines an async abstract base class that peripheral adapter implementations
(bless, bluez_peripheral, etc.) must inherit from to create BLE GATT servers
that broadcast services and characteristics.

This is the server-side counterpart to ClientManagerProtocol. Where clients
connect TO devices and READ/PARSE data, peripherals ARE devices that ENCODE
and BROADCAST data for others to read.

Adapters must provide async implementations of all abstract methods below.

TODO: Create PeripheralDevice class (analogous to Device) that provides:
    - High-level abstraction over PeripheralManagerProtocol
    - SIG translator integration for encoding values
    - Hosted service state management (like DeviceConnected for clients)
    - See device.py for the client-side pattern to follow
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import ClassVar

from typing_extensions import Self

from bluetooth_sig.types.company import CompanyIdentifier, ManufacturerData
from bluetooth_sig.types.peripheral_types import CharacteristicDefinition, ServiceDefinition
from bluetooth_sig.types.uuid import BluetoothUUID


class PeripheralManagerProtocol(ABC):
    """Abstract base class for BLE peripheral/GATT server implementations.

    This protocol defines the interface for creating BLE peripherals that
    broadcast services and characteristics. Implementations wrap backend
    libraries like bless, bluez_peripheral, etc.

    Uses a fluent builder pattern for advertisement configuration - call
    configuration methods before start() to customise advertising.

    The workflow is:
    1. Create peripheral manager with a device name
    2. Configure advertising (optional): with_manufacturer_data(), with_tx_power(), etc.
    3. Add services and characteristics (using CharacteristicDefinition)
    4. Start advertising
    5. Update characteristic values as needed
    6. Stop when done

    Example::
        >>> from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
        >>> from bluetooth_sig.gatt.services import BatteryService
        >>> from bluetooth_sig.types.company import ManufacturerData
        >>>
        >>> # Create peripheral with fluent configuration
        >>> peripheral = SomePeripheralManager("My Sensor")
        >>> peripheral.with_tx_power(-10).with_connectable(True)
        >>>
        >>> # Define a service with battery level
        >>> char = BatteryLevelCharacteristic()
        >>> char_def = CharacteristicDefinition.from_characteristic(char, 85)
        >>>
        >>> service = ServiceDefinition(
        ...     uuid=BatteryService.get_class_uuid(),
        ...     characteristics=[char_def],
        ... )
        >>>
        >>> await peripheral.add_service(service)
        >>> await peripheral.start()
        >>>
        >>> # Later, update the battery level
        >>> await peripheral.update_characteristic("2A19", char.build_value(75))

    """

    # Class-level flag indicating backend capabilities
    supports_advertising: ClassVar[bool] = True

    def __init__(self, name: str) -> None:
        """Initialize the peripheral manager.

        Args:
            name: The advertised device name visible to scanners

        """
        self._name = name

        # Service and characteristic tracking
        self._services: list[ServiceDefinition] = []
        self._char_definitions: dict[str, CharacteristicDefinition] = {}

        # Advertisement configuration (set via fluent methods)
        self._manufacturer_data: ManufacturerData | None = None
        self._service_data: dict[BluetoothUUID, bytes] = {}
        self._tx_power: int | None = None
        self._is_connectable = True
        self._is_discoverable = True

        # Callbacks for read/write handling
        self._read_callbacks: dict[str, Callable[[], bytearray]] = {}
        self._write_callbacks: dict[str, Callable[[bytearray], None]] = {}

    @property
    def name(self) -> str:
        """Get the advertised device name.

        Returns:
            The device name as it appears to BLE scanners

        """
        return self._name

    @property
    def services(self) -> list[ServiceDefinition]:
        """Get the list of registered services.

        Returns:
            List of ServiceDefinition objects added to this peripheral.

        """
        return self._services

    @property
    def manufacturer_data(self) -> ManufacturerData | None:
        """Get the configured manufacturer data.

        Returns:
            ManufacturerData if configured, None otherwise.

        """
        return self._manufacturer_data

    @property
    def service_data(self) -> dict[BluetoothUUID, bytes]:
        """Get the configured service data.

        Returns:
            Dictionary mapping service UUIDs to data bytes.

        """
        return self._service_data

    @property
    def tx_power(self) -> int | None:
        """Get the configured TX power level.

        Returns:
            TX power in dBm if configured, None otherwise.

        """
        return self._tx_power

    @property
    def is_connectable_config(self) -> bool:
        """Get the connectable configuration.

        Returns:
            True if peripheral is configured to accept connections.

        """
        return self._is_connectable

    @property
    def is_discoverable_config(self) -> bool:
        """Get the discoverable configuration.

        Returns:
            True if peripheral is configured to be discoverable.

        """
        return self._is_discoverable

    def with_manufacturer_data(self, manufacturer_data: ManufacturerData) -> Self:
        r"""Set manufacturer-specific advertising data.

        Args:
            manufacturer_data: ManufacturerData instance from the types module.

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If called after start().

        Example::
            >>> from bluetooth_sig.types.company import ManufacturerData
            >>> mfr = ManufacturerData.from_id_and_payload(0x004C, b"\x02\x15...")
            >>> peripheral.with_manufacturer_data(mfr)

        """
        if self.is_advertising:
            raise RuntimeError("Cannot configure after peripheral has started")
        self._manufacturer_data = manufacturer_data
        return self

    def with_manufacturer_id(
        self,
        company_id: int | CompanyIdentifier,
        payload: bytes,
    ) -> Self:
        r"""Set manufacturer data from company ID and payload.

        Args:
            company_id: Bluetooth SIG company identifier (e.g., 0x004C for Apple)
                        or CompanyIdentifier instance.
            payload: Manufacturer-specific payload bytes.

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If called after start().

        Example::
            >>> peripheral.with_manufacturer_id(0x004C, b"\x02\x15...")

        """
        if self.is_advertising:
            raise RuntimeError("Cannot configure after peripheral has started")
        cid = company_id if isinstance(company_id, int) else company_id.id
        self._manufacturer_data = ManufacturerData.from_id_and_payload(cid, payload)
        return self

    def with_service_data(
        self,
        service_uuid: BluetoothUUID,
        data: bytes,
    ) -> Self:
        r"""Add service data to advertisement.

        Args:
            service_uuid: BluetoothUUID of the service.
            data: Service-specific data bytes.

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If called after start().

        Example::
            >>> from bluetooth_sig.gatt.services import BatteryService
            >>> peripheral.with_service_data(
            ...     BatteryService.get_class_uuid(),
            ...     b"\x50",  # 80% battery
            ... )

        """
        if self.is_advertising:
            raise RuntimeError("Cannot configure after peripheral has started")
        self._service_data[service_uuid] = data
        return self

    def with_tx_power(self, power_dbm: int) -> Self:
        """Set TX power level for advertising.

        Args:
            power_dbm: Transmission power in dBm (-127 to +127).

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If called after start().

        """
        if self.is_advertising:
            raise RuntimeError("Cannot configure after peripheral has started")
        self._tx_power = power_dbm
        return self

    def with_connectable(self, connectable: bool) -> Self:
        """Set whether the peripheral accepts connections.

        Args:
            connectable: True to accept connections (default), False for broadcast only.

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If called after start().

        """
        if self.is_advertising:
            raise RuntimeError("Cannot configure after peripheral has started")
        self._is_connectable = connectable
        return self

    def with_discoverable(self, discoverable: bool) -> Self:
        """Set whether the peripheral is discoverable.

        Args:
            discoverable: True to be discoverable (default), False otherwise.

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If called after start().

        """
        if self.is_advertising:
            raise RuntimeError("Cannot configure after peripheral has started")
        self._is_discoverable = discoverable
        return self

    # -------------------------------------------------------------------------
    # Service Management (Generic Implementation)
    # -------------------------------------------------------------------------

    async def add_service(self, service: ServiceDefinition) -> None:
        """Add a GATT service to the peripheral.

        Services must be added before calling start(). Each service contains
        one or more characteristics that clients can interact with.

        Args:
            service: The service definition to add

        Raises:
            RuntimeError: If called after start()

        """
        if self.is_advertising:
            raise RuntimeError("Cannot add services after peripheral has started")

        self._services.append(service)

        # Track characteristic definitions for later lookup
        for char_def in service.characteristics:
            uuid_upper = str(char_def.uuid).upper()
            self._char_definitions[uuid_upper] = char_def

            # Register any callbacks from the definition
            if char_def.on_read:
                self._read_callbacks[uuid_upper] = char_def.on_read
            if char_def.on_write:
                self._write_callbacks[uuid_upper] = char_def.on_write

    def get_characteristic_definition(
        self,
        char_uuid: str | BluetoothUUID,
    ) -> CharacteristicDefinition | None:
        """Get the characteristic definition by UUID.

        Args:
            char_uuid: UUID of the characteristic.

        Returns:
            CharacteristicDefinition if found, None otherwise.

        """
        uuid_upper = str(char_uuid).upper()
        return self._char_definitions.get(uuid_upper)

    def set_read_callback(
        self,
        char_uuid: str | BluetoothUUID,
        callback: Callable[[], bytearray],
    ) -> None:
        """Set a callback for dynamic read value generation.

        When a client reads the characteristic, this callback will be invoked
        to generate the current value instead of returning the stored value.

        Args:
            char_uuid: UUID of the characteristic
            callback: Function that returns the encoded value to serve

        Raises:
            KeyError: If characteristic UUID not found

        """
        uuid_str = str(char_uuid).upper()
        if uuid_str not in self._char_definitions:
            raise KeyError(f"Characteristic {uuid_str} not found")
        self._read_callbacks[uuid_str] = callback

    def set_write_callback(
        self,
        char_uuid: str | BluetoothUUID,
        callback: Callable[[bytearray], None],
    ) -> None:
        """Set a callback for handling client writes.

        When a client writes to the characteristic, this callback will be
        invoked with the written data.

        Args:
            char_uuid: UUID of the characteristic
            callback: Function called with the written data

        Raises:
            KeyError: If characteristic UUID not found

        """
        uuid_str = str(char_uuid).upper()
        if uuid_str not in self._char_definitions:
            raise KeyError(f"Characteristic {uuid_str} not found")
        self._write_callbacks[uuid_str] = callback

    # -------------------------------------------------------------------------
    # Abstract Methods (Backend-Specific Implementation Required)
    # -------------------------------------------------------------------------

    @abstractmethod
    async def start(self) -> None:
        """Start advertising and accepting connections.

        Backend implementations must:
        1. Create the platform-specific GATT server
        2. Register all services and characteristics from self._services
        3. Configure advertisement data from self._manufacturer_data, etc.
        4. Begin advertising

        Raises:
            RuntimeError: If no services have been added

        """

    @abstractmethod
    async def stop(self) -> None:
        """Stop advertising and disconnect all clients."""

    @property
    @abstractmethod
    def is_advertising(self) -> bool:
        """Check if the peripheral is currently advertising.

        Returns:
            True if advertising, False otherwise

        """

    @abstractmethod
    async def update_characteristic(
        self,
        char_uuid: str | BluetoothUUID,
        value: bytearray,
        *,
        notify: bool = True,
    ) -> None:
        """Update a characteristic's value.

        This sets the new value that will be returned when clients read the
        characteristic. If notify=True and the characteristic supports
        notifications, subscribed clients will be notified of the change.

        Args:
            char_uuid: UUID of the characteristic to update
            value: New encoded value (use characteristic.build_value() to encode)
            notify: If True, notify subscribed clients of the change

        Raises:
            KeyError: If characteristic UUID not found
            RuntimeError: If peripheral not started

        """

    @abstractmethod
    async def get_characteristic_value(self, char_uuid: str | BluetoothUUID) -> bytearray:
        """Get the current value of a characteristic.

        Args:
            char_uuid: UUID of the characteristic

        Returns:
            The current encoded value

        Raises:
            KeyError: If characteristic UUID not found

        """

    @property
    def connected_clients(self) -> int:
        """Get the number of currently connected clients.

        Returns:
            Number of connected BLE centrals

        Raises:
            NotImplementedError: If backend doesn't track connections

        """
        raise NotImplementedError(f"{self.__class__.__name__} does not track connected clients")


__all__ = [
    "CharacteristicDefinition",
    "PeripheralManagerProtocol",
    "ServiceDefinition",
]

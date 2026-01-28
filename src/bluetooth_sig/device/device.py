"""Device class for grouping BLE device services, characteristics, encryption, and advertiser data.

This module provides a high-level Device abstraction that groups all
services, characteristics, encryption requirements, and advertiser data
for a BLE device. It integrates with the BluetoothSIGTranslator for
parsing while providing a unified view of device state.
"""
# pylint: disable=too-many-lines  # Device abstraction is a cohesive module with related classes
# TODO split into multiple files

from __future__ import annotations

import logging
from abc import abstractmethod
from enum import Enum
from typing import Any, Callable, Protocol, TypeVar, cast, overload

from ..advertising.registry import PayloadInterpreterRegistry
from ..gatt.characteristics import CharacteristicName
from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.characteristics.registry import CharacteristicRegistry
from ..gatt.characteristics.unknown import UnknownCharacteristic
from ..gatt.context import CharacteristicContext, DeviceInfo
from ..gatt.descriptors.base import BaseDescriptor
from ..gatt.descriptors.registry import DescriptorRegistry
from ..gatt.services import ServiceName
from ..types import (
    AdvertisementData,
    CharacteristicInfo,
    DescriptorData,
    DescriptorInfo,
)
from ..types.device_types import ScannedDevice
from ..types.uuid import BluetoothUUID
from .advertising import DeviceAdvertising
from .connected import DeviceConnected, DeviceEncryption, DeviceService
from .connection import ConnectionManagerProtocol

# Type variable for generic characteristic return types
T = TypeVar("T")

__all__ = [
    "DependencyResolutionMode",
    "Device",
    "DeviceAdvertising",
    "DeviceConnected",
    "SIGTranslatorProtocol",
]


class DependencyResolutionMode(Enum):
    """Mode for automatic dependency resolution during characteristic reads.

    Attributes:
        NORMAL: Auto-resolve dependencies, use cache when available
        SKIP_DEPENDENCIES: Skip dependency resolution and validation
        FORCE_REFRESH: Re-read dependencies from device, ignoring cache
    """

    NORMAL = "normal"
    SKIP_DEPENDENCIES = "skip_dependencies"
    FORCE_REFRESH = "force_refresh"


class SIGTranslatorProtocol(Protocol):  # pylint: disable=too-few-public-methods
    """Protocol for SIG translator interface."""

    @abstractmethod
    def parse_characteristics(
        self,
        char_data: dict[str, bytes],
        ctx: CharacteristicContext | None = None,
    ) -> dict[str, Any]:
        """Parse multiple characteristics at once."""

    @abstractmethod
    def parse_characteristic(
        self,
        uuid: str,
        raw_data: bytes,
        ctx: CharacteristicContext | None = None,
    ) -> Any:  # noqa: ANN401  # Runtime UUID dispatch cannot be type-safe
        """Parse a single characteristic's raw bytes."""

    @abstractmethod
    def get_characteristic_uuid_by_name(self, name: CharacteristicName) -> BluetoothUUID | None:
        """Get the UUID for a characteristic name enum (enum-only API)."""

    @abstractmethod
    def get_service_uuid_by_name(self, name: str | ServiceName) -> BluetoothUUID | None:
        """Get the UUID for a service name or enum."""

    def get_characteristic_info_by_name(self, name: CharacteristicName) -> Any | None:  # noqa: ANN401  # Adapter-specific characteristic info
        """Get characteristic info by enum name (optional method)."""


class Device:  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    r"""High-level BLE device abstraction using composition pattern.

    This class coordinates between connected GATT operations and advertising
    packet interpretation through two subsystems:
    - `device.connected` - GATT connection, services, characteristics
    - `device.advertising` - Vendor-specific advertising interpretation

    Key features:
    - Parse advertising data via `device.advertising` subsystem
    - Manage GATT connections via `device.connected` subsystem
    - Convenience methods delegate to appropriate subsystem
    - Integrates with [BluetoothSIGTranslator][bluetooth_sig.BluetoothSIGTranslator]

    Attributes:
        advertising: DeviceAdvertising subsystem for vendor-specific interpretation
        connected: DeviceConnected subsystem for GATT operations
        translator: SIG translator for parsing characteristics

    Example:
        Create and use device with composition::

            from bluetooth_sig import BluetoothSIGTranslator
            from bluetooth_sig.device import Device

            translator = BluetoothSIGTranslator()
            device = Device(connection_manager, translator)

            # Use connected subsystem for GATT operations
            await device.connected.connect()
            await device.connected.discover_services()
            battery = await device.connected.read("2A19")

            # Use advertising subsystem for packet interpretation
            device.advertising.set_bindkey(b"\\x01\\x02...")
            result = device.advertising.process(advertising_data)

            # Convenience methods delegate to subsystems
            await device.connect()  # → device.connected.connect()
            await device.read("battery_level")  # → device.connected.read()

    """

    def __init__(self, connection_manager: ConnectionManagerProtocol, translator: SIGTranslatorProtocol) -> None:
        """Initialise Device instance with connection manager and translator.

        Args:
            connection_manager: Connection manager implementing ConnectionManagerProtocol
            translator: SIGTranslatorProtocol instance

        """
        self.connection_manager = connection_manager
        self.translator = translator
        self._name: str = ""

        # Connected subsystem (composition pattern)
        self.connected = DeviceConnected(
            mac_address=self.address,
            connection_manager=connection_manager,
        )

        # Advertising subsystem (composition pattern)
        self.advertising = DeviceAdvertising(self.address, connection_manager)
        # Set up registry for auto-detection
        self.advertising.set_registry(PayloadInterpreterRegistry())

        # Cache for device_info property and last advertisement
        self._device_info_cache: DeviceInfo | None = None
        self._last_advertisement: AdvertisementData | None = None

    def __str__(self) -> str:
        """Return string representation of Device.

        Returns:
            str: String representation of Device.

        """
        service_count = len(self.connected.services)
        char_count = sum(len(service.characteristics) for service in self.connected.services.values())
        return f"Device({self.address}, name={self.name}, {service_count} services, {char_count} characteristics)"

    @property
    def services(self) -> dict[str, DeviceService]:
        """GATT services discovered on device.

        Delegates to device.connected.services.

        Returns:
            Dictionary of service UUID → DeviceService

        """
        return self.connected.services

    @property
    def encryption(self) -> DeviceEncryption:
        """Encryption state for connected device.

        Delegates to device.connected.encryption.

        Returns:
            DeviceEncryption instance

        """
        return self.connected.encryption

    @property
    def address(self) -> str:
        """Get the device address from the connection manager.

        Returns:
            BLE device address

        """
        return self.connection_manager.address

    @staticmethod
    async def scan(manager_class: type[ConnectionManagerProtocol], timeout: float = 5.0) -> list[ScannedDevice]:
        """Scan for nearby BLE devices using a specific connection manager.

        This is a static method that doesn't require a Device instance.
        Use it to discover devices before creating Device instances.

        Args:
            manager_class: The connection manager class to use for scanning
                          (e.g., BleakRetryConnectionManager)
            timeout: Scan duration in seconds (default: 5.0)

        Returns:
            List of discovered devices

        Raises:
            NotImplementedError: If the connection manager doesn't support scanning

        Example::

            from bluetooth_sig.device import Device
            from connection_managers.bleak_retry import BleakRetryConnectionManager

            # Scan for devices
            devices = await Device.scan(BleakRetryConnectionManager, timeout=10.0)

            # Create Device instance for first discovered device
            if devices:
                translator = BluetoothSIGTranslator()
                device = Device(devices[0].address, translator)

        """
        return await manager_class.scan(timeout)

    async def connect(self) -> None:
        """Connect to the BLE device.

        Convenience method that delegates to device.connected.connect().

        Raises:
            RuntimeError: If no connection manager is attached

        """
        await self.connected.connect()

    async def disconnect(self) -> None:
        """Disconnect from the BLE device.

        Convenience method that delegates to device.connected.disconnect().

        Raises:
            RuntimeError: If no connection manager is attached

        """
        await self.connected.disconnect()

    def _get_cached_characteristic(self, char_uuid: BluetoothUUID) -> BaseCharacteristic[Any] | None:
        """Get cached characteristic instance from services.

        Delegates to device.connected.get_cached_characteristic().

        Args:
            char_uuid: UUID of the characteristic to find

        Returns: BaseCharacteristic[Any] instance if found, None otherwise

        """
        return self.connected.get_cached_characteristic(char_uuid)

    def _cache_characteristic(self, char_uuid: BluetoothUUID, char_instance: BaseCharacteristic[Any]) -> None:
        """Store characteristic instance in services cache.

        Delegates to device.connected.cache_characteristic().

        Args:
            char_uuid: UUID of the characteristic
            char_instance: BaseCharacteristic[Any] instance to cache

        """
        self.connected.cache_characteristic(char_uuid, char_instance)

    def _create_unknown_characteristic(self, dep_uuid: BluetoothUUID) -> BaseCharacteristic[Any]:
        """Create an unknown characteristic instance for a UUID not in registry.

        Args:
            dep_uuid: UUID of the unknown characteristic

        Returns:
            UnknownCharacteristic instance

        """
        dep_uuid_str = str(dep_uuid)
        char_info = CharacteristicInfo(uuid=dep_uuid, name=f"Unknown-{dep_uuid_str}")
        return UnknownCharacteristic(info=char_info)

    async def _resolve_single_dependency(
        self,
        dep_uuid: BluetoothUUID,
        is_required: bool,
        dep_class: type[BaseCharacteristic[Any]],
    ) -> Any | None:  # noqa: ANN401  # Dependency can be any characteristic type
        """Resolve a single dependency by reading and parsing it.

        Args:
            dep_uuid: UUID of the dependency characteristic
            is_required: Whether this is a required dependency
            dep_class: The dependency characteristic class

        Returns:
            Parsed characteristic data, or None if optional and failed

        Raises:
            ValueError: If required dependency fails to read

        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached")

        dep_uuid_str = str(dep_uuid)

        try:
            raw_data = await self.connection_manager.read_gatt_char(dep_uuid)

            # Get or create characteristic instance
            char_instance = self._get_cached_characteristic(dep_uuid)
            if char_instance is None:
                # Create a new characteristic instance using registry
                char_class_or_none = CharacteristicRegistry.get_characteristic_class_by_uuid(dep_uuid)
                if char_class_or_none:
                    char_instance = char_class_or_none()
                else:
                    char_instance = self._create_unknown_characteristic(dep_uuid)

                # Cache the instance
                self._cache_characteristic(dep_uuid, char_instance)

            # Parse using the characteristic instance
            return char_instance.parse_value(raw_data)

        except Exception as e:  # pylint: disable=broad-exception-caught
            if is_required:
                raise ValueError(
                    f"Failed to read required dependency {dep_class.__name__} ({dep_uuid_str}): {e}"
                ) from e
            # Optional dependency failed, log and continue
            logging.warning("Failed to read optional dependency %s: %s", dep_class.__name__, e)
            return None

    async def _ensure_dependencies_resolved(
        self,
        char_class: type[BaseCharacteristic[Any]],
        resolution_mode: DependencyResolutionMode,
    ) -> CharacteristicContext:
        """Ensure all dependencies for a characteristic are resolved.

        This method automatically reads feature characteristics needed for validation
        of measurement characteristics. Feature characteristics are cached after first read.

        Args:
            char_class: The characteristic class to resolve dependencies for
            resolution_mode: How to handle dependency resolution

        Returns:
            CharacteristicContext with resolved dependencies

        Raises:
            RuntimeError: If no connection manager is attached

        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        # Get dependency declarations from characteristic class
        optional_deps = getattr(char_class, "_optional_dependencies", [])
        required_deps = getattr(char_class, "_required_dependencies", [])

        # Build context with resolved dependencies
        context_chars: dict[str, Any] = {}

        for dep_class in required_deps + optional_deps:
            is_required = dep_class in required_deps

            # Get UUID for dependency characteristic
            dep_uuid = dep_class.get_class_uuid()
            if not dep_uuid:
                if is_required:
                    raise ValueError(f"Required dependency {dep_class.__name__} has no UUID")
                continue

            dep_uuid_str = str(dep_uuid)

            # Check resolution mode
            if resolution_mode == DependencyResolutionMode.SKIP_DEPENDENCIES:
                continue  # Skip all dependency resolution

            # Check cache (unless force refresh)
            if resolution_mode != DependencyResolutionMode.FORCE_REFRESH:
                cached_char = self._get_cached_characteristic(dep_uuid)
                if cached_char is not None and cached_char.last_parsed is not None:
                    # Use the last_parsed data from the cached characteristic
                    context_chars[dep_uuid_str] = cached_char.last_parsed
                    continue

            # Read and parse dependency from device
            parsed_data = await self._resolve_single_dependency(dep_uuid, is_required, dep_class)
            if parsed_data is not None:
                context_chars[dep_uuid_str] = parsed_data

        # Create context with device info and resolved dependencies
        device_info = DeviceInfo(
            address=self.address,
            name=self.name,
            manufacturer_data=self._last_advertisement.ad_structures.core.manufacturer_data
            if self._last_advertisement
            else {},
            service_uuids=self._last_advertisement.ad_structures.core.service_uuids if self._last_advertisement else [],
        )

        return CharacteristicContext(
            device_info=device_info,
            other_characteristics=context_chars,
        )

    @overload
    async def read(
        self,
        char: type[BaseCharacteristic[T]],
        resolution_mode: DependencyResolutionMode = ...,
    ) -> T | None: ...

    @overload
    async def read(
        self,
        char: str | CharacteristicName,
        resolution_mode: DependencyResolutionMode = ...,
    ) -> Any | None: ...  # noqa: ANN401  # Runtime UUID dispatch cannot be type-safe

    async def read(
        self,
        char: str | CharacteristicName | type[BaseCharacteristic[T]],
        resolution_mode: DependencyResolutionMode = DependencyResolutionMode.NORMAL,
    ) -> T | Any | None:  # Runtime UUID dispatch cannot be type-safe
        """Read a characteristic value from the device.

        Args:
            char: Name, enum, or characteristic class to read.
                       Passing the class enables type-safe return values.
            resolution_mode: How to handle automatic dependency resolution:
                - NORMAL: Auto-resolve dependencies, use cache when available (default)
                - SKIP_DEPENDENCIES: Skip dependency resolution and validation
                - FORCE_REFRESH: Re-read dependencies from device, ignoring cache

        Returns:
            Parsed characteristic value or None if read fails.
            Return type is inferred from characteristic class when provided.

        Raises:
            RuntimeError: If no connection manager is attached
            ValueError: If required dependencies cannot be resolved

        Example::

            # Type-safe: pass characteristic class, return type is inferred
            from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

            level: int | None = await device.read(BatteryLevelCharacteristic)

            # Not type-safe: pass string/enum, returns Any
            level = await device.read(CharacteristicName.BATTERY_LEVEL)
            level = await device.read("2A19")

        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        # Handle characteristic class input (type-safe path)
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            char_class: type[BaseCharacteristic[Any]] = char
            char_instance = char_class()
            resolved_uuid = char_instance.uuid

            ctx: CharacteristicContext | None = None
            if resolution_mode != DependencyResolutionMode.SKIP_DEPENDENCIES:
                ctx = await self._ensure_dependencies_resolved(char_class, resolution_mode)

            raw = await self.connection_manager.read_gatt_char(resolved_uuid)
            return char_instance.parse_value(raw, ctx=ctx)

        # Handle string/enum input (not type-safe path)
        resolved_uuid = self._resolve_characteristic_name(char)

        char_class_lookup = CharacteristicRegistry.get_characteristic_class_by_uuid(resolved_uuid)

        # Resolve dependencies if characteristic class is known
        ctx = None
        if char_class_lookup and resolution_mode != DependencyResolutionMode.SKIP_DEPENDENCIES:
            ctx = await self._ensure_dependencies_resolved(char_class_lookup, resolution_mode)

        # Read the characteristic
        raw = await self.connection_manager.read_gatt_char(resolved_uuid)
        return self.translator.parse_characteristic(str(resolved_uuid), raw, ctx=ctx)

    @overload
    async def write(
        self,
        char: type[BaseCharacteristic[T]],
        data: T,
        response: bool = ...,
    ) -> None: ...

    @overload
    async def write(
        self,
        char: str | CharacteristicName,
        data: bytes,
        response: bool = ...,
    ) -> None: ...

    async def write(
        self,
        char: str | CharacteristicName | type[BaseCharacteristic[T]],
        data: bytes | T,
        response: bool = True,
    ) -> None:
        r"""Write data to a characteristic on the device.

        Args:
            char: Name, enum, or characteristic class to write to.
                       Passing the class enables type-safe value encoding.
            data: Raw bytes (for string/enum) or typed value (for characteristic class).
                  When using characteristic class, the value is encoded using build_value().
            response: If True, use write-with-response (wait for acknowledgment).
                     If False, use write-without-response (faster but no confirmation).
                     Default is True for reliability.

        Raises:
            RuntimeError: If no connection manager is attached
            CharacteristicEncodeError: If encoding fails (when using characteristic class)

        Example::

            # Type-safe: pass characteristic class and typed value
            from bluetooth_sig.gatt.characteristics import AlertLevelCharacteristic

            await device.write(AlertLevelCharacteristic, AlertLevel.HIGH)

            # Not type-safe: pass raw bytes
            await device.write("2A06", b"\x02")
            await device.write(CharacteristicName.ALERT_LEVEL, b"\x02")

        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        # Handle characteristic class input (type-safe path)
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            char_instance = char()
            resolved_uuid = char_instance.uuid
            # data is typed value T, encode it
            encoded = char_instance.build_value(data)  # type: ignore[arg-type]
            await self.connection_manager.write_gatt_char(resolved_uuid, bytes(encoded), response=response)
            return

        # Handle string/enum input (not type-safe path)
        # data must be bytes in this path
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f"When using string/enum char_name, data must be bytes, got {type(data).__name__}")

        resolved_uuid = self._resolve_characteristic_name(char)
        # cast is safe: isinstance check above ensures data is bytes/bytearray
        await self.connection_manager.write_gatt_char(resolved_uuid, cast("bytes", data), response=response)

    @overload
    async def start_notify(
        self,
        char: type[BaseCharacteristic[T]],
        callback: Callable[[T], None],
    ) -> None: ...

    @overload
    async def start_notify(
        self,
        char: str | CharacteristicName,
        callback: Callable[[Any], None],
    ) -> None: ...

    async def start_notify(
        self,
        char: str | CharacteristicName | type[BaseCharacteristic[T]],
        callback: Callable[[T], None] | Callable[[Any], None],
    ) -> None:
        """Start notifications for a characteristic.

        Args:
            char: Name, enum, or characteristic class to monitor.
                  Passing the class enables type-safe callbacks.
            callback: Function to call when notifications are received.
                      Callback parameter type is inferred from characteristic class.

        Raises:
            RuntimeError: If no connection manager is attached

        Example::

            # Type-safe: callback receives typed value
            from bluetooth_sig.gatt.characteristics import HeartRateMeasurementCharacteristic


            def on_heart_rate(value: HeartRateMeasurementData) -> None:
                print(f"Heart rate: {value.heart_rate}")


            await device.start_notify(HeartRateMeasurementCharacteristic, on_heart_rate)

            # Not type-safe: callback receives Any
            await device.start_notify("2A37", lambda v: print(v))

        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        # Handle characteristic class input (type-safe path)
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            char_instance = char()
            resolved_uuid = char_instance.uuid

            def _typed_cb(sender: str, data: bytes) -> None:
                del sender  # Required by callback interface
                parsed = char_instance.parse_value(data)
                try:
                    callback(parsed)
                except Exception:  # pylint: disable=broad-exception-caught
                    logging.exception("Notification callback raised an exception")

            await self.connection_manager.start_notify(resolved_uuid, _typed_cb)
            return

        # Handle string/enum input (not type-safe path)
        resolved_uuid = self._resolve_characteristic_name(char)

        def _internal_cb(sender: str, data: bytes) -> None:
            parsed = self.translator.parse_characteristic(sender, data)
            try:
                callback(parsed)
            except Exception:  # pylint: disable=broad-exception-caught
                logging.exception("Notification callback raised an exception")

        await self.connection_manager.start_notify(resolved_uuid, _internal_cb)

    def _resolve_characteristic_name(self, identifier: str | CharacteristicName) -> BluetoothUUID:
        """Resolve a characteristic name or enum to its UUID.

        Args:
            identifier: Characteristic name string or enum

        Returns:
            Characteristic UUID string

        Raises:
            ValueError: If the characteristic name cannot be resolved

        """
        if isinstance(identifier, CharacteristicName):
            # For enum inputs, ask the translator for the UUID
            uuid = self.translator.get_characteristic_uuid_by_name(identifier)
            if uuid:
                return uuid
            norm = identifier.value.strip()
        else:
            norm = identifier
        stripped = norm.replace("-", "")
        if len(stripped) in (4, 8, 32) and all(c in "0123456789abcdefABCDEF" for c in stripped):
            return BluetoothUUID(norm)

        raise ValueError(f"Unknown characteristic name: '{identifier}'")

    async def stop_notify(self, char_name: str | CharacteristicName) -> None:
        """Stop notifications for a characteristic.

        Args:
            char_name: Characteristic name or UUID

        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached")

        resolved_uuid = self._resolve_characteristic_name(char_name)
        await self.connection_manager.stop_notify(resolved_uuid)

    async def read_descriptor(self, desc_uuid: BluetoothUUID | BaseDescriptor) -> DescriptorData:
        """Read a descriptor value from the device.

        Args:
            desc_uuid: UUID of the descriptor to read or BaseDescriptor instance

        Returns:
            Parsed descriptor data with metadata

        Raises:
            RuntimeError: If no connection manager is attached

        """
        # Extract UUID from BaseDescriptor if needed
        uuid = desc_uuid.uuid if isinstance(desc_uuid, BaseDescriptor) else desc_uuid

        raw_data = await self.connected.read_descriptor(uuid)

        # Try to create a descriptor instance and parse the data
        descriptor = DescriptorRegistry.create_descriptor(str(uuid))
        if descriptor:
            return descriptor.parse_value(raw_data)

        # If no registered descriptor found, return unparsed DescriptorData
        return DescriptorData(
            info=DescriptorInfo(uuid=uuid, name="Unknown Descriptor"),
            value=raw_data,
            raw_data=raw_data,
            parse_success=False,
            error_message="Unknown descriptor UUID - no parser available",
        )

    async def write_descriptor(self, desc_uuid: BluetoothUUID | BaseDescriptor, data: bytes | DescriptorData) -> None:
        """Write data to a descriptor on the device.

        Args:
            desc_uuid: UUID of the descriptor to write to or BaseDescriptor instance
            data: Either raw bytes to write, or a DescriptorData object.
                 If DescriptorData is provided, its raw_data will be written.

        Raises:
            RuntimeError: If no connection manager is attached

        """
        # Extract UUID from BaseDescriptor if needed
        uuid = desc_uuid.uuid if isinstance(desc_uuid, BaseDescriptor) else desc_uuid

        # Extract raw bytes from DescriptorData if needed
        raw_data: bytes
        raw_data = data.raw_data if isinstance(data, DescriptorData) else data

        await self.connected.write_descriptor(uuid, raw_data)

    async def pair(self) -> None:
        """Pair with the device.

        Convenience method that delegates to device.connected.pair().

        Raises:
            RuntimeError: If no connection manager is attached

        """
        await self.connected.pair()

    async def unpair(self) -> None:
        """Unpair from the device.

        Convenience method that delegates to device.connected.unpair().

        Raises:
            RuntimeError: If no connection manager is attached

        """
        await self.connected.unpair()

    async def read_rssi(self) -> int:
        """Read the RSSI (signal strength) of the connection.

        Convenience method that delegates to device.connected.read_rssi().

        Returns:
            RSSI value in dBm (typically negative, e.g., -60)

        Raises:
            RuntimeError: If no connection manager is attached

        """
        return await self.connected.read_rssi()

    def set_disconnected_callback(self, callback: Callable[[], None]) -> None:
        """Set a callback to be invoked when the device disconnects.

        Convenience method that delegates to device.connected.set_disconnected_callback().

        Args:
            callback: Function to call when disconnection occurs

        Raises:
            RuntimeError: If no connection manager is attached

        """
        self.connected.set_disconnected_callback(callback)

    @property
    def mtu_size(self) -> int:
        """Get the negotiated MTU size in bytes.

        Delegates to device.connected.mtu_size.

        Returns:
            The MTU size negotiated for this connection (typically 23-512 bytes)

        Raises:
            RuntimeError: If no connection manager is attached

        """
        return self.connected.mtu_size

    async def refresh_advertisement(self, refresh: bool = False) -> AdvertisementData | None:
        """Get advertisement data from the connection manager.

        Args:
            refresh: If True, perform an active scan to get fresh advertisement
                    data from the device. If False, return the last cached value.

        Returns:
            Interpreted AdvertisementData if available, None if no advertisement
            has been received by the connection manager yet.

        Raises:
            RuntimeError: If no connection manager is attached

        Example::

            device.attach_connection_manager(manager)

            # Get cached advertisement (fast, no BLE activity)
            ad = await device.refresh_advertisement()

            # Force fresh scan (slower, active BLE scan)
            ad = await device.refresh_advertisement(refresh=True)

            if ad and ad.interpreted_data:
                print(f"Sensor: {ad.interpreted_data}")

        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        advertisement = await self.connection_manager.get_latest_advertisement(refresh=refresh)
        if advertisement is None:
            return None

        # Process and cache the advertisement
        processed_ad, _result = self.advertising.process_from_connection_manager(advertisement)
        self._last_advertisement = processed_ad

        # Update device name if not set
        if advertisement.ad_structures.core.local_name and not self.name:
            self.name = advertisement.ad_structures.core.local_name

        return processed_ad

    def parse_raw_advertisement(self, raw_data: bytes, rssi: int = 0) -> AdvertisementData:
        """Parse raw advertising PDU bytes directly.

        Use this method when you have raw BLE advertising PDU bytes (e.g., from
        a custom BLE stack or packet capture). For framework-integrated scanning,
        use the connection manager's convert_advertisement() followed by
        update_advertisement() instead.

        Args:
            raw_data: Raw BLE advertising PDU bytes
            rssi: Received signal strength in dBm

        Returns:
            AdvertisementData with parsed AD structures and vendor interpretation

        Example:
            # Parse raw PDU bytes directly
            result = device.parse_raw_advertisement(pdu_bytes, rssi=-65)
            print(result.manufacturer_data)

        """
        # Delegate to advertising subsystem
        advertisement, _result = self.advertising.parse_raw_pdu(raw_data, rssi)
        self._last_advertisement = advertisement

        # Update device name if present and not already set
        if advertisement.ad_structures.core.local_name and not self.name:
            self.name = advertisement.ad_structures.core.local_name

        return advertisement

    def get_characteristic_data(self, char_uuid: BluetoothUUID) -> Any | None:  # noqa: ANN401  # Heterogeneous cache
        """Get parsed characteristic data - single source of truth via characteristic.last_parsed.

        Searches across all services to find the characteristic by UUID.

        Args:
            char_uuid: UUID of the characteristic

        Returns:
            Parsed characteristic value if found, None otherwise.

        Example::

            # Search for characteristic across all services
            battery_data = device.get_characteristic_data(BluetoothUUID("2A19"))
            if battery_data is not None:
                print(f"Battery: {battery_data}%")

        """
        char_instance = self._get_cached_characteristic(char_uuid)
        if char_instance is not None:
            return char_instance.last_parsed
        return None

    async def discover_services(self) -> dict[str, Any]:
        """Discover services and characteristics from the connected BLE device.

        This method performs BLE service discovery using the attached connection
        manager, retrieving the device's service structure with characteristics
        and their runtime properties (READ, WRITE, NOTIFY, etc.).

        The discovered services are stored in `self.services` as DeviceService
        objects with properly instantiated characteristic classes from the registry.

        This implements the standard BLE workflow:
            1. await device.connect()
            2. await device.discover_services()  # This method
            3. value = await device.read("battery_level")

        Note:
            - This method discovers the SERVICE STRUCTURE (what services/characteristics
              exist and their properties), but does NOT read characteristic VALUES.
            - Use `read()` to retrieve actual characteristic values after discovery.
            - Services are cached in `self.services` keyed by service UUID string.

        Returns:
            Dictionary mapping service UUIDs to DeviceService objects

        Raises:
            RuntimeError: If no connection manager is attached

        Example::

            device = Device(address, translator)
            device.attach_connection_manager(manager)

            await device.connect()
            services = await device.discover_services()  # Discover structure

            # Now services are available
            for service_uuid, device_service in services.items():
                print(f"Service: {service_uuid}")
                for char_uuid, char_instance in device_service.characteristics.items():
                    print(f"  Characteristic: {char_uuid}")

            # Read characteristic values
            battery = await device.read("battery_level")

        """
        # Delegate to connected subsystem
        services_list = await self.connected.discover_services()

        # Invalidate device_info cache since services changed
        self._device_info_cache = None

        # Return as dict for backward compatibility
        return {str(svc.uuid): svc for svc in services_list}

    async def get_characteristic_info(self, char_uuid: str) -> Any | None:  # noqa: ANN401  # Adapter-specific characteristic metadata
        """Get information about a characteristic from the connection manager.

        Args:
            char_uuid: UUID of the characteristic

        Returns:
            Characteristic information or None if not found

        Raises:
            RuntimeError: If no connection manager is attached

        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        services_data = await self.connection_manager.get_services()
        for service_info in services_data:
            for char_uuid_key, char_info in service_info.characteristics.items():
                if char_uuid_key == char_uuid:
                    return char_info
        return None

    async def read_multiple(self, char_names: list[str | CharacteristicName]) -> dict[str, Any | None]:
        """Read multiple characteristics in batch.

        Args:
            char_names: List of characteristic names or enums to read

        Returns:
            Dictionary mapping characteristic UUIDs to parsed values

        Raises:
            RuntimeError: If no connection manager is attached

        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        results: dict[str, Any | None] = {}
        for char_name in char_names:
            try:
                value = await self.read(char_name)
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[str(resolved_uuid)] = value
            except Exception as exc:  # pylint: disable=broad-exception-caught
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[str(resolved_uuid)] = None
                logging.warning("Failed to read characteristic %s: %s", char_name, exc)

        return results

    async def write_multiple(
        self, data_map: dict[str | CharacteristicName, bytes], response: bool = True
    ) -> dict[str, bool]:
        """Write to multiple characteristics in batch.

        Args:
            data_map: Dictionary mapping characteristic names/enums to data bytes
            response: If True, use write-with-response for all writes.
                     If False, use write-without-response for all writes.

        Returns:
            Dictionary mapping characteristic UUIDs to success status

        Raises:
            RuntimeError: If no connection manager is attached

        """
        if not self.connection_manager:
            raise RuntimeError("No connection manager attached to Device")

        results: dict[str, bool] = {}
        for char_name, data in data_map.items():
            try:
                await self.write(char_name, data, response=response)
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[str(resolved_uuid)] = True
            except Exception as exc:  # pylint: disable=broad-exception-caught
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[str(resolved_uuid)] = False
                logging.warning("Failed to write characteristic %s: %s", char_name, exc)

        return results

    @property
    def device_info(self) -> DeviceInfo:
        """Get cached device info object.

        Returns:
            DeviceInfo with current device metadata

        """
        if self._device_info_cache is None:
            self._device_info_cache = DeviceInfo(
                address=self.address,
                name=self.name,
                manufacturer_data=self._last_advertisement.ad_structures.core.manufacturer_data
                if self._last_advertisement
                else {},
                service_uuids=self._last_advertisement.ad_structures.core.service_uuids
                if self._last_advertisement
                else [],
            )
        else:
            # Update existing cache object with current data
            self._device_info_cache.name = self.name
            if self._last_advertisement:
                self._device_info_cache.manufacturer_data = (
                    self._last_advertisement.ad_structures.core.manufacturer_data
                )
                self._device_info_cache.service_uuids = self._last_advertisement.ad_structures.core.service_uuids
        return self._device_info_cache

    @property
    def name(self) -> str:
        """Get the device name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the device name and update cached device_info."""
        self._name = value
        # Update existing cache object if it exists
        if self._device_info_cache is not None:
            self._device_info_cache.name = value

    @property
    def is_connected(self) -> bool:
        """Check if the device is currently connected.

        Delegates to device.connected.is_connected.

        Returns:
            True if connected, False otherwise

        """
        return self.connected.is_connected

    @property
    def last_advertisement(self) -> AdvertisementData | None:
        """Get the last received advertisement data.

        This is automatically updated when advertisements are processed via
        refresh_advertisement() or parse_raw_advertisement().

        Returns:
            AdvertisementData with AD structures and interpreted_data if available,
            None if no advertisement has been received yet.

        """
        return self._last_advertisement

    def get_service_by_uuid(self, service_uuid: str) -> DeviceService | None:
        """Get a service by its UUID.

        Args:
            service_uuid: UUID of the service

        Returns:
            DeviceService instance or None if not found

        """
        return self.services.get(service_uuid)

    def get_services_by_name(self, service_name: str | ServiceName) -> list[DeviceService]:
        """Get services by name.

        Args:
            service_name: Name or enum of the service

        Returns:
            List of matching DeviceService instances

        """
        service_uuid = self.translator.get_service_uuid_by_name(
            service_name if isinstance(service_name, str) else service_name.value
        )
        if service_uuid and str(service_uuid) in self.services:
            return [self.services[str(service_uuid)]]
        return []

    def list_characteristics(self, service_uuid: str | None = None) -> dict[str, list[str]]:
        """List all characteristics, optionally filtered by service.

        Args:
            service_uuid: Optional service UUID to filter by

        Returns:
            Dictionary mapping service UUIDs to lists of characteristic UUIDs

        """
        if service_uuid:
            service = self.services.get(service_uuid)
            if service:
                return {service_uuid: list(service.characteristics.keys())}
            return {}

        return {svc_uuid: list(service.characteristics.keys()) for svc_uuid, service in self.services.items()}

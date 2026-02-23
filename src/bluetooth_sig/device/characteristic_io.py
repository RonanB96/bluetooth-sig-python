"""Characteristic I/O operations for BLE devices.

Encapsulates read, write, and notification operations for GATT characteristics,
including type-safe overloads for class-based and string/enum-based access.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, TypeVar, cast, overload

from ..gatt.characteristics import CharacteristicName
from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.characteristics.registry import CharacteristicRegistry
from ..gatt.context import CharacteristicContext, DeviceInfo
from ..types.uuid import BluetoothUUID
from .client import ClientManagerProtocol
from .dependency_resolver import DependencyResolutionMode, DependencyResolver
from .protocols import SIGTranslatorProtocol

logger = logging.getLogger(__name__)

# Type variable for generic characteristic return types
T = TypeVar("T")


class CharacteristicIO:
    """Read, write, and notification operations for GATT characteristics.

    Encapsulates the I/O logic extracted from Device, handling both type-safe
    (class-based) and dynamic (string/enum-based) characteristic access patterns.

    Uses ``DependencyResolver`` for automatic dependency resolution before reads,
    and a ``device_info_factory`` callable to get current ``DeviceInfo`` without
    a back-reference to the owning Device.
    """

    def __init__(
        self,
        connection_manager: ClientManagerProtocol,
        translator: SIGTranslatorProtocol,
        dep_resolver: DependencyResolver,
        device_info_factory: Callable[[], DeviceInfo],
    ) -> None:
        """Initialise with connection manager, translator, resolver, and info factory.

        Args:
            connection_manager: Connection manager for BLE I/O
            translator: Translator for parsing/encoding characteristics
            dep_resolver: Resolver for characteristic dependencies
            device_info_factory: Callable returning current DeviceInfo

        """
        self._connection_manager = connection_manager
        self._translator = translator
        self._dep_resolver = dep_resolver
        self._device_info_factory = device_info_factory

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

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

        """
        # Handle characteristic class input (type-safe path)
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            char_class: type[BaseCharacteristic[Any]] = char
            char_instance = char_class()
            resolved_uuid = char_instance.uuid

            ctx: CharacteristicContext | None = None
            if resolution_mode != DependencyResolutionMode.SKIP_DEPENDENCIES:
                device_info = self._device_info_factory()
                ctx = await self._dep_resolver.resolve(char_class, resolution_mode, device_info)

            raw = await self._connection_manager.read_gatt_char(resolved_uuid)
            return char_instance.parse_value(raw, ctx=ctx)

        # Handle string/enum input (not type-safe path)
        resolved_uuid = self._resolve_characteristic_name(char)

        char_class_lookup = CharacteristicRegistry.get_characteristic_class_by_uuid(resolved_uuid)

        # Resolve dependencies if characteristic class is known
        ctx = None
        if char_class_lookup and resolution_mode != DependencyResolutionMode.SKIP_DEPENDENCIES:
            device_info = self._device_info_factory()
            ctx = await self._dep_resolver.resolve(char_class_lookup, resolution_mode, device_info)

        # Read the characteristic
        raw = await self._connection_manager.read_gatt_char(resolved_uuid)
        return self._translator.parse_characteristic(str(resolved_uuid), raw, ctx=ctx)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

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

        """
        # Handle characteristic class input (type-safe path)
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            char_instance = char()
            resolved_uuid = char_instance.uuid
            # data is typed value T, encode it
            encoded = char_instance.build_value(data)  # type: ignore[arg-type]  # T is erased at runtime; overload ensures type safety at call site
            await self._connection_manager.write_gatt_char(resolved_uuid, bytes(encoded), response=response)
            return

        # Handle string/enum input (not type-safe path)
        # data must be bytes in this path
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f"When using string/enum char_name, data must be bytes, got {type(data).__name__}")

        resolved_uuid = self._resolve_characteristic_name(char)
        # cast is safe: isinstance check above ensures data is bytes/bytearray
        await self._connection_manager.write_gatt_char(resolved_uuid, cast("bytes", data), response=response)

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

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

        """
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
                    logger.exception("Notification callback raised an exception")

            await self._connection_manager.start_notify(resolved_uuid, _typed_cb)
            return

        # Handle string/enum input (not type-safe path)
        resolved_uuid = self._resolve_characteristic_name(char)
        translator = self._translator

        def _internal_cb(sender: str, data: bytes) -> None:
            parsed = translator.parse_characteristic(sender, data)
            try:
                callback(parsed)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Notification callback raised an exception")

        await self._connection_manager.start_notify(resolved_uuid, _internal_cb)

    async def stop_notify(self, char_name: str | CharacteristicName) -> None:
        """Stop notifications for a characteristic.

        Args:
            char_name: Characteristic name or UUID

        """
        resolved_uuid = self._resolve_characteristic_name(char_name)
        await self._connection_manager.stop_notify(resolved_uuid)

    # ------------------------------------------------------------------
    # Batch operations
    # ------------------------------------------------------------------

    async def read_multiple(self, char_names: list[str | CharacteristicName]) -> dict[str, Any | None]:
        """Read multiple characteristics in batch.

        Args:
            char_names: List of characteristic names or enums to read

        Returns:
            Dictionary mapping characteristic UUIDs to parsed values

        """
        results: dict[str, Any | None] = {}
        for char_name in char_names:
            try:
                value = await self.read(char_name)
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[str(resolved_uuid)] = value
            except Exception as exc:  # pylint: disable=broad-exception-caught
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[str(resolved_uuid)] = None
                logger.warning("Failed to read characteristic %s: %s", char_name, exc)

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

        """
        results: dict[str, bool] = {}
        for char_name, data in data_map.items():
            try:
                await self.write(char_name, data, response=response)
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[str(resolved_uuid)] = True
            except Exception as exc:  # pylint: disable=broad-exception-caught
                resolved_uuid = self._resolve_characteristic_name(char_name)
                results[str(resolved_uuid)] = False
                logger.warning("Failed to write characteristic %s: %s", char_name, exc)

        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

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
            uuid = self._translator.get_characteristic_uuid_by_name(identifier)
            if uuid:
                return uuid
            norm = identifier.value.strip()
        else:
            norm = identifier
        stripped = norm.replace("-", "")
        if len(stripped) in (4, 8, 32) and all(c in "0123456789abcdefABCDEF" for c in stripped):
            return BluetoothUUID(norm)

        raise ValueError(f"Unknown characteristic name: '{identifier}'")

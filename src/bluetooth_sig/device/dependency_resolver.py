"""Dependency resolution for characteristic reads.

Resolves required and optional dependencies before reading a characteristic,
building a ``CharacteristicContext`` will all resolved dependency values.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.characteristics.registry import CharacteristicRegistry
from ..gatt.characteristics.unknown import UnknownCharacteristic
from ..gatt.context import CharacteristicContext, DeviceInfo
from ..types import CharacteristicInfo
from ..types.uuid import BluetoothUUID
from .client import ClientManagerProtocol
from .connected import DeviceConnected

logger = logging.getLogger(__name__)


class DependencyResolver:
    """Resolves characteristic dependencies by reading them from the device.

    Encapsulates the logic for:
    - Discovering which dependencies a characteristic declares
    - Reading dependency values from the device (with caching)
    - Building a ``CharacteristicContext`` for the target characteristic

    Uses ``DeviceConnected`` for characteristic instance caching and
    ``ClientManagerProtocol`` for BLE reads.
    """

    def __init__(
        self,
        connection_manager: ClientManagerProtocol,
        connected: DeviceConnected,
    ) -> None:
        """Initialise with connection manager and connected subsystem.

        Args:
            connection_manager: Connection manager for BLE reads
            connected: Connected subsystem for characteristic cache

        """
        self._connection_manager = connection_manager
        self._connected = connected

    async def resolve(
        self,
        char_class: type[BaseCharacteristic[Any]],
        resolution_mode: DependencyResolutionMode,
        device_info: DeviceInfo,
    ) -> CharacteristicContext:
        """Ensure all dependencies for a characteristic are resolved.

        Automatically reads feature characteristics needed for validation
        of measurement characteristics. Feature characteristics are cached
        after first read.

        Args:
            char_class: The characteristic class to resolve dependencies for
            resolution_mode: How to handle dependency resolution
            device_info: Current device info for context construction

        Returns:
            CharacteristicContext with resolved dependencies

        Raises:
            RuntimeError: If no connection manager is attached

        """
        optional_deps = getattr(char_class, "_optional_dependencies", [])
        required_deps = getattr(char_class, "_required_dependencies", [])

        context_chars: dict[str, Any] = {}

        for dep_class in required_deps + optional_deps:
            is_required = dep_class in required_deps

            dep_uuid = dep_class.get_class_uuid()
            if not dep_uuid:
                if is_required:
                    raise ValueError(f"Required dependency {dep_class.__name__} has no UUID")
                continue

            dep_uuid_str = str(dep_uuid)

            if resolution_mode == DependencyResolutionMode.SKIP_DEPENDENCIES:
                continue

            # Check cache (unless force refresh)
            if resolution_mode != DependencyResolutionMode.FORCE_REFRESH:
                cached_char = self._connected.get_cached_characteristic(dep_uuid)
                if cached_char is not None and cached_char.last_parsed is not None:
                    context_chars[dep_uuid_str] = cached_char.last_parsed
                    continue

            parsed_data = await self._resolve_single(dep_uuid, is_required, dep_class)
            if parsed_data is not None:
                context_chars[dep_uuid_str] = parsed_data

        return CharacteristicContext(
            device_info=device_info,
            other_characteristics=context_chars,
        )

    async def _resolve_single(
        self,
        dep_uuid: BluetoothUUID,
        is_required: bool,
        dep_class: type[BaseCharacteristic[Any]],
    ) -> Any | None:  # noqa: ANN401  # Dependency can be any characteristic type
        """Read and parse a single dependency characteristic.

        Args:
            dep_uuid: UUID of the dependency characteristic
            is_required: Whether this is a required dependency
            dep_class: The dependency characteristic class

        Returns:
            Parsed characteristic data, or None if optional and failed

        Raises:
            ValueError: If required dependency fails to read

        """
        dep_uuid_str = str(dep_uuid)

        try:
            raw_data = await self._connection_manager.read_gatt_char(dep_uuid)

            char_instance = self._connected.get_cached_characteristic(dep_uuid)
            if char_instance is None:
                char_class_or_none = CharacteristicRegistry.get_characteristic_class_by_uuid(dep_uuid)
                if char_class_or_none:
                    char_instance = char_class_or_none()
                else:
                    char_info = CharacteristicInfo(uuid=dep_uuid, name=f"Unknown-{dep_uuid_str}")
                    char_instance = UnknownCharacteristic(info=char_info)

                self._connected.cache_characteristic(dep_uuid, char_instance)

            return char_instance.parse_value(raw_data)

        except Exception as e:  # pylint: disable=broad-exception-caught
            if is_required:
                raise ValueError(
                    f"Failed to read required dependency {dep_class.__name__} ({dep_uuid_str}): {e}"
                ) from e
            logger.warning("Failed to read optional dependency %s: %s", dep_class.__name__, e)
            return None


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

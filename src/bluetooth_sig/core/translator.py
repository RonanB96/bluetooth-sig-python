"""Core Bluetooth SIG standards translator functionality."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from graphlib import TopologicalSorter
from typing import Any, cast

from ..gatt.characteristics.base import BaseCharacteristic, CharacteristicData
from ..gatt.characteristics.custom import CustomBaseCharacteristic
from ..gatt.characteristics.registry import CharacteristicRegistry
from ..gatt.characteristics.unknown import UnknownCharacteristic
from ..gatt.exceptions import MissingDependencyError
from ..gatt.services import ServiceName
from ..gatt.services.base import BaseGattService
from ..gatt.services.custom import CustomBaseGattService
from ..gatt.services.registry import GattServiceRegistry
from ..gatt.uuid_registry import CustomUuidEntry, uuid_registry
from ..types import (
    CharacteristicContext,
    CharacteristicDataProtocol,
    CharacteristicInfo,
    ServiceInfo,
    SIGInfo,
    ValidationResult,
)
from ..types.gatt_enums import CharacteristicName, ValueType
from ..types.uuid import BluetoothUUID

# Type alias for characteristic data in process_services
CharacteristicDataDict = dict[str, Any]

logger = logging.getLogger(__name__)


class BluetoothSIGTranslator:  # pylint: disable=too-many-public-methods
    """Pure Bluetooth SIG standards translator for characteristic and service interpretation.

    This class provides the primary API surface for Bluetooth SIG standards translation,
    covering characteristic parsing, service discovery, UUID resolution, and registry
    management.

    Singleton Pattern:
        This class is implemented as a singleton to provide a global registry for
        custom characteristics and services. Access the singleton instance using
        `BluetoothSIGTranslator.get_instance()` or the module-level `translator` variable.

    Key features:
    - Parse raw BLE characteristic data using Bluetooth SIG specifications
    - Resolve UUIDs to [CharacteristicInfo][bluetooth_sig.types.CharacteristicInfo]
      and [ServiceInfo][bluetooth_sig.types.ServiceInfo]
    - Create BaseGattService instances from service UUIDs
    - Access comprehensive registry of supported characteristics and services

    Note: This class intentionally has >20 public methods as it serves as the
    primary API surface for Bluetooth SIG standards translation. The methods are
    organized by functionality and reducing them would harm API clarity.
    """

    _instance: BluetoothSIGTranslator | None = None
    _instance_lock: bool = False  # Simple lock to prevent recursion

    def __new__(cls) -> BluetoothSIGTranslator:
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> BluetoothSIGTranslator:
        """Get the singleton instance of BluetoothSIGTranslator.

        Returns:
            The singleton BluetoothSIGTranslator instance

        Example:
            ```python
            from bluetooth_sig import BluetoothSIGTranslator

            # Get the singleton instance
            translator = BluetoothSIGTranslator.get_instance()
            ```
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        """Initialize the SIG translator (singleton pattern)."""
        # Only initialize once
        if self.__class__._instance_lock:
            return
        self.__class__._instance_lock = True

        self._services: dict[str, BaseGattService] = {}

    def __str__(self) -> str:
        """Return string representation of the translator."""
        return "BluetoothSIGTranslator(pure SIG standards)"

    def parse_characteristic(
        self,
        uuid: str,
        raw_data: bytes | bytearray,
        ctx: CharacteristicContext | None = None,
    ) -> CharacteristicData:
        r"""Parse a characteristic's raw data using Bluetooth SIG standards.

        Args:
            uuid: The characteristic UUID (with or without dashes)
            raw_data: Raw bytes from the characteristic (bytes or bytearray)
            ctx: Optional CharacteristicContext providing device-level info

        Returns:
            CharacteristicData with parsed value and metadata

        Example:
            Parse battery level data:

            ```python
            from bluetooth_sig import BluetoothSIGTranslator

            translator = BluetoothSIGTranslator()
            result = translator.parse_characteristic("2A19", b"\x64")
            print(f"Battery: {result.value}%")  # Battery: 100%
            ```

        """
        logger.debug("Parsing characteristic UUID=%s, data_len=%d", uuid, len(raw_data))

        # Create characteristic instance for parsing
        characteristic = CharacteristicRegistry.create_characteristic(uuid)

        if characteristic:
            logger.debug("Found parser for UUID=%s: %s", uuid, type(characteristic).__name__)
            # Use the parse_value method; pass context when provided.
            result = characteristic.parse_value(raw_data, ctx)

            if result.parse_success:
                logger.debug("Successfully parsed %s: %s", characteristic.name, result.value)
            else:
                logger.warning("Parse failed for %s: %s", characteristic.name, result.error_message)

        else:
            # No parser found, return fallback result
            logger.info("No parser available for UUID=%s", uuid)

            fallback_info = CharacteristicInfo(
                uuid=BluetoothUUID(uuid),
                name="Unknown",
                description="",
                value_type=ValueType.UNKNOWN,
                unit="",
            )
            fallback_char = UnknownCharacteristic(info=fallback_info)
            # Ensure raw bytes are passed as immutable bytes object
            raw_bytes = bytes(raw_data) if isinstance(raw_data, (bytearray, memoryview)) else raw_data
            result = CharacteristicData(
                characteristic=fallback_char,
                value=raw_bytes,
                raw_data=raw_bytes,
                parse_success=False,
                error_message="No parser available for this characteristic UUID",
            )

        return result

    def get_characteristic_info_by_uuid(self, uuid: str) -> CharacteristicInfo | None:
        """Get information about a characteristic by UUID.

        Retrieve metadata for a Bluetooth characteristic using its UUID. This includes
        the characteristic's name, description, value type, unit, and properties.

        Args:
            uuid: The characteristic UUID (16-bit short form or full 128-bit)

        Returns:
            [CharacteristicInfo][bluetooth_sig.CharacteristicInfo] with metadata or None if not found

        Example:
            Get battery level characteristic info:

            ```python
            from bluetooth_sig import BluetoothSIGTranslator

            translator = BluetoothSIGTranslator()
            info = translator.get_characteristic_info_by_uuid("2A19")
            if info:
                print(f"Name: {info.name}")  # Name: Battery Level
            ```

        """
        try:
            bt_uuid = BluetoothUUID(uuid)
        except ValueError:
            return None

        char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(bt_uuid)
        if not char_class:
            return None

        # Create temporary instance to get metadata (no parameters needed for auto-resolution)
        try:
            temp_char = char_class()
            return temp_char.info
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def get_characteristic_uuid_by_name(self, name: CharacteristicName) -> BluetoothUUID | None:
        """Get the UUID for a characteristic name enum.

        Args:
            name: CharacteristicName enum

        Returns:
            Characteristic UUID or None if not found

        """
        info = self.get_characteristic_info_by_name(name)
        return info.uuid if info else None

    def get_service_uuid_by_name(self, name: str | ServiceName) -> BluetoothUUID | None:
        """Get the UUID for a service name or enum.

        Args:
            name: Service name or enum

        Returns:
            Service UUID or None if not found

        """
        name_str = name.value if isinstance(name, ServiceName) else name
        info = self.get_service_info_by_name(name_str)
        return info.uuid if info else None

    def get_characteristic_info_by_name(self, name: CharacteristicName) -> CharacteristicInfo | None:
        """Get characteristic info by enum name.

        Args:
            name: CharacteristicName enum

        Returns:
            CharacteristicInfo if found, None otherwise

        """
        char_class = CharacteristicRegistry.get_characteristic_class(name)
        if not char_class:
            return None

        # Try get_configured_info first (for custom characteristics)
        info = char_class.get_configured_info()
        if info:
            return info

        # For SIG characteristics, create temporary instance to get metadata
        try:
            temp_char = char_class()
            return temp_char.info
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def get_service_info_by_name(self, name: str) -> ServiceInfo | None:
        """Get service info by name instead of UUID.

        Args:
            name: Service name

        Returns:
            ServiceInfo if found, None otherwise

        """
        # Use UUID registry for name-based lookup
        try:
            uuid_info = uuid_registry.get_service_info(name)
            if uuid_info:
                return ServiceInfo(uuid=uuid_info.uuid, name=uuid_info.name, characteristics=[])
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        return None

    def get_service_info_by_uuid(self, uuid: str) -> ServiceInfo | None:
        """Get information about a service by UUID.

        Args:
            uuid: The service UUID

        Returns:
            ServiceInfo with metadata or None if not found

        """
        service_class = GattServiceRegistry.get_service_class_by_uuid(BluetoothUUID(uuid))
        if not service_class:
            return None

        try:
            temp_service = service_class()
            # Convert characteristics dict to list of CharacteristicInfo
            char_infos: list[CharacteristicInfo] = []
            for _, char_instance in temp_service.characteristics.items():
                # Use public info property
                char_infos.append(char_instance.info)
            return ServiceInfo(
                uuid=temp_service.uuid,
                name=temp_service.name,
                characteristics=char_infos,
            )
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def list_supported_characteristics(self) -> dict[str, str]:
        """List all supported characteristics with their names and UUIDs.

        Returns:
            Dictionary mapping characteristic names to UUIDs

        """
        result: dict[str, str] = {}
        for name, char_class in CharacteristicRegistry.get_all_characteristics().items():
            # Try to get configured_info from class using public accessor
            configured_info = char_class.get_configured_info()
            if configured_info:
                # Convert CharacteristicName enum to string for dict key
                name_str = name.value if hasattr(name, "value") else str(name)
                result[name_str] = str(configured_info.uuid)
        return result

    def list_supported_services(self) -> dict[str, str]:
        """List all supported services with their names and UUIDs.

        Returns:
            Dictionary mapping service names to UUIDs

        """
        result: dict[str, str] = {}
        for service_class in GattServiceRegistry.get_all_services():
            try:
                temp_service = service_class()
                service_name = getattr(temp_service, "_service_name", service_class.__name__)
                result[service_name] = str(temp_service.uuid)
            except Exception:  # pylint: disable=broad-exception-caught
                continue
        return result

    def process_services(self, services: dict[str, dict[str, CharacteristicDataDict]]) -> None:
        """Process discovered services and their characteristics.

        Args:
            services: Dictionary of service UUIDs to their characteristics

        """
        for uuid_str, service_data in services.items():
            uuid = BluetoothUUID(uuid_str)
            # Convert dict[str, dict] to ServiceDiscoveryData
            characteristics: dict[BluetoothUUID, CharacteristicInfo] = {}
            for char_uuid_str, char_data in service_data.get("characteristics", {}).items():
                char_uuid = BluetoothUUID(char_uuid_str)
                # Create CharacteristicInfo from dict
                vtype_raw = char_data.get("value_type", "bytes")
                if isinstance(vtype_raw, str):
                    value_type = ValueType(vtype_raw)
                elif isinstance(vtype_raw, ValueType):
                    value_type = vtype_raw
                else:
                    value_type = ValueType.BYTES
                characteristics[char_uuid] = CharacteristicInfo(
                    uuid=char_uuid,
                    name=char_data.get("name", ""),
                    unit=char_data.get("unit", ""),
                    value_type=value_type,
                )
            service = GattServiceRegistry.create_service(uuid, characteristics)
            if service:
                self._services[str(uuid)] = service

    def get_service_by_uuid(self, uuid: str) -> BaseGattService | None:
        """Get a service instance by UUID.

        Args:
            uuid: The service UUID

        Returns:
            Service instance if found, None otherwise

        """
        return self._services.get(uuid)

    @property
    def discovered_services(self) -> list[BaseGattService]:
        """Get list of discovered service instances.

        Returns:
            List of discovered service instances

        """
        return list(self._services.values())

    def clear_services(self) -> None:
        """Clear all discovered services."""
        self._services.clear()

    def get_sig_info_by_name(self, name: str) -> SIGInfo | None:
        """Get Bluetooth SIG information for a characteristic or service by name.

        Args:
            name: Characteristic or service name

        Returns:
            CharacteristicInfo or ServiceInfo if found, None otherwise

        """
        # Use the UUID registry for name-based lookups (string inputs).
        try:
            char_info = uuid_registry.get_characteristic_info(name)
            if char_info:
                # Build CharacteristicInfo from registry data
                value_type = ValueType.UNKNOWN
                if char_info.value_type:
                    try:
                        value_type = ValueType(char_info.value_type)
                    except (ValueError, KeyError):
                        value_type = ValueType.UNKNOWN
                return CharacteristicInfo(
                    uuid=char_info.uuid,
                    name=char_info.name,
                    value_type=value_type,
                    unit=char_info.unit or "",
                )
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        # Try service
        service_info = self.get_service_info_by_name(name)
        if service_info:
            return service_info

        return None

    def get_sig_info_by_uuid(self, uuid: str) -> SIGInfo | None:
        """Get Bluetooth SIG information for a UUID.

        Args:
            uuid: UUID string (with or without dashes)

        Returns:
            CharacteristicInfo or ServiceInfo if found, None otherwise

        """
        # Try characteristic first
        char_info = self.get_characteristic_info_by_uuid(uuid)
        if char_info:
            return char_info

        # Try service
        service_info = self.get_service_info_by_uuid(uuid)
        if service_info:
            return service_info

        return None

    def parse_characteristics(
        self,
        char_data: dict[str, bytes],
        ctx: CharacteristicContext | None = None,
    ) -> dict[str, CharacteristicData]:
        r"""Parse multiple characteristics at once with dependency-aware ordering.

        This method automatically handles multi-characteristic dependencies by parsing
        independent characteristics first, then parsing characteristics that depend on them.
        The parsing order is determined by the `required_dependencies` and `optional_dependencies`
        attributes declared on characteristic classes.

        Required dependencies MUST be present and successfully parsed; missing required
        dependencies result in parse failure with MissingDependencyError. Optional dependencies
        enrich parsing when available but are not mandatory.

        Args:
            char_data: Dictionary mapping UUIDs to raw data bytes
            ctx: Optional CharacteristicContext used as the starting context

        Returns:
            Dictionary mapping UUIDs to CharacteristicData results

        Raises:
            ValueError: If circular dependencies are detected

        Example:
            Parse multiple environmental characteristics:

            ```python
            from bluetooth_sig import BluetoothSIGTranslator

            translator = BluetoothSIGTranslator()
            data = {
                "2A6E": b"\\x0A\\x00",  # Temperature
                "2A6F": b"\\x32\\x00",  # Humidity
            }
            results = translator.parse_characteristics(data)
            for uuid, result in results.items():
                print(f"{uuid}: {result.value}")
            ```

        """
        return self._parse_characteristics_batch(char_data, ctx)

    def _parse_characteristics_batch(
        self,
        char_data: dict[str, bytes],
        ctx: CharacteristicContext | None,
    ) -> dict[str, CharacteristicData]:
        """Parse multiple characteristics using dependency-aware ordering."""
        logger.debug("Batch parsing %d characteristics", len(char_data))

        # Prepare characteristics and dependencies
        uuid_to_characteristic, uuid_to_required_deps, uuid_to_optional_deps = (
            self._prepare_characteristic_dependencies(char_data)
        )

        # Resolve dependency order
        sorted_uuids = self._resolve_dependency_order(char_data, uuid_to_required_deps, uuid_to_optional_deps)

        # Build base context
        base_context = ctx

        results: dict[str, CharacteristicData] = {}
        for uuid_str in sorted_uuids:
            raw_data = char_data[uuid_str]
            characteristic = uuid_to_characteristic.get(uuid_str)

            missing_required = self._find_missing_required_dependencies(
                uuid_str,
                uuid_to_required_deps.get(uuid_str, []),
                results,
                base_context,
            )

            if missing_required:
                results[uuid_str] = self._build_missing_dependency_failure(
                    uuid_str,
                    raw_data,
                    characteristic,
                    missing_required,
                )
                continue

            self._log_optional_dependency_gaps(
                uuid_str,
                uuid_to_optional_deps.get(uuid_str, []),
                results,
                base_context,
            )

            parse_context = self._build_parse_context(base_context, results)

            results[uuid_str] = self.parse_characteristic(uuid_str, raw_data, ctx=parse_context)

        logger.debug("Batch parsing complete: %d results", len(results))
        return results

    def _prepare_characteristic_dependencies(
        self, characteristic_data: Mapping[str, bytes]
    ) -> tuple[dict[str, BaseCharacteristic], dict[str, list[str]], dict[str, list[str]]]:
        """Instantiate characteristics once and collect declared dependencies."""
        uuid_to_characteristic: dict[str, BaseCharacteristic] = {}
        uuid_to_required_deps: dict[str, list[str]] = {}
        uuid_to_optional_deps: dict[str, list[str]] = {}

        for uuid in characteristic_data:
            characteristic = CharacteristicRegistry.create_characteristic(uuid)
            if characteristic is None:
                continue

            uuid_to_characteristic[uuid] = characteristic

            required = characteristic.required_dependencies
            optional = characteristic.optional_dependencies

            if required:
                uuid_to_required_deps[uuid] = required
                logger.debug("Characteristic %s has required dependencies: %s", uuid, required)
            if optional:
                uuid_to_optional_deps[uuid] = optional
                logger.debug("Characteristic %s has optional dependencies: %s", uuid, optional)

        return uuid_to_characteristic, uuid_to_required_deps, uuid_to_optional_deps

    def _resolve_dependency_order(
        self,
        characteristic_data: Mapping[str, bytes],
        uuid_to_required_deps: Mapping[str, list[str]],
        uuid_to_optional_deps: Mapping[str, list[str]],
    ) -> list[str]:
        """Topologically sort characteristics based on declared dependencies."""
        try:
            sorter: TopologicalSorter[str] = TopologicalSorter()
            for uuid in characteristic_data:
                all_deps = uuid_to_required_deps.get(uuid, []) + uuid_to_optional_deps.get(uuid, [])
                batch_deps = [dep for dep in all_deps if dep in characteristic_data]
                sorter.add(uuid, *batch_deps)

            sorted_sequence = sorter.static_order()
            sorted_uuids = list(sorted_sequence)
            logger.debug("Dependency-sorted parsing order: %s", sorted_uuids)
            return sorted_uuids
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("Dependency sorting failed: %s. Using original order.", exc)
            return list(characteristic_data.keys())

    def _find_missing_required_dependencies(
        self,
        uuid: str,
        required_deps: list[str],
        results: Mapping[str, CharacteristicData],
        base_context: CharacteristicContext | None,
    ) -> list[str]:
        """Determine which required dependencies are unavailable for a characteristic."""
        if not required_deps:
            return []

        missing: list[str] = []
        other_characteristics = (
            base_context.other_characteristics if base_context and base_context.other_characteristics else None
        )

        for dep_uuid in required_deps:
            if dep_uuid in results:
                if not results[dep_uuid].parse_success:
                    missing.append(dep_uuid)
                continue

            if other_characteristics and dep_uuid in other_characteristics:
                if not other_characteristics[dep_uuid].parse_success:
                    missing.append(dep_uuid)
                continue

            missing.append(dep_uuid)

        if missing:
            logger.debug("Characteristic %s missing required dependencies: %s", uuid, missing)

        return missing

    def _build_missing_dependency_failure(
        self,
        uuid: str,
        raw_data: bytes,
        characteristic: BaseCharacteristic | None,
        missing_required: list[str],
    ) -> CharacteristicData:
        """Create a failure result when required dependencies are absent."""
        char_name = characteristic.name if characteristic else "Unknown"
        error = MissingDependencyError(char_name, missing_required)
        logger.warning("Skipping %s due to missing required dependencies: %s", uuid, missing_required)

        # Create a characteristic to hold the failure info
        if characteristic is not None:
            failure_char = characteristic
        else:
            fallback_info = self.get_characteristic_info_by_uuid(uuid)
            if fallback_info is not None:
                failure_info = fallback_info
            else:
                failure_info = CharacteristicInfo(
                    uuid=BluetoothUUID(uuid),
                    name=char_name,
                    description="",
                    value_type=ValueType.UNKNOWN,
                    unit="",
                )

            failure_char = UnknownCharacteristic(info=failure_info)

        return CharacteristicData(
            characteristic=failure_char,
            value=None,
            raw_data=raw_data,
            parse_success=False,
            error_message=str(error),
        )

    def _log_optional_dependency_gaps(
        self,
        uuid: str,
        optional_deps: list[str],
        results: Mapping[str, CharacteristicData],
        base_context: CharacteristicContext | None,
    ) -> None:
        """Emit debug logs when optional dependencies are unavailable."""
        if not optional_deps:
            return

        other_characteristics = (
            base_context.other_characteristics if base_context and base_context.other_characteristics else None
        )

        for dep_uuid in optional_deps:
            if dep_uuid in results:
                continue
            if other_characteristics and dep_uuid in other_characteristics:
                continue
            logger.debug("Optional dependency %s not available for %s", dep_uuid, uuid)

    def _build_parse_context(
        self,
        base_context: CharacteristicContext | None,
        results: Mapping[str, CharacteristicData],
    ) -> CharacteristicContext:
        """Construct the context passed to per-characteristic parsers."""
        results_mapping = cast(Mapping[str, CharacteristicDataProtocol], results)

        if base_context is not None:
            return CharacteristicContext(
                device_info=base_context.device_info,
                advertisement=base_context.advertisement,
                other_characteristics=results_mapping,
                raw_service=base_context.raw_service,
            )

        return CharacteristicContext(other_characteristics=results_mapping)

    def get_characteristics_info_by_uuids(self, uuids: list[str]) -> dict[str, CharacteristicInfo | None]:
        """Get information about multiple characteristics by UUID.

        Args:
            uuids: List of characteristic UUIDs

        Returns:
            Dictionary mapping UUIDs to CharacteristicInfo
            (or None if not found)

        """
        results: dict[str, CharacteristicInfo | None] = {}
        for uuid in uuids:
            results[uuid] = self.get_characteristic_info_by_uuid(uuid)
        return results

    def validate_characteristic_data(self, uuid: str, data: bytes) -> ValidationResult:
        """Validate characteristic data format against SIG specifications.

        Args:
            uuid: The characteristic UUID
            data: Raw data bytes to validate

        Returns:
            ValidationResult with validation details

        """
        try:
            # Attempt to parse the data - if it succeeds, format is valid
            parsed = self.parse_characteristic(uuid, data)
            return ValidationResult(
                uuid=BluetoothUUID(uuid),
                name=parsed.characteristic.name,
                is_valid=parsed.parse_success,
                actual_length=len(data),
                error_message=parsed.error_message,
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            # If parsing failed, data format is invalid
            return ValidationResult(
                uuid=BluetoothUUID(uuid),
                name="Unknown",
                is_valid=False,
                actual_length=len(data),
                error_message=str(e),
            )

    def get_service_characteristics(self, service_uuid: str) -> list[str]:  # pylint: disable=too-many-return-statements
        """Get the characteristic UUIDs associated with a service.

        Args:
            service_uuid: The service UUID

        Returns:
            List of characteristic UUIDs for this service

        """
        service_class = GattServiceRegistry.get_service_class_by_uuid(BluetoothUUID(service_uuid))
        if not service_class:
            return []

        try:
            temp_service = service_class()
            required_chars = temp_service.get_required_characteristics()
            return [str(k) for k in required_chars]
        except Exception:  # pylint: disable=broad-exception-caught
            return []

    def register_custom_characteristic_class(
        self,
        characteristic_class: type[CustomBaseCharacteristic],
        override: bool = False,
    ) -> None:
        """Register a custom characteristic class at runtime.

        Args:
            characteristic_class: The characteristic class to register
            override: Whether to override existing registrations

        Raises:
            TypeError: If cls does not inherit from BaseCharacteristic
            ValueError: If class has no valid _info with UUID

        """
        # Extract UUID from class._info
        configured_info = characteristic_class.get_configured_info()
        if not configured_info or not configured_info.uuid:
            raise ValueError(
                f"Cannot register {characteristic_class.__name__}: class has no valid _info with UUID. "
                "Ensure the class has a _info class attribute with a valid CharacteristicInfo."
            )
        uuid_str = str(configured_info.uuid)

        # Register the class
        CharacteristicRegistry.register_characteristic_class(uuid_str, characteristic_class, override)

        # Register metadata in UUID registry
        entry = CustomUuidEntry(
            uuid=configured_info.uuid,
            name=configured_info.name,
            summary=configured_info.description or "",
            unit=configured_info.unit,
            value_type=(
                configured_info.value_type.value
                if isinstance(configured_info.value_type, ValueType)
                else str(configured_info.value_type)
            ),
        )
        uuid_registry.register_characteristic(entry, override)

    def register_custom_service_class(
        self,
        service_class: type[CustomBaseGattService],
        override: bool = False,
    ) -> None:
        """Register a custom service class at runtime.

        Args:
            service_class: The service class to register
            override: Whether to override existing registrations

        Raises:
            TypeError: If cls does not inherit from CustomGattService
            ValueError: If class has no valid _info with UUID

        """
        # Extract UUID from class._info
        configured_info = service_class.get_configured_info()
        if not configured_info or not configured_info.uuid:
            raise ValueError(
                f"Cannot register {service_class.__name__}: class has no valid _info with UUID. "
                "Ensure the class has a _info class attribute with a valid ServiceInfo."
            )
        uuid_str = str(configured_info.uuid)

        # Register the class
        GattServiceRegistry.register_service_class(uuid_str, service_class, override)

        # Register metadata in UUID registry
        entry = CustomUuidEntry(
            uuid=configured_info.uuid,
            name=configured_info.name,
            summary=configured_info.description or "",
        )
        uuid_registry.register_service(entry, override)

    # Async methods for non-blocking operation in async contexts

    async def parse_characteristic_async(
        self,
        uuid: str | BluetoothUUID,
        raw_data: bytes,
        ctx: CharacteristicContext | None = None,
    ) -> CharacteristicData:
        """Parse characteristic data in an async-compatible manner.

        This is an async wrapper that allows characteristic parsing to be used
        in async contexts. The actual parsing is performed synchronously as it's
        a fast, CPU-bound operation that doesn't benefit from async I/O.

        Args:
            uuid: The characteristic UUID (string or BluetoothUUID)
            raw_data: Raw bytes from the characteristic
            ctx: Optional context providing device-level info

        Returns:
            CharacteristicData with parsed value and metadata

        Example:
            ```python
            async with BleakClient(address) as client:
                data = await client.read_gatt_char("2A19")
                result = await translator.parse_characteristic_async("2A19", data)
                print(f"Battery: {result.value}%")
            ```
        """
        # Convert to string for consistency with sync API
        uuid_str = str(uuid) if isinstance(uuid, BluetoothUUID) else uuid

        # Delegate to sync implementation
        return self.parse_characteristic(uuid_str, raw_data, ctx)

    async def parse_characteristics_async(
        self,
        char_data: dict[str, bytes],
        ctx: CharacteristicContext | None = None,
    ) -> dict[str, CharacteristicData]:
        """Parse multiple characteristics in an async-compatible manner.

        This is an async wrapper for batch characteristic parsing. The parsing
        is performed synchronously as it's a fast, CPU-bound operation. This method
        allows batch parsing to be used naturally in async workflows.

        Args:
            char_data: Dictionary mapping UUIDs to raw data bytes
            ctx: Optional context

        Returns:
            Dictionary mapping UUIDs to CharacteristicData results

        Example:
            ```python
            async with BleakClient(address) as client:
                # Read multiple characteristics
                char_data = {}
                for uuid in ["2A19", "2A6E", "2A6F"]:
                    char_data[uuid] = await client.read_gatt_char(uuid)

                # Parse all asynchronously
                results = await translator.parse_characteristics_async(char_data)
                for uuid, result in results.items():
                    print(f"{uuid}: {result.value}")
            ```
        """
        # Delegate directly to sync implementation
        # The sync implementation already handles dependency ordering
        return self.parse_characteristics(char_data, ctx)


# Global instance
BluetoothSIG = BluetoothSIGTranslator()

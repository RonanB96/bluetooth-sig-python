# pylint: disable=too-many-lines # TODO split up Comprehensive translator with many methods
"""Core Bluetooth SIG standards translator functionality."""

from __future__ import annotations

import inspect
import logging
import struct
import typing
from collections.abc import Mapping
from graphlib import TopologicalSorter
from typing import Any, TypeVar, overload

from ..gatt.characteristics import templates
from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.characteristics.registry import CharacteristicRegistry
from ..gatt.exceptions import (
    CharacteristicError,
    CharacteristicParseError,
    MissingDependencyError,
    SpecialValueDetectedError,
)
from ..gatt.services import ServiceName
from ..gatt.services.base import BaseGattService
from ..gatt.services.registry import GattServiceRegistry
from ..gatt.uuid_registry import uuid_registry
from ..types import (
    CharacteristicContext,
    CharacteristicInfo,
    ServiceInfo,
    SIGInfo,
    ValidationResult,
)
from ..types.gatt_enums import CharacteristicName, ValueType
from ..types.uuid import BluetoothUUID

# Type alias for characteristic data in process_services
# Performance: str keys (normalized UUIDs) instead of BluetoothUUID for fast lookups
CharacteristicDataDict = dict[str, Any]

# Type variable for generic characteristic return types
T = TypeVar("T")

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

        Example::

            from bluetooth_sig import BluetoothSIGTranslator

            # Get the singleton instance
            translator = BluetoothSIGTranslator.get_instance()
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

        # Performance: Use str keys (normalized UUIDs) for fast dict lookups
        self._services: dict[str, BaseGattService] = {}

    def __str__(self) -> str:
        """Return string representation of the translator."""
        return "BluetoothSIGTranslator(pure SIG standards)"

    @overload
    def parse_characteristic(
        self,
        char: type[BaseCharacteristic[T]],
        raw_data: bytes | bytearray,
        ctx: CharacteristicContext | None = ...,
    ) -> T: ...

    @overload
    def parse_characteristic(
        self,
        char: str,
        raw_data: bytes | bytearray,
        ctx: CharacteristicContext | None = ...,
    ) -> Any: ...  # noqa: ANN401  # Runtime UUID dispatch cannot be type-safe

    def parse_characteristic(
        self,
        char: str | type[BaseCharacteristic[T]],
        raw_data: bytes | bytearray,
        ctx: CharacteristicContext | None = None,
    ) -> T | Any:  # Runtime UUID dispatch cannot be type-safe
        r"""Parse a characteristic's raw data using Bluetooth SIG standards.

        Args:
            char: Characteristic class (type-safe) or UUID string (not type-safe).
            raw_data: Raw bytes from the characteristic (bytes or bytearray)
            ctx: Optional CharacteristicContext providing device-level info

        Returns:
            Parsed value. Return type is inferred when passing characteristic class.

            - Primitives: ``int``, ``float``, ``str``, ``bool``
            - Dataclasses: ``NavigationData``, ``HeartRateMeasurement``, etc.
            - Special values: ``SpecialValueResult`` (via exception)

        Raises:
            SpecialValueDetectedError: Special sentinel value detected
            CharacteristicParseError: Parse/validation failure

        Example::

            from bluetooth_sig import BluetoothSIGTranslator
            from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

            translator = BluetoothSIGTranslator()

            # Type-safe: pass characteristic class, return type is inferred
            level: int = translator.parse_characteristic(BatteryLevelCharacteristic, b"\\x64")

            # Not type-safe: pass UUID string, returns Any
            value = translator.parse_characteristic("2A19", b"\\x64")

        """
        # Handle characteristic class input (type-safe path)
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            char_instance = char()
            logger.debug("Parsing characteristic class=%s, data_len=%d", char.__name__, len(raw_data))
            try:
                value = char_instance.parse_value(raw_data, ctx)
                logger.debug("Successfully parsed %s: %s", char_instance.name, value)
            except SpecialValueDetectedError as e:
                logger.debug("Special value detected for %s: %s", char_instance.name, e.special_value.meaning)
                raise
            except CharacteristicParseError as e:
                logger.warning("Parse failed for %s: %s", char_instance.name, e)
                raise
            else:
                return value

        # Handle string UUID input (not type-safe path)
        logger.debug("Parsing characteristic UUID=%s, data_len=%d", char, len(raw_data))

        # Get characteristic instance for parsing
        characteristic = CharacteristicRegistry.get_characteristic(char)

        if characteristic:
            logger.debug("Found parser for UUID=%s: %s", char, type(characteristic).__name__)
            # Use the parse_value method which raises exceptions on failure
            try:
                value = characteristic.parse_value(raw_data, ctx)
                logger.debug("Successfully parsed %s: %s", characteristic.name, value)
            except SpecialValueDetectedError as e:
                logger.debug("Special value detected for %s: %s", characteristic.name, e.special_value.meaning)
                raise
            except CharacteristicParseError as e:
                logger.warning("Parse failed for %s: %s", characteristic.name, e)
                raise
            else:
                return value
        else:
            # No parser found, raise an error
            logger.info("No parser available for UUID=%s", char)
            raise CharacteristicParseError(
                message=f"No parser available for characteristic UUID: {char}",
                name="Unknown",
                uuid=BluetoothUUID(char),
                raw_data=bytes(raw_data),
            )

    @overload
    def encode_characteristic(
        self,
        char: type[BaseCharacteristic[T]],
        value: T,
        validate: bool = ...,
    ) -> bytes: ...

    @overload
    def encode_characteristic(
        self,
        char: str,
        value: Any,  # noqa: ANN401  # Runtime UUID dispatch cannot be type-safe
        validate: bool = ...,
    ) -> bytes: ...

    def encode_characteristic(
        self,
        char: str | type[BaseCharacteristic[T]],
        value: T | Any,  # Runtime UUID dispatch cannot be type-safe
        validate: bool = True,
    ) -> bytes:
        r"""Encode a value for writing to a characteristic.

        Args:
            char: Characteristic class (type-safe) or UUID string (not type-safe).
            value: The value to encode. Type is checked when using characteristic class.
            validate: If True, validates the value before encoding (default: True)

        Returns:
            Encoded bytes ready to write to the characteristic

        Raises:
            ValueError: If UUID is invalid, characteristic not found, or value is invalid
            TypeError: If value type doesn't match characteristic's expected type
            CharacteristicEncodeError: If encoding fails

        Example::

            from bluetooth_sig import BluetoothSIGTranslator
            from bluetooth_sig.gatt.characteristics import AlertLevelCharacteristic
            from bluetooth_sig.gatt.characteristics.alert_level import AlertLevel

            translator = BluetoothSIGTranslator()

            # Type-safe: pass characteristic class and typed value
            data: bytes = translator.encode_characteristic(AlertLevelCharacteristic, AlertLevel.HIGH)

            # Not type-safe: pass UUID string
            data = translator.encode_characteristic("2A06", 2)

        """
        # Handle characteristic class input (type-safe path)
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            char_instance = char()
            logger.debug("Encoding characteristic class=%s, value=%s", char.__name__, value)
            try:
                if validate:
                    encoded = char_instance.build_value(value)
                    logger.debug("Successfully encoded %s with validation", char_instance.name)
                else:
                    encoded = char_instance._encode_value(value)  # pylint: disable=protected-access
                    logger.debug("Successfully encoded %s without validation", char_instance.name)
                return bytes(encoded)
            except Exception:
                logger.exception("Encoding failed for %s", char_instance.name)
                raise

        # Handle string UUID input (not type-safe path)
        logger.debug("Encoding characteristic UUID=%s, value=%s", char, value)

        # Get characteristic instance
        characteristic = CharacteristicRegistry.get_characteristic(char)
        if not characteristic:
            raise ValueError(f"No encoder available for characteristic UUID: {char}")

        logger.debug("Found encoder for UUID=%s: %s", char, type(characteristic).__name__)

        # Handle dict input - convert to proper type
        if isinstance(value, dict):
            # Get the expected value type for this characteristic
            value_type = self._get_characteristic_value_type_class(characteristic)
            if value_type and hasattr(value_type, "__init__") and not isinstance(value_type, str):
                try:
                    # Try to construct the dataclass from dict
                    value = value_type(**value)
                    logger.debug("Converted dict to %s", value_type.__name__)
                except (TypeError, ValueError) as e:
                    type_name = getattr(value_type, "__name__", str(value_type))
                    raise TypeError(f"Failed to convert dict to {type_name} for characteristic {char}: {e}") from e

        # Encode using build_value (with validation) or encode_value (without)
        try:
            if validate:
                encoded = characteristic.build_value(value)
                logger.debug("Successfully encoded %s with validation", characteristic.name)
            else:
                encoded = characteristic._encode_value(value)  # pylint: disable=protected-access
                logger.debug("Successfully encoded %s without validation", characteristic.name)
            return bytes(encoded)
        except Exception:
            logger.exception("Encoding failed for %s", characteristic.name)
            raise

    def _get_characteristic_value_type_class(  # pylint: disable=too-many-return-statements,too-many-branches
        self, characteristic: BaseCharacteristic[Any]
    ) -> type[Any] | None:
        """Get the Python type class that a characteristic expects.

        Args:
            characteristic: The characteristic instance

        Returns:
            The type class, or None if it can't be determined

        """
        # Try to infer from decode_value return type annotation (resolve string annotations)
        if hasattr(characteristic, "_decode_value"):
            try:
                # Use get_type_hints to resolve string annotations
                # Need to pass the characteristic's module globals to resolve forward references
                module = inspect.getmodule(characteristic.__class__)
                globalns = getattr(module, "__dict__", {}) if module else {}
                type_hints = typing.get_type_hints(characteristic._decode_value, globalns=globalns)  # pylint: disable=protected-access  # Need to inspect decode method signature
                return_type = type_hints.get("return")
                if return_type and return_type is not type(None):
                    return return_type  # type: ignore[no-any-return]
            except (TypeError, AttributeError, NameError):
                # Fallback to direct signature inspection if type hints fail
                return_type = inspect.signature(characteristic._decode_value).return_annotation  # pylint: disable=protected-access  # Need signature access
                sig = inspect.signature(characteristic._decode_value)  # pylint: disable=protected-access  # Duplicate for clarity
                return_annotation = sig.return_annotation
                if (
                    return_annotation
                    and return_annotation != inspect.Parameter.empty
                    and not isinstance(return_annotation, str)
                ):
                    # Return non-string annotation
                    return return_annotation  # type: ignore[no-any-return]

        # Try to get from _manual_value_type attribute
        # pylint: disable=protected-access  # Need to inspect manual type info
        if hasattr(characteristic, "_manual_value_type"):
            manual_type = characteristic._manual_value_type
            if manual_type and isinstance(manual_type, str) and hasattr(templates, manual_type):
                # Resolve string annotation from templates module
                return getattr(templates, manual_type)  # type: ignore[no-any-return]

        # Try to get from template first
        # pylint: disable=protected-access  # Need to inspect template for type info
        if hasattr(characteristic, "_template") and characteristic._template:
            template = characteristic._template
            # Check if template has a value_type annotation
            if hasattr(template, "__orig_class__"):
                # Extract type from Generic
                args = typing.get_args(template.__orig_class__)
                if args:
                    return args[0]  # type: ignore[no-any-return]

        # For simple types, check info.value_type
        info = characteristic.info
        if info.value_type == ValueType.INT:
            return int
        if info.value_type == ValueType.FLOAT:
            return float
        if info.value_type == ValueType.STRING:
            return str
        if info.value_type == ValueType.BOOL:
            return bool
        if info.value_type == ValueType.BYTES:
            return bytes

        return None

    def get_value_type(self, uuid: str) -> ValueType | None:
        """Get the expected value type for a characteristic.

        Retrieves the ValueType enum indicating what type of data this
        characteristic produces (int, float, string, bytes, etc.).

        Args:
            uuid: The characteristic UUID (16-bit short form or full 128-bit)

        Returns:
            ValueType enum if characteristic is found, None otherwise

        Example::
            Check what type a characteristic returns::

                from bluetooth_sig import BluetoothSIGTranslator

                translator = BluetoothSIGTranslator()
                value_type = translator.get_value_type("2A19")
                print(value_type)  # ValueType.INT

        """
        info = self.get_characteristic_info_by_uuid(uuid)
        return info.value_type if info else None

    def supports(self, uuid: str) -> bool:
        """Check if a characteristic UUID is supported.

        Args:
            uuid: The characteristic UUID to check

        Returns:
            True if the characteristic has a parser/encoder, False otherwise

        Example::
            Check if characteristic is supported::

                from bluetooth_sig import BluetoothSIGTranslator

                translator = BluetoothSIGTranslator()
                if translator.supports("2A19"):
                    result = translator.parse_characteristic("2A19", data)

        """
        try:
            bt_uuid = BluetoothUUID(uuid)
            char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(bt_uuid)
        except (ValueError, TypeError):
            return False
        else:
            return char_class is not None

    def get_characteristic_info_by_uuid(self, uuid: str) -> CharacteristicInfo | None:
        """Get information about a characteristic by UUID.

        Retrieve metadata for a Bluetooth characteristic using its UUID. This includes
        the characteristic's name, description, value type, unit, and properties.

        Args:
            uuid: The characteristic UUID (16-bit short form or full 128-bit)

        Returns:
            [CharacteristicInfo][bluetooth_sig.CharacteristicInfo] with metadata or None if not found

        Example::
            Get battery level characteristic info::

                from bluetooth_sig import BluetoothSIGTranslator

                translator = BluetoothSIGTranslator()
                info = translator.get_characteristic_info_by_uuid("2A19")
                if info:
                    print(f"Name: {info.name}")  # Name: Battery Level

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
        except (TypeError, ValueError, AttributeError):
            # Instantiation may fail if characteristic requires parameters or has missing dependencies
            return None
        else:
            return temp_char.info

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
        except (TypeError, ValueError, AttributeError):
            # Instantiation may fail if characteristic requires parameters or has missing dependencies
            return None
        else:
            return temp_char.info

    def get_service_info_by_name(self, name: str | ServiceName) -> ServiceInfo | None:
        """Get service info by name or enum instead of UUID.

        Args:
            name: Service name string or ServiceName enum

        Returns:
            ServiceInfo if found, None otherwise

        """
        # Convert enum to string value if needed
        name_str = name.value if isinstance(name, ServiceName) else name

        # Use UUID registry for name-based lookup
        try:
            uuid_info = uuid_registry.get_service_info(name_str)
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
        except (TypeError, ValueError, AttributeError):
            # Service instantiation may fail if it requires parameters or has missing data
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
        except (KeyError, ValueError, AttributeError):  # Registry lookups may fail, fall through to service lookup
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
    ) -> dict[str, Any]:
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
            Dictionary mapping UUIDs to parsed values

        Raises:
            ValueError: If circular dependencies are detected
            CharacteristicParseError: If parsing fails for any characteristic

        Example::
            Parse multiple environmental characteristics::

                from bluetooth_sig import BluetoothSIGTranslator

                translator = BluetoothSIGTranslator()
                data = {
                    "2A6E": b"\\x0A\\x00",  # Temperature
                    "2A6F": b"\\x32\\x00",  # Humidity
                }
                try:
                    results = translator.parse_characteristics(data)
                    for uuid, value in results.items():
                        print(f"{uuid}: {value}")
                except CharacteristicParseError as e:
                    print(f"Parse failed: {e}")

        """
        return self._parse_characteristics_batch(char_data, ctx)

    def _parse_characteristics_batch(
        self,
        char_data: dict[str, bytes],
        ctx: CharacteristicContext | None,
    ) -> dict[str, Any]:
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

        results: dict[str, Any] = {}
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
                raise MissingDependencyError(characteristic.name if characteristic else "Unknown", missing_required)

            self._log_optional_dependency_gaps(
                uuid_str,
                uuid_to_optional_deps.get(uuid_str, []),
                results,
                base_context,
            )

            parse_context = self._build_parse_context(base_context, results)

            # Let parse errors propagate to caller
            value = self.parse_characteristic(uuid_str, raw_data, ctx=parse_context)
            results[uuid_str] = value

        logger.debug("Batch parsing complete: %d results", len(results))
        return results

    def _prepare_characteristic_dependencies(
        self, characteristic_data: Mapping[str, bytes]
    ) -> tuple[dict[str, BaseCharacteristic[Any]], dict[str, list[str]], dict[str, list[str]]]:
        """Instantiate characteristics once and collect declared dependencies."""
        # Performance: All dicts use str keys (UUID strings) for O(1) lookups in hot paths
        uuid_to_characteristic: dict[str, BaseCharacteristic[Any]] = {}
        uuid_to_required_deps: dict[str, list[str]] = {}
        uuid_to_optional_deps: dict[str, list[str]] = {}

        for uuid in characteristic_data:
            characteristic = CharacteristicRegistry.get_characteristic(uuid)
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
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("Dependency sorting failed: %s. Using original order.", exc)
            return list(characteristic_data.keys())
        else:
            return sorted_uuids

    def _find_missing_required_dependencies(
        self,
        uuid: str,
        required_deps: list[str],
        results: Mapping[str, Any],
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
                # If it's in results, it was successfully parsed
                continue

            if other_characteristics and dep_uuid in other_characteristics:
                # If it's in context, assume it's available
                continue

            missing.append(dep_uuid)

        if missing:
            logger.debug("Characteristic %s missing required dependencies: %s", uuid, missing)

        return missing

    def _log_optional_dependency_gaps(
        self,
        uuid: str,
        optional_deps: list[str],
        results: Mapping[str, Any],
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
        results: Mapping[str, Any],
    ) -> CharacteristicContext:
        """Construct the context passed to per-characteristic parsers."""
        if base_context is not None:
            return CharacteristicContext(
                device_info=base_context.device_info,
                advertisement=base_context.advertisement,
                other_characteristics=results,
                raw_service=base_context.raw_service,
            )

        return CharacteristicContext(other_characteristics=results)

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
            self.parse_characteristic(uuid, data)
            # Try to get expected_length
            try:
                bt_uuid = BluetoothUUID(uuid)
                char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(bt_uuid)
                expected = char_class.expected_length if char_class else None
            except (ValueError, AttributeError):
                # UUID parsing or class lookup may fail
                expected = None
            return ValidationResult(
                is_valid=True,
                actual_length=len(data),
                expected_length=expected,
                error_message="",
            )
        except (CharacteristicParseError, ValueError, TypeError, struct.error, CharacteristicError) as e:
            # Parsing failed - data format is invalid
            # Try to get expected_length even on failure for better error reporting
            try:
                bt_uuid = BluetoothUUID(uuid)
                char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(bt_uuid)
                expected = char_class.expected_length if char_class else None
            except (ValueError, AttributeError):
                # UUID parsing or class lookup may fail
                expected = None
            return ValidationResult(
                is_valid=False,
                actual_length=len(data),
                expected_length=expected,
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
        uuid_or_name: str,
        cls: type[BaseCharacteristic[Any]],
        info: CharacteristicInfo | None = None,
        override: bool = False,
    ) -> None:
        """Register a custom characteristic class at runtime.

        Args:
            uuid_or_name: The characteristic UUID or name
            cls: The characteristic class to register
            info: Optional CharacteristicInfo with metadata (name, unit, value_type)
            override: Whether to override existing registrations

        Raises:
            TypeError: If cls does not inherit from BaseCharacteristic
            ValueError: If UUID conflicts with existing registration and override=False

        Example::

            from bluetooth_sig import BluetoothSIGTranslator, CharacteristicInfo, ValueType
            from bluetooth_sig.types import BluetoothUUID

            translator = BluetoothSIGTranslator()
            info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789abc"),
                name="Custom Temperature",
                unit="°C",
                value_type=ValueType.FLOAT,
            )
            translator.register_custom_characteristic_class(str(info.uuid), MyCustomCharacteristic, info=info)

        """
        # Register the class
        CharacteristicRegistry.register_characteristic_class(uuid_or_name, cls, override)

        # Register metadata in uuid_registry if provided
        if info:
            uuid_registry.register_characteristic(
                uuid=info.uuid,
                name=info.name or cls.__name__,
                identifier=info.id,
                unit=info.unit,
                value_type=info.value_type,
                override=override,
            )

    def register_custom_service_class(
        self,
        uuid_or_name: str,
        cls: type[BaseGattService],
        info: ServiceInfo | None = None,
        override: bool = False,
    ) -> None:
        """Register a custom service class at runtime.

        Args:
            uuid_or_name: The service UUID or name
            cls: The service class to register
            info: Optional ServiceInfo with metadata (name)
            override: Whether to override existing registrations

        Raises:
            TypeError: If cls does not inherit from BaseGattService
            ValueError: If UUID conflicts with existing registration and override=False

        Example::

            from bluetooth_sig import BluetoothSIGTranslator, ServiceInfo
            from bluetooth_sig.types import BluetoothUUID

            translator = BluetoothSIGTranslator()
            info = ServiceInfo(uuid=BluetoothUUID("12345678-1234-1234-1234-123456789abc"), name="Custom Service")
            translator.register_custom_service_class(str(info.uuid), MyCustomService, info=info)

        """
        # Register the class
        GattServiceRegistry.register_service_class(uuid_or_name, cls, override)

        # Register metadata in uuid_registry if provided
        if info:
            uuid_registry.register_service(
                uuid=info.uuid,
                name=info.name or cls.__name__,
                identifier=info.id,
                override=override,
            )

    # Async methods for non-blocking operation in async contexts

    @overload
    async def parse_characteristic_async(
        self,
        char: type[BaseCharacteristic[T]],
        raw_data: bytes,
        ctx: CharacteristicContext | None = ...,
    ) -> T: ...

    @overload
    async def parse_characteristic_async(
        self,
        char: str | BluetoothUUID,
        raw_data: bytes,
        ctx: CharacteristicContext | None = ...,
    ) -> Any: ...  # noqa: ANN401  # Runtime UUID dispatch cannot be type-safe

    async def parse_characteristic_async(
        self,
        char: str | BluetoothUUID | type[BaseCharacteristic[T]],
        raw_data: bytes,
        ctx: CharacteristicContext | None = None,
    ) -> T | Any:  # Runtime UUID dispatch cannot be type-safe
        """Parse characteristic data in an async-compatible manner.

        This is an async wrapper that allows characteristic parsing to be used
        in async contexts. The actual parsing is performed synchronously as it's
        a fast, CPU-bound operation that doesn't benefit from async I/O.

        Args:
            char: Characteristic class (type-safe) or UUID string/BluetoothUUID (not type-safe).
            raw_data: Raw bytes from the characteristic
            ctx: Optional context providing device-level info

        Returns:
            Parsed value. Return type is inferred when passing characteristic class.

        Raises:
            SpecialValueDetectedError: Special sentinel value detected
            CharacteristicParseError: Parse/validation failure

        Example::

            async with BleakClient(address) as client:
                data = await client.read_gatt_char("2A19")

                # Type-safe: pass characteristic class
                from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

                level: int = await translator.parse_characteristic_async(BatteryLevelCharacteristic, data)

                # Not type-safe: pass UUID string
                value = await translator.parse_characteristic_async("2A19", data)

        """
        # Handle characteristic class input (type-safe path)
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            return self.parse_characteristic(char, raw_data, ctx)

        # Convert to string for consistency with sync API
        uuid_str = str(char) if isinstance(char, BluetoothUUID) else char

        # Delegate to sync implementation
        return self.parse_characteristic(uuid_str, raw_data, ctx)

    async def parse_characteristics_async(
        self,
        char_data: dict[str, bytes],
        ctx: CharacteristicContext | None = None,
    ) -> dict[str, Any]:
        """Parse multiple characteristics in an async-compatible manner.

        This is an async wrapper for batch characteristic parsing. The parsing
        is performed synchronously as it's a fast, CPU-bound operation. This method
        allows batch parsing to be used naturally in async workflows.

        Args:
            char_data: Dictionary mapping UUIDs to raw data bytes
            ctx: Optional context

        Returns:
            Dictionary mapping UUIDs to parsed values

        Example::

            async with BleakClient(address) as client:
                # Read multiple characteristics
                char_data = {}
                for uuid in ["2A19", "2A6E", "2A6F"]:
                    char_data[uuid] = await client.read_gatt_char(uuid)

                # Parse all asynchronously
                results = await translator.parse_characteristics_async(char_data)
                for uuid, value in results.items():
                    print(f"{uuid}: {value}")
        """
        # Delegate directly to sync implementation
        # The sync implementation already handles dependency ordering
        return self.parse_characteristics(char_data, ctx)

    @overload
    async def encode_characteristic_async(
        self,
        char: type[BaseCharacteristic[T]],
        value: T,
        validate: bool = ...,
    ) -> bytes: ...

    @overload
    async def encode_characteristic_async(
        self,
        char: str | BluetoothUUID,
        value: Any,  # noqa: ANN401  # Runtime UUID dispatch cannot be type-safe
        validate: bool = ...,
    ) -> bytes: ...

    async def encode_characteristic_async(
        self,
        char: str | BluetoothUUID | type[BaseCharacteristic[T]],
        value: T | Any,  # Runtime UUID dispatch cannot be type-safe
        validate: bool = True,
    ) -> bytes:
        """Encode characteristic value in an async-compatible manner.

        This is an async wrapper that allows characteristic encoding to be used
        in async contexts. The actual encoding is performed synchronously as it's
        a fast, CPU-bound operation that doesn't benefit from async I/O.

        Args:
            char: Characteristic class (type-safe) or UUID string/BluetoothUUID (not type-safe).
            value: The value to encode (dataclass, dict, or primitive).
                   Type is checked when using characteristic class.
            validate: If True, validates before encoding (default: True)

        Returns:
            Encoded bytes ready to write

        Example::

            async with BleakClient(address) as client:
                from bluetooth_sig.gatt.characteristics import AlertLevelCharacteristic
                from bluetooth_sig.gatt.characteristics.alert_level import AlertLevel

                # Type-safe: pass characteristic class
                data: bytes = await translator.encode_characteristic_async(AlertLevelCharacteristic, AlertLevel.HIGH)
                await client.write_gatt_char(str(AlertLevelCharacteristic().uuid), data)

                # Not type-safe: pass UUID string
                data = await translator.encode_characteristic_async("2A06", 2)
                await client.write_gatt_char("2A06", data)
        """
        # Handle characteristic class input (type-safe path)
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            return self.encode_characteristic(char, value, validate)

        # Convert to string for consistency with sync API
        uuid_str = str(char) if isinstance(char, BluetoothUUID) else char

        # Delegate to sync implementation
        return self.encode_characteristic(uuid_str, value, validate)

    def create_value(self, uuid: str, **kwargs: Any) -> Any:  # noqa: ANN401
        """Create a properly typed value instance for a characteristic.

        This is a convenience method that constructs the appropriate dataclass
        or value type for a characteristic, which can then be passed to
        encode_characteristic() or used directly.

        Args:
            uuid: The characteristic UUID
            **kwargs: Field values for the characteristic's type

        Returns:
            Properly typed value instance

        Raises:
            ValueError: If UUID is invalid or characteristic not found
            TypeError: If kwargs don't match the characteristic's expected fields

        Example::
            Create complex characteristic values::

                from bluetooth_sig import BluetoothSIGTranslator

                translator = BluetoothSIGTranslator()

                # Create acceleration data
                accel = translator.create_value("2C1D", x_axis=1.5, y_axis=0.5, z_axis=9.8)

                # Encode and write
                data = translator.encode_characteristic("2C1D", accel)
                await client.write_gatt_char("2C1D", data)

        """
        # Get characteristic instance
        characteristic = CharacteristicRegistry.get_characteristic(uuid)
        if not characteristic:
            raise ValueError(f"No characteristic found for UUID: {uuid}")

        # Get the value type
        value_type = self._get_characteristic_value_type_class(characteristic)

        if not value_type:
            # For simple types, just return the single value if provided
            if len(kwargs) == 1:
                return next(iter(kwargs.values()))
            raise ValueError(
                f"Cannot determine value type for characteristic {uuid}. "
                "Try passing a dict to encode_characteristic() instead."
            )

        # Handle simple primitive types
        if value_type in (int, float, str, bool, bytes):
            if len(kwargs) == 1:
                value = next(iter(kwargs.values()))
                if not isinstance(value, value_type):
                    type_name = getattr(value_type, "__name__", str(value_type))
                    raise TypeError(f"Expected {type_name}, got {type(value).__name__}")
                return value
            type_name = getattr(value_type, "__name__", str(value_type))
            raise TypeError(f"Simple type {type_name} expects a single value")

        # Construct complex type from kwargs
        try:
            return value_type(**kwargs)
        except (TypeError, ValueError) as e:
            type_name = getattr(value_type, "__name__", str(value_type))
            raise TypeError(f"Failed to create {type_name} for characteristic {uuid}: {e}") from e


# Global instance
BluetoothSIG = BluetoothSIGTranslator()

"""Core Bluetooth SIG standards translator — thin composition facade.

This module provides the public ``BluetoothSIGTranslator`` class, which
delegates all work to five focused components:

* :class:`~.query.CharacteristicQueryEngine` — read-only metadata lookups
* :class:`~.parser.CharacteristicParser` — single + batch parse
* :class:`~.encoder.CharacteristicEncoder` — encode, validate, create_value
* :class:`~.registration.RegistrationManager` — custom class registration
* :class:`~.service_manager.ServiceManager` — discovered-service lifecycle

The facade preserves every public method signature, ``@overload``
decorator, async wrapper, and the singleton pattern from the original
monolithic implementation.
"""

from __future__ import annotations

from typing import Any, TypeVar, overload

from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.services import ServiceName
from ..gatt.services.base import BaseGattService
from ..types import (
    CharacteristicContext,
    CharacteristicInfo,
    ServiceInfo,
    SIGInfo,
    ValidationResult,
)
from ..types.gatt_enums import CharacteristicName, ValueType
from ..types.uuid import BluetoothUUID
from .encoder import CharacteristicEncoder
from .parser import CharacteristicParser
from .query import CharacteristicQueryEngine
from .registration import RegistrationManager
from .service_manager import CharacteristicDataDict, ServiceManager

# Re-export for backward compatibility
__all__ = ["BluetoothSIGTranslator", "BluetoothSIG", "CharacteristicDataDict"]

T = TypeVar("T")


class BluetoothSIGTranslator:  # pylint: disable=too-many-public-methods
    """Pure Bluetooth SIG standards translator for characteristic and service interpretation.

    This class provides the primary API surface for Bluetooth SIG standards translation,
    covering characteristic parsing, service discovery, UUID resolution, and registry
    management.

    Singleton Pattern:
        This class is implemented as a singleton to provide a global registry for
        custom characteristics and services. Access the singleton instance using
        ``BluetoothSIGTranslator.get_instance()`` or the module-level ``translator`` variable.

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
        if self.__class__._instance_lock:
            return
        self.__class__._instance_lock = True

        # Compose delegates
        self._query = CharacteristicQueryEngine()
        self._parser = CharacteristicParser()
        self._encoder = CharacteristicEncoder(self._parser)
        self._registration = RegistrationManager()
        self._services = ServiceManager()

    def __str__(self) -> str:
        """Return string representation of the translator."""
        return "BluetoothSIGTranslator(pure SIG standards)"

    # -------------------------------------------------------------------------
    # Parse
    # -------------------------------------------------------------------------

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
    ) -> T | Any:
        r"""Parse a characteristic's raw data using Bluetooth SIG standards.

        Args:
            char: Characteristic class (type-safe) or UUID string (not type-safe).
            raw_data: Raw bytes from the characteristic (bytes or bytearray)
            ctx: Optional CharacteristicContext providing device-level info

        Returns:
            Parsed value. Return type is inferred when passing characteristic class.

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
        return self._parser.parse_characteristic(char, raw_data, ctx)

    def parse_characteristics(
        self,
        char_data: dict[str, bytes],
        ctx: CharacteristicContext | None = None,
    ) -> dict[str, Any]:
        r"""Parse multiple characteristics at once with dependency-aware ordering.

        Args:
            char_data: Dictionary mapping UUIDs to raw data bytes
            ctx: Optional CharacteristicContext used as the starting context

        Returns:
            Dictionary mapping UUIDs to parsed values

        Raises:
            ValueError: If circular dependencies are detected
            CharacteristicParseError: If parsing fails for any characteristic

        Example::

            from bluetooth_sig import BluetoothSIGTranslator

            translator = BluetoothSIGTranslator()
            data = {
                "2A6E": b"\\x0A\\x00",  # Temperature
                "2A6F": b"\\x32\\x00",  # Humidity
            }
            try:
                results = translator.parse_characteristics(data)
            except CharacteristicParseError as e:
                print(f"Parse failed: {e}")

        """
        return self._parser.parse_characteristics(char_data, ctx)

    # -------------------------------------------------------------------------
    # Encode
    # -------------------------------------------------------------------------

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
        value: T | Any,
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
        return self._encoder.encode_characteristic(char, value, validate)

    def validate_characteristic_data(self, uuid: str, data: bytes) -> ValidationResult:
        """Validate characteristic data format against SIG specifications.

        Args:
            uuid: The characteristic UUID
            data: Raw data bytes to validate

        Returns:
            ValidationResult with validation details

        """
        return self._encoder.validate_characteristic_data(uuid, data)

    def create_value(self, uuid: str, **kwargs: Any) -> Any:  # noqa: ANN401
        """Create a properly typed value instance for a characteristic.

        Args:
            uuid: The characteristic UUID
            **kwargs: Field values for the characteristic's type

        Returns:
            Properly typed value instance

        Raises:
            ValueError: If UUID is invalid or characteristic not found
            TypeError: If kwargs don't match the characteristic's expected fields

        Example::

            from bluetooth_sig import BluetoothSIGTranslator

            translator = BluetoothSIGTranslator()
            accel = translator.create_value("2C1D", x_axis=1.5, y_axis=0.5, z_axis=9.8)
            data = translator.encode_characteristic("2C1D", accel)

        """
        return self._encoder.create_value(uuid, **kwargs)

    # -------------------------------------------------------------------------
    # Query / Info
    # -------------------------------------------------------------------------

    def get_value_type(self, uuid: str) -> ValueType | None:
        """Get the expected value type for a characteristic.

        Args:
            uuid: The characteristic UUID (16-bit short form or full 128-bit)

        Returns:
            ValueType enum if characteristic is found, None otherwise

        """
        return self._query.get_value_type(uuid)

    def supports(self, uuid: str) -> bool:
        """Check if a characteristic UUID is supported.

        Args:
            uuid: The characteristic UUID to check

        Returns:
            True if the characteristic has a parser/encoder, False otherwise

        """
        return self._query.supports(uuid)

    def get_characteristic_info_by_uuid(self, uuid: str) -> CharacteristicInfo | None:
        """Get information about a characteristic by UUID.

        Args:
            uuid: The characteristic UUID (16-bit short form or full 128-bit)

        Returns:
            CharacteristicInfo with metadata or None if not found

        """
        return self._query.get_characteristic_info_by_uuid(uuid)

    def get_characteristic_uuid_by_name(self, name: CharacteristicName) -> BluetoothUUID | None:
        """Get the UUID for a characteristic name enum.

        Args:
            name: CharacteristicName enum

        Returns:
            Characteristic UUID or None if not found

        """
        return self._query.get_characteristic_uuid_by_name(name)

    def get_service_uuid_by_name(self, name: str | ServiceName) -> BluetoothUUID | None:
        """Get the UUID for a service name or enum.

        Args:
            name: Service name or enum

        Returns:
            Service UUID or None if not found

        """
        return self._query.get_service_uuid_by_name(name)

    def get_characteristic_info_by_name(self, name: CharacteristicName) -> CharacteristicInfo | None:
        """Get characteristic info by enum name.

        Args:
            name: CharacteristicName enum

        Returns:
            CharacteristicInfo if found, None otherwise

        """
        return self._query.get_characteristic_info_by_name(name)

    def get_service_info_by_name(self, name: str | ServiceName) -> ServiceInfo | None:
        """Get service info by name or enum.

        Args:
            name: Service name string or ServiceName enum

        Returns:
            ServiceInfo if found, None otherwise

        """
        return self._query.get_service_info_by_name(name)

    def get_service_info_by_uuid(self, uuid: str) -> ServiceInfo | None:
        """Get information about a service by UUID.

        Args:
            uuid: The service UUID

        Returns:
            ServiceInfo with metadata or None if not found

        """
        return self._query.get_service_info_by_uuid(uuid)

    def list_supported_characteristics(self) -> dict[str, str]:
        """List all supported characteristics with their names and UUIDs.

        Returns:
            Dictionary mapping characteristic names to UUIDs

        """
        return self._query.list_supported_characteristics()

    def list_supported_services(self) -> dict[str, str]:
        """List all supported services with their names and UUIDs.

        Returns:
            Dictionary mapping service names to UUIDs

        """
        return self._query.list_supported_services()

    def get_characteristics_info_by_uuids(self, uuids: list[str]) -> dict[str, CharacteristicInfo | None]:
        """Get information about multiple characteristics by UUID.

        Args:
            uuids: List of characteristic UUIDs

        Returns:
            Dictionary mapping UUIDs to CharacteristicInfo (or None if not found)

        """
        return self._query.get_characteristics_info_by_uuids(uuids)

    def get_service_characteristics(self, service_uuid: str) -> list[str]:
        """Get the characteristic UUIDs associated with a service.

        Args:
            service_uuid: The service UUID

        Returns:
            List of characteristic UUIDs for this service

        """
        return self._query.get_service_characteristics(service_uuid)

    def get_sig_info_by_name(self, name: str) -> SIGInfo | None:
        """Get Bluetooth SIG information for a characteristic or service by name.

        Args:
            name: Characteristic or service name

        Returns:
            CharacteristicInfo or ServiceInfo if found, None otherwise

        """
        return self._query.get_sig_info_by_name(name)

    def get_sig_info_by_uuid(self, uuid: str) -> SIGInfo | None:
        """Get Bluetooth SIG information for a UUID.

        Args:
            uuid: UUID string (with or without dashes)

        Returns:
            CharacteristicInfo or ServiceInfo if found, None otherwise

        """
        return self._query.get_sig_info_by_uuid(uuid)

    # -------------------------------------------------------------------------
    # Service lifecycle
    # -------------------------------------------------------------------------

    def process_services(self, services: dict[str, dict[str, CharacteristicDataDict]]) -> None:
        """Process discovered services and their characteristics.

        Args:
            services: Dictionary of service UUIDs to their characteristics

        """
        self._services.process_services(services)

    def get_service_by_uuid(self, uuid: str) -> BaseGattService | None:
        """Get a service instance by UUID.

        Args:
            uuid: The service UUID

        Returns:
            Service instance if found, None otherwise

        """
        return self._services.get_service_by_uuid(uuid)

    @property
    def discovered_services(self) -> list[BaseGattService]:
        """Get list of discovered service instances.

        Returns:
            List of discovered service instances

        """
        return self._services.discovered_services

    def clear_services(self) -> None:
        """Clear all discovered services."""
        self._services.clear_services()

    # -------------------------------------------------------------------------
    # Registration
    # -------------------------------------------------------------------------

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
            translator.register_custom_characteristic_class(str(info.uuid), MyCustomChar, info=info)

        """
        self._registration.register_custom_characteristic_class(uuid_or_name, cls, info, override)

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
            info = ServiceInfo(uuid=BluetoothUUID("12345678-..."), name="Custom Service")
            translator.register_custom_service_class(str(info.uuid), MyService, info=info)

        """
        self._registration.register_custom_service_class(uuid_or_name, cls, info, override)

    # -------------------------------------------------------------------------
    # Async wrappers
    # -------------------------------------------------------------------------

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
    ) -> T | Any:
        """Parse characteristic data in an async-compatible manner.

        Args:
            char: Characteristic class (type-safe) or UUID string/BluetoothUUID.
            raw_data: Raw bytes from the characteristic
            ctx: Optional context providing device-level info

        Returns:
            Parsed value. Return type is inferred when passing characteristic class.

        Raises:
            SpecialValueDetectedError: Special sentinel value detected
            CharacteristicParseError: Parse/validation failure

        """
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            return self._parser.parse_characteristic(char, raw_data, ctx)

        uuid_str = str(char) if isinstance(char, BluetoothUUID) else char
        return self._parser.parse_characteristic(uuid_str, raw_data, ctx)

    async def parse_characteristics_async(
        self,
        char_data: dict[str, bytes],
        ctx: CharacteristicContext | None = None,
    ) -> dict[str, Any]:
        """Parse multiple characteristics in an async-compatible manner.

        Args:
            char_data: Dictionary mapping UUIDs to raw data bytes
            ctx: Optional context

        Returns:
            Dictionary mapping UUIDs to parsed values

        """
        return self._parser.parse_characteristics(char_data, ctx)

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
        value: T | Any,
        validate: bool = True,
    ) -> bytes:
        """Encode characteristic value in an async-compatible manner.

        Args:
            char: Characteristic class (type-safe) or UUID string/BluetoothUUID.
            value: The value to encode.
            validate: If True, validates before encoding (default: True)

        Returns:
            Encoded bytes ready to write

        """
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            return self._encoder.encode_characteristic(char, value, validate)

        uuid_str = str(char) if isinstance(char, BluetoothUUID) else char
        return self._encoder.encode_characteristic(uuid_str, value, validate)


# Global instance
BluetoothSIG = BluetoothSIGTranslator()

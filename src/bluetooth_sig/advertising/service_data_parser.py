"""Service data parser for BLE advertisements.

Parses service data payloads using registered GATT characteristic classes,
enabling automatic interpretation of SIG-standard and custom characteristics
from advertisement service data.

This bridges the advertising and GATT layers:
- Advertisement Service Data (UUID → raw bytes) is extracted by AdvertisingPDUParser
- This module maps UUIDs to characteristic classes via CharacteristicRegistry
- Characteristic classes decode bytes using their standard parse_value() method
"""

from __future__ import annotations

from typing import Any

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.types.context import CharacteristicContext, DeviceInfo
from bluetooth_sig.types.uuid import BluetoothUUID


class ServiceDataParser:
    r"""Parser for service data from BLE advertisements.

    Uses registered GATT characteristic classes to decode service data payloads.
    Both SIG-standard and custom-registered characteristics are supported via
    the unified CharacteristicRegistry.

    Example:
        parser = ServiceDataParser()

        # Parse all service data from an advertisement
        service_data = {BluetoothUUID("2A6E"): b'\xE8\x03'}  # Temperature
        results = parser.parse(service_data)
        # results = {BluetoothUUID("2A6E"): 10.0}  # Parsed temperature in °C

        # Parse with context
        ctx = ServiceDataParser.build_context(
            device_name="MySensor",
            device_address="AA:BB:CC:DD:EE:FF",
        )
        results = parser.parse(service_data, ctx)

    """

    # Cache characteristic instances by UUID for performance
    _char_cache: dict[str, BaseCharacteristic[Any]] = {}

    @classmethod
    def get_characteristic(cls, uuid: BluetoothUUID) -> BaseCharacteristic[Any] | None:
        """Get a cached characteristic instance for the given UUID.

        Args:
            uuid: The characteristic UUID to look up

        Returns:
            Characteristic instance if UUID is registered, None otherwise

        """
        normalized = uuid.normalized
        if normalized in cls._char_cache:
            return cls._char_cache[normalized]

        char_instance = CharacteristicRegistry.get_characteristic(uuid)
        if char_instance is not None:
            cls._char_cache[normalized] = char_instance

        return char_instance

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the characteristic instance cache (for testing)."""
        cls._char_cache.clear()

    @staticmethod
    def build_context(
        device_name: str = "",
        device_address: str = "",
        manufacturer_data: dict[int, bytes] | None = None,
        service_uuids: list[BluetoothUUID] | None = None,
        advertisement: bytes = b"",
        validate: bool = True,
    ) -> CharacteristicContext:
        """Build a CharacteristicContext from advertisement information.

        Args:
            device_name: Device local name from advertisement
            device_address: Device MAC address
            manufacturer_data: Manufacturer data from advertisement
            service_uuids: Service UUIDs from advertisement
            advertisement: Raw advertisement bytes
            validate: Whether to perform validation during parsing

        Returns:
            CharacteristicContext populated with device info

        """
        return CharacteristicContext(
            device_info=DeviceInfo(
                name=device_name,
                address=device_address,
                manufacturer_data=manufacturer_data or {},
                service_uuids=service_uuids or [],
            ),
            advertisement=advertisement,
            validate=validate,
        )

    def parse(
        self,
        service_data: dict[BluetoothUUID, bytes],
        ctx: CharacteristicContext | None = None,
    ) -> dict[BluetoothUUID, Any]:  # noqa: ANN401 - dynamic types from runtime lookup
        """Parse service data using registered characteristic classes.

        Iterates through service data entries, looking up each UUID in the
        CharacteristicRegistry. For recognised UUIDs, calls parse_value()
        to decode the payload. Unrecognised UUIDs are skipped.

        Use ctx.validate=False to suppress validation exceptions.

        Args:
            service_data: Mapping of service UUID to raw payload bytes
            ctx: Optional context for parsing

        Returns:
            Mapping of UUID to parsed values (only includes recognised UUIDs)

        Raises:
            CharacteristicParseError: If parsing fails (when validate=True)
            SpecialValueDetected: If a special value sentinel is detected

        """
        results: dict[BluetoothUUID, Any] = {}

        for uuid, data in service_data.items():
            char_instance = self.get_characteristic(uuid)
            if char_instance is None:
                continue

            results[uuid] = char_instance.parse_value(data, ctx)

        return results

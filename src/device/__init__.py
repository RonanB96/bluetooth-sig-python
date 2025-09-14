"""Device class for grouping BLE device services, characteristics, encryption, and advertiser data.

This module provides a high-level Device abstraction that groups all services,
characteristics, encryption requirements, and advertiser data for a BLE device.
It integrates with the BluetoothSIGTranslator for parsing while providing a
unified view of device state.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol

from bluetooth_sig.gatt.context import CharacteristicContext, DeviceInfo
from bluetooth_sig.gatt.services import GattServiceRegistry
from bluetooth_sig.gatt.services.base import BaseGattService
from bluetooth_sig.types import CharacteristicDataProtocol


class SIGTranslatorProtocol(Protocol):
    """Protocol defining the interface needed by Device class from a SIG translator."""

    @abstractmethod
    def parse_characteristics(
        self, char_data: dict[str, bytes], ctx: CharacteristicContext | None = None
    ) -> dict[str, Any]:
        """Parse multiple characteristics at once.

        Args:
            char_data: Dictionary mapping UUIDs to raw data bytes
            ctx: Optional base CharacteristicContext

        Returns:
            Dictionary mapping UUIDs to parsed characteristic data
        """
        ...


class UnknownService(BaseGattService):
    """Generic service for unknown/unsupported service UUIDs."""

    @classmethod
    def get_expected_characteristics(cls) -> dict[str, type]:
        """No expected characteristics for unknown services."""
        return {}

    @classmethod
    def get_required_characteristics(cls) -> dict[str, type]:
        """No required characteristics for unknown services."""
        return {}


@dataclass
class DeviceService:
    """Represents a service on a device with its characteristics."""

    service: BaseGattService
    characteristics: dict[str, CharacteristicDataProtocol] = field(default_factory=dict)


@dataclass
class DeviceEncryption:
    """Encryption requirements and status for the device."""

    requires_authentication: bool = False
    requires_encryption: bool = False
    encryption_level: str | None = None
    security_mode: int | None = None
    key_size: int | None = None


@dataclass
class DeviceAdvertiserData:
    """Parsed advertiser data from device discovery."""

    raw_data: bytes
    local_name: str | None = None
    manufacturer_data: dict[int, bytes] = field(default_factory=dict)
    service_uuids: list[str] = field(default_factory=list)
    tx_power: int | None = None
    rssi: int | None = None
    flags: int | None = None


class Device:
    """High-level representation of a BLE device with all its services and data.

    This class provides a unified view of a BLE device's services, characteristics,
    encryption requirements, and advertiser data. It serves as a pure SIG standards
    translator abstraction, not a BLE connection manager.

    The Device class integrates with BluetoothSIGTranslator for characteristic parsing
    while maintaining device-level context and relationships between services and
    characteristics.
    """

    def __init__(self, address: str, translator: SIGTranslatorProtocol) -> None:
        """Initialize a Device instance.

        Args:
            address: The device MAC address or identifier
            translator: BluetoothSIGTranslator instance for parsing characteristics
        """
        self.address = address
        self.translator = translator
        self.name: str | None = None
        self.services: dict[str, DeviceService] = {}
        self.encryption = DeviceEncryption()
        self.advertiser_data: DeviceAdvertiserData | None = None

    def __str__(self) -> str:
        """Return string representation of the device."""
        service_count = len(self.services)
        char_count = sum(
            len(service.characteristics) for service in self.services.values()
        )
        return f"Device({self.address}, name={self.name}, {service_count} services, {char_count} characteristics)"

    def add_service(self, service_uuid: str, characteristics: dict[str, bytes]) -> None:
        """Add a service with its characteristics to the device.

        Args:
            service_uuid: The service UUID
            characteristics: Dictionary mapping characteristic UUIDs to raw data bytes
        """
        # Get the service class for this UUID
        service_class = GattServiceRegistry.get_service_class(service_uuid)
        if not service_class:
            # Create a generic service if no specific class found
            service: BaseGattService = UnknownService()
        else:
            service = service_class()

        # Create device context for parsing
        device_info = DeviceInfo(
            address=self.address,
            name=self.name,
            manufacturer_data=self.advertiser_data.manufacturer_data
            if self.advertiser_data
            else None,
            service_uuids=self.advertiser_data.service_uuids
            if self.advertiser_data
            else None,
        )

        base_ctx = CharacteristicContext(device_info=device_info)

        # Parse all characteristics for this service
        parsed_characteristics = self.translator.parse_characteristics(
            characteristics, ctx=base_ctx
        )

        # Update encryption requirements based on parsed characteristics
        for char_data in parsed_characteristics.values():
            self.update_encryption_requirements(char_data)

        # Create device service instance
        device_service = DeviceService(
            service=service, characteristics=parsed_characteristics
        )

        # Store the service
        self.services[service_uuid] = device_service

    def parse_advertiser_data(self, raw_data: bytes) -> None:
        """Parse and store advertiser data for the device.

        Args:
            raw_data: Raw advertisement data bytes
        """
        # BLE Advertisement Data Format:
        # Each AD structure: [Length (1 byte)] [AD Type (1 byte)] [AD Data (Length-1 bytes)]
        # Common AD Types:
        # 0x01: Flags
        # 0x02: Incomplete List of 16-bit Service UUIDs
        # 0x03: Complete List of 16-bit Service UUIDs
        # 0x08: Shortened Local Name
        # 0x09: Complete Local Name
        # 0x0A: Tx Power Level
        # 0xFF: Manufacturer Specific Data

        manufacturer_data = {}
        service_uuids = []
        local_name = None
        tx_power = None
        flags = None

        i = 0
        while i < len(raw_data):
            if i + 1 >= len(raw_data):
                break

            length = raw_data[i]
            if length == 0 or i + length + 1 > len(raw_data):
                break

            ad_type = raw_data[i + 1]
            ad_data = raw_data[i + 2 : i + length + 1]

            if ad_type == 0x01 and len(ad_data) >= 1:  # Flags
                flags = ad_data[0]
            elif ad_type == 0x02 or ad_type == 0x03:  # Service UUIDs (16-bit)
                # Parse 16-bit UUIDs (little endian)
                for j in range(0, len(ad_data), 2):
                    if j + 1 < len(ad_data):
                        uuid_short = ad_data[j] | (ad_data[j + 1] << 8)
                        service_uuids.append(f"{uuid_short:04X}")
            elif ad_type == 0x08 or ad_type == 0x09:  # Local Name
                try:
                    local_name = ad_data.decode("utf-8")
                except UnicodeDecodeError:
                    local_name = ad_data.hex()
            elif ad_type == 0x0A and len(ad_data) >= 1:  # Tx Power
                tx_power = int.from_bytes(ad_data[:1], byteorder="little", signed=True)
            elif ad_type == 0xFF and len(ad_data) >= 2:  # Manufacturer Data
                company_id = ad_data[0] | (ad_data[1] << 8)
                manufacturer_data[company_id] = ad_data[2:]

            i += length + 1

        self.advertiser_data = DeviceAdvertiserData(
            raw_data=raw_data,
            local_name=local_name,
            manufacturer_data=manufacturer_data,
            service_uuids=service_uuids,
            tx_power=tx_power,
            flags=flags,
        )

        # Update device name from advertisement if available
        if local_name and not self.name:
            self.name = local_name

    def get_characteristic_data(
        self, service_uuid: str, char_uuid: str
    ) -> CharacteristicDataProtocol | None:
        """Get parsed characteristic data for a specific characteristic.

        Args:
            service_uuid: The service UUID
            char_uuid: The characteristic UUID

        Returns:
            CharacteristicData if found, None otherwise
        """
        service = self.services.get(service_uuid)
        if service:
            return service.characteristics.get(char_uuid)
        return None

    def update_encryption_requirements(
        self, char_data: CharacteristicDataProtocol
    ) -> None:
        """Update encryption requirements based on characteristic parsing results.

        Args:
            char_data: Parsed characteristic data that may indicate encryption needs
        """
        # Check if characteristic requires encryption based on properties
        if hasattr(char_data, "properties") and char_data.properties:
            if (
                "encrypt-read" in char_data.properties
                or "encrypt-write" in char_data.properties
            ):
                self.encryption.requires_encryption = True
            if (
                "auth-read" in char_data.properties
                or "auth-write" in char_data.properties
            ):
                self.encryption.requires_authentication = True

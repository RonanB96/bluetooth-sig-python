"""Resolve advertised service UUIDs to GATT service classes.

Maps advertised service UUIDs (from AD types 0x02-0x07) to GATT service classes.
This bridges advertising discovery with GATT service discovery, allowing
callers to pre-plan which characteristics to read after connecting.

Based on Bluetooth SIG Core Specification Supplement for advertising data
AD Type categories.
"""

from __future__ import annotations

from bluetooth_sig.gatt.services.base import BaseGattService
from bluetooth_sig.gatt.services.registry import GattServiceRegistry
from bluetooth_sig.types.uuid import BluetoothUUID


class ResolvedService:
    """Information about a resolved advertised service.

    Attributes:
        uuid: The service UUID from the advertisement.
        service_class: The GATT service class, or None if not in registry.
        name: Human-readable service name.
        is_sig_defined: Whether this is a SIG-defined service.

    """

    __slots__ = ("is_sig_defined", "name", "service_class", "uuid")

    def __init__(
        self,
        uuid: BluetoothUUID,
        service_class: type[BaseGattService] | None,
        name: str,
        *,
        is_sig_defined: bool,
    ) -> None:
        """Initialise resolved service.

        Args:
            uuid: The service UUID.
            service_class: The GATT service class, or None.
            name: Human-readable service name.
            is_sig_defined: Whether this is a SIG-defined service.

        """
        self.uuid = uuid
        self.service_class = service_class
        self.name = name
        self.is_sig_defined = is_sig_defined

    def __repr__(self) -> str:
        """Return string representation."""
        class_name = self.service_class.__name__ if self.service_class else "None"
        return f"ResolvedService(uuid={self.uuid}, service_class={class_name}, name={self.name!r})"


class AdvertisingServiceResolver:
    """Resolves advertised service UUIDs to GATT service classes.

    Maps service UUIDs advertised in BLE advertisements to their
    corresponding GATT service classes from the registry.

    Example::
        resolver = AdvertisingServiceResolver()

        # Resolve a single UUID
        resolved = resolver.resolve(BluetoothUUID("0000180f-0000-1000-8000-00805f9b34fb"))
        if resolved.service_class:
            print(f"Found service: {resolved.name}")

        # Resolve multiple UUIDs from advertisement
        service_uuids = [
            BluetoothUUID("0000180f-0000-1000-8000-00805f9b34fb"),  # Battery Service
            BluetoothUUID("0000180d-0000-1000-8000-00805f9b34fb"),  # Heart Rate Service
        ]
        resolved_services = resolver.resolve_all(service_uuids)

    """

    def resolve(self, uuid: BluetoothUUID | str) -> ResolvedService:
        """Resolve a single service UUID to its GATT service class.

        Args:
            uuid: The service UUID to resolve.

        Returns:
            ResolvedService with service class if found, or None if unknown.

        """
        if isinstance(uuid, str):
            uuid = BluetoothUUID(uuid)

        service_class = GattServiceRegistry.get_service_class_by_uuid(uuid)

        if service_class is not None:
            # Get name from the service class
            name = service_class.__name__
            # Check if it's SIG-defined (uses SIG base UUID)
            is_sig_defined = uuid.is_sig_service()
            return ResolvedService(
                uuid=uuid,
                service_class=service_class,
                name=name,
                is_sig_defined=is_sig_defined,
            )

        # Unknown service - return with None service_class
        return ResolvedService(
            uuid=uuid,
            service_class=None,
            name=f"Unknown Service ({uuid})",
            is_sig_defined=False,
        )

    def resolve_all(
        self,
        uuids: list[BluetoothUUID] | list[str],
    ) -> list[ResolvedService]:
        """Resolve multiple service UUIDs.

        Args:
            uuids: List of service UUIDs to resolve.

        Returns:
            List of ResolvedService objects, one per input UUID.

        """
        return [self.resolve(uuid) for uuid in uuids]

    def get_known_services(
        self,
        uuids: list[BluetoothUUID] | list[str],
    ) -> list[ResolvedService]:
        """Get only the services that have known GATT service classes.

        Filters out unknown services from the result.

        Args:
            uuids: List of service UUIDs to check.

        Returns:
            List of ResolvedService objects for known services only.

        """
        return [resolved for resolved in self.resolve_all(uuids) if resolved.service_class is not None]

    def get_sig_services(
        self,
        uuids: list[BluetoothUUID] | list[str],
    ) -> list[ResolvedService]:
        """Get only the SIG-defined services from the list.

        Filters to return only services with SIG-assigned 16-bit UUIDs.

        Args:
            uuids: List of service UUIDs to check.

        Returns:
            List of ResolvedService objects for SIG-defined services only.

        """
        return [resolved for resolved in self.resolve_all(uuids) if resolved.is_sig_defined]

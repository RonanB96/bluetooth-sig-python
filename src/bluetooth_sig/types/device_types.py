"""Device-related data types for BLE device management."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Literal, Union

import msgspec

from .advertising import AdvertisementData
from .uuid import BluetoothUUID

# Type alias for scanning mode
ScanningMode = Literal["active", "passive"]

# Type alias for scan detection callback: receives ScannedDevice as it's discovered
# Uses Union[] instead of | for Python 3.9 compatibility with GenericAlias
ScanDetectionCallback = Callable[["ScannedDevice"], Union[Awaitable[None], None]]

# Type alias for scan filter function: returns True if device matches
ScanFilterFunc = Callable[["ScannedDevice"], bool]

# Circular dependency: gatt.characteristics.base imports from types,
# and this module needs to reference those classes for type hints.
if TYPE_CHECKING:
    from ..gatt.characteristics.base import BaseCharacteristic
    from ..gatt.services.base import BaseGattService


class ScannedDevice(msgspec.Struct, kw_only=True):
    """Minimal wrapper for a device discovered during BLE scanning.

    Attributes:
        address: Bluetooth MAC address or platform-specific identifier
        name: OS-provided device name (may be None)
        advertisement_data: Complete parsed advertising data (includes rssi, manufacturer_data, etc.)

    """

    address: str
    name: str | None = None
    advertisement_data: AdvertisementData | None = None


class DeviceService(msgspec.Struct, kw_only=True):
    r"""Represents a service on a device with its characteristics.

    The characteristics dictionary stores BaseCharacteristic instances.
    Access parsed data via characteristic.last_parsed property.

    This provides a single source of truth: BaseCharacteristic instances
    maintain their own last_parsed CharacteristicData.

    Example::

        # After discover_services() and read()
        service = device.services["0000180f..."]  # Battery Service
        battery_char = service.characteristics["00002a19..."]  # BatteryLevelCharacteristic instance

        # Access last parsed result
        if battery_char.last_parsed:
            print(f"Battery: {battery_char.last_parsed.value}%")

        # Or decode new data
        parsed_value = battery_char.decode_value(raw_data)
    """

    service: BaseGattService
    characteristics: dict[str, BaseCharacteristic] = msgspec.field(default_factory=dict)


class DeviceEncryption(msgspec.Struct, kw_only=True):
    """Encryption requirements and status for the device."""

    requires_authentication: bool = False
    requires_encryption: bool = False
    encryption_level: str = ""
    security_mode: int = 0
    key_size: int = 0


class ScanFilter(msgspec.Struct, kw_only=True):
    """Filter configuration for BLE scanning operations.

    All filters are optional. When multiple filters are specified, a device must
    match ALL filters (AND logic) to be included in results.

    For OR logic across different filter types, perform multiple scans or use
    a custom `filter_func`.

    Attributes:
        service_uuids: Only include devices advertising these service UUIDs.
            On some platforms (macOS), this filtering happens at the OS level
            for better efficiency. UUIDs should be in standard string format
            (e.g., "0000180f-0000-1000-8000-00805f9b34fb" or short "180f").
        addresses: Only include devices with these MAC addresses.
            Useful for reconnecting to known devices. Case-insensitive matching.
        names: Only include devices with names containing any of these substrings.
            Case-insensitive partial matching. Device must have a name to match.
        rssi_threshold: Only include devices with RSSI >= this value (in dBm).
            Typical values: -30 (very close), -60 (nearby), -90 (far).
        filter_func: Custom filter function for complex matching logic.
            Called with each ScannedDevice, return True to include.
            Runs after all other filters.

    Example::

        # Find Heart Rate monitors nearby
        filters = ScanFilter(
            service_uuids=["180d"],  # Heart Rate Service
            rssi_threshold=-70,
        )

        # Find specific known devices
        filters = ScanFilter(
            addresses=["AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"],
        )


        # Custom filter for manufacturer-specific criteria
        def my_filter(device: ScannedDevice) -> bool:
            if device.advertisement_data is None:
                return False
            # Check for specific manufacturer ID
            mfr_data = device.advertisement_data.ad_structures.core.manufacturer_data
            return 0x004C in mfr_data  # Apple devices


        filters = ScanFilter(filter_func=my_filter)

    """

    service_uuids: list[str] | None = None
    addresses: list[str] | None = None
    names: list[str] | None = None
    rssi_threshold: int | None = None
    filter_func: ScanFilterFunc | None = None

    def _passes_address_filter(self, device: ScannedDevice) -> bool:
        """Check if device passes the address filter (No filter means passes filter)."""
        addresses = self.addresses
        if addresses is None:
            return True
        return any(addr.upper() == device.address.upper() for addr in addresses)  # pylint: disable=not-an-iterable

    def _passes_name_filter(self, device: ScannedDevice) -> bool:
        """Check if device passes the name filter (No filter means passes filter)."""
        names = self.names
        if names is None:
            return True
        if device.name is None:
            return False
        device_name_lower = device.name.lower()
        return any(name.lower() in device_name_lower for name in names)  # pylint: disable=not-an-iterable

    def _passes_rssi_filter(self, device: ScannedDevice) -> bool:
        """Check if device passes the RSSI threshold (No filter means passes filter)."""
        if self.rssi_threshold is None:
            return True
        if device.advertisement_data is None or device.advertisement_data.rssi is None:
            return False
        return device.advertisement_data.rssi >= self.rssi_threshold

    def _passes_service_uuid_filter(self, device: ScannedDevice) -> bool:
        """Check if device passes the service UUID filter (No filter means passes filter)."""
        service_uuids = self.service_uuids
        if service_uuids is None:
            return True
        if device.advertisement_data is None:
            return False
        advertised = device.advertisement_data.ad_structures.core.service_uuids
        # Normalise UUIDs for comparison using BluetoothUUID
        normalized_filters = {BluetoothUUID(uuid).normalized for uuid in service_uuids}  # pylint: disable=not-an-iterable
        normalized_advertised = {uuid.normalized for uuid in advertised}
        return bool(normalized_filters & normalized_advertised)

    def matches(self, device: ScannedDevice) -> bool:
        """Check if a device passes all specified filters.

        Args:
            device: The scanned device to check

        Returns:
            True if device passes all filters, False otherwise

        """
        # Check each filter criterion
        if not self._passes_address_filter(device):
            return False
        if not self._passes_name_filter(device):
            return False
        if not self._passes_rssi_filter(device):
            return False
        if not self._passes_service_uuid_filter(device):
            return False

        # Check custom filter function
        filter_func = self.filter_func
        if filter_func is not None:
            if not filter_func(device):  # pylint: disable=not-callable
                return False

        return True


class ScanOptions(msgspec.Struct, kw_only=True):
    """Configuration options for scanning operations.

    Combines filter criteria with scan behavior settings.

    Attributes:
        timeout: Maximum scan duration in seconds. None for indefinite (use with callbacks).
        filters: Filter criteria for discovered devices. None for no filtering.
        scanning_mode: 'active' sends scan requests for additional data (default),
            'passive' only listens to advertisements (saves power, not supported on macOS).
        return_first_match: If True with filters, stop scanning on first matching device.
            Useful for targeted device discovery (faster than full scan + filter).
        adapter: Backend-specific adapter identifier (e.g., "hci0" for BlueZ on Linux).
            None uses the default adapter.

    Example::

        # Quick scan for a specific device type
        options = ScanOptions(
            timeout=10.0,
            filters=ScanFilter(service_uuids=["180d"]),
            return_first_match=True,
        )

        # Passive background scan
        options = ScanOptions(
            timeout=30.0,
            scanning_mode="passive",
        )

    """

    timeout: float | None = 5.0
    filters: ScanFilter | None = None
    scanning_mode: ScanningMode = "active"
    return_first_match: bool = False
    adapter: str | None = None

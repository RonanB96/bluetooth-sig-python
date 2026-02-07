"""Final composed advertising data result types."""

from __future__ import annotations

from typing import Any

import msgspec

from bluetooth_sig.types.advertising.ad_structures import (
    AdvertisingDataStructures,
    ExtendedAdvertisingData,
)
from bluetooth_sig.types.company import ManufacturerData
from bluetooth_sig.types.uuid import BluetoothUUID


class AdvertisingData(msgspec.Struct, kw_only=True):
    """Complete BLE advertising data with device information and metadata.

    Attributes:
        raw_data: Raw bytes from the advertising packet
        ad_structures: Parsed AD structures organized by category
        extended: Extended advertising data (BLE 5.0+)
        rssi: Received signal strength indicator in dBm
    """

    raw_data: bytes
    ad_structures: AdvertisingDataStructures = msgspec.field(default_factory=AdvertisingDataStructures)
    extended: ExtendedAdvertisingData = msgspec.field(default_factory=ExtendedAdvertisingData)
    rssi: int | None = None

    @property
    def is_extended_advertising(self) -> bool:
        """Check if this advertisement uses extended advertising."""
        return bool(self.extended.extended_payload) or bool(self.extended.auxiliary_packets)

    @property
    def total_payload_size(self) -> int:
        """Get total payload size including extended data."""
        base_size = len(self.raw_data)
        if self.extended.extended_payload:
            base_size += len(self.extended.extended_payload)
        for aux_packet in self.extended.auxiliary_packets:
            base_size += len(aux_packet.payload)
        return base_size


class AdvertisementData(msgspec.Struct, kw_only=True):
    """Complete parsed advertisement with PDU structures and interpreted data.

    This is the unified result from Device.update_advertisement(), containing
    both low-level AD structures and high-level vendor-specific interpretation.

    The interpreted_data field is typed as Any to maintain msgspec.Struct compatibility
    while supporting generic vendor-specific result types at runtime.

    Attributes:
        ad_structures: Parsed AD structures (manufacturer_data, service_data, etc.)
        interpreted_data: Vendor-specific typed result (e.g., sensor readings), or None
        interpreter_name: Name of the interpreter used (e.g., "BTHome", "Xiaomi"), or None
        rssi: Received signal strength indicator in dBm

    Example::
        # Using connection manager (recommended)
        ad_data = BleakConnectionManager.convert_advertisement(bleak_advertisement)
        result = device.update_advertisement(ad_data)

        # Access low-level AD structures
        print(result.ad_structures.core.manufacturer_data)  # {0x0499: b'...'}
        print(result.ad_structures.properties.flags)

        # Access vendor-specific interpreted data
        if result.interpreted_data:
            print(f"Interpreter: {result.interpreter_name}")
            print(f"Temperature: {result.interpreted_data.temperature}")

    """

    ad_structures: AdvertisingDataStructures = msgspec.field(default_factory=AdvertisingDataStructures)
    interpreted_data: Any = None
    interpreter_name: str | None = None
    rssi: int | None = None

    @property
    def manufacturer_data(self) -> dict[int, ManufacturerData]:
        """Convenience accessor for manufacturer data (company_id → ManufacturerData)."""
        return self.ad_structures.core.manufacturer_data

    @property
    def service_data(self) -> dict[BluetoothUUID, bytes]:
        """Convenience accessor for service data (UUID → payload)."""
        return self.ad_structures.core.service_data

    @property
    def local_name(self) -> str:
        """Convenience accessor for device local name."""
        return self.ad_structures.core.local_name

    @property
    def has_interpretation(self) -> bool:
        """Check if vendor-specific interpretation was applied."""
        return self.interpreted_data is not None

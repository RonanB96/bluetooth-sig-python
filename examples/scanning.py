#!/usr/bin/env python3
"""Example: Comprehensive BLE device scanning with auto-parsing.

Scans for nearby BLE devices and automatically parses:
- Service UUIDs (resolved to known GATT services)
- Service Data (parsed using SIG characteristic definitions)
- Manufacturer Data (company names and vendor-specific parsing)
- Advertising payloads (via registered interpreters)

This example combines discovery, service resolution, and payload parsing
into a single comprehensive scanning tool.
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig.advertising import (
    AdvertisingServiceResolver,
    ManufacturerData,
    PayloadContext,
    parse_advertising_payloads,
)
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.types.uuid import BluetoothUUID

# Create resolver instance for service lookups
_service_resolver = AdvertisingServiceResolver()


def format_bytes(data: bytes, max_len: int = 20) -> str:
    """Format bytes as hex string with length indication for long data."""
    hex_str = data.hex()
    if len(data) > max_len:
        return f"{hex_str[: max_len * 2]}... ({len(data)} bytes)"
    return hex_str


def parse_service_data_value(uuid: BluetoothUUID, payload: bytes) -> str | None:
    """Try to parse service data using characteristic registry."""
    char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(uuid)
    if char_class is None:
        return None

    try:
        char_instance = char_class()
        parsed = char_instance.parse_value(payload)
        return f"{char_class.__name__}: {parsed}"
    except Exception:
        return None


async def scan_devices(timeout: float = 10.0) -> None:
    """Scan for BLE devices and parse all available advertising data."""
    print("=" * 70)
    print("BLE Device Scanner with Auto-Parsing")
    print("=" * 70)

    try:
        from bleak import BleakScanner
        from bleak.backends.scanner import AdvertisementData as BleakAdvertisementData
    except ImportError:
        print("Bleak not installed. Install with: pip install bleak")
        return

    print(f"\nScanning for BLE devices ({timeout:.0f} seconds)...\n")

    # Collect all advertisements (keeps latest per address)
    devices_seen: dict[str, tuple[str | None, BleakAdvertisementData]] = {}

    def detection_callback(device: object, advertisement_data: BleakAdvertisementData) -> None:
        """Callback for each advertisement received."""
        from bleak.backends.device import BLEDevice

        ble_device: BLEDevice = device  # type: ignore[assignment]
        devices_seen[ble_device.address] = (ble_device.name, advertisement_data)

    scanner = BleakScanner(detection_callback=detection_callback)
    await scanner.start()
    await asyncio.sleep(timeout)
    await scanner.stop()

    if not devices_seen:
        print("No devices found")
        return

    print(f"Found {len(devices_seen)} device(s)\n")
    print("-" * 70)

    # Statistics
    stats = {
        "with_manufacturer_data": 0,
        "with_service_data": 0,
        "with_service_uuids": 0,
        "parsed_service_data": 0,
        "parsed_payloads": 0,
    }
    parsed_results: list[tuple[str, str | None, object]] = []

    # Process each device
    for address, (name, adv) in sorted(devices_seen.items()):
        display_name = name or "Unknown"
        print(f"\n{display_name} [{address}]")
        print(f"   RSSI: {adv.rssi} dBm")

        # Show local name if different from device name
        if adv.local_name and adv.local_name != name:
            print(f"   Local Name: {adv.local_name}")

        # TX Power
        if adv.tx_power is not None:
            print(f"   TX Power: {adv.tx_power} dBm")

        # Service UUIDs (advertised services)
        if adv.service_uuids:
            stats["with_service_uuids"] += 1
            print(f"   Service UUIDs ({len(adv.service_uuids)}):")
            for uuid_str in adv.service_uuids:
                try:
                    uuid = BluetoothUUID(uuid_str)
                    resolved = _service_resolver.resolve(uuid)
                    if resolved.service_class:
                        print(f"      • {uuid.short_form}: {resolved.name}")
                    else:
                        print(f"      • {uuid.short_form}")
                except Exception:
                    print(f"      • {uuid_str}")

        # Manufacturer Data
        if adv.manufacturer_data:
            stats["with_manufacturer_data"] += 1
            print(f"   Manufacturer Data ({len(adv.manufacturer_data)} entries):")
            for company_id, payload in adv.manufacturer_data.items():
                mfr_data = ManufacturerData.from_id_and_payload(company_id, payload)
                print(f"      • {mfr_data.company.name}: {format_bytes(mfr_data.payload)}")

        # Service Data - try to parse each one
        service_data_uuids: dict[BluetoothUUID, bytes] = {}
        if adv.service_data:
            stats["with_service_data"] += 1
            print(f"   Service Data ({len(adv.service_data)} entries):")
            for uuid_str, payload in adv.service_data.items():
                try:
                    uuid = BluetoothUUID(uuid_str)
                    service_data_uuids[uuid] = payload

                    # Try to parse as SIG characteristic
                    parsed = parse_service_data_value(uuid, payload)
                    if parsed:
                        print(f"      • {uuid.short_form}: {parsed}")
                        stats["parsed_service_data"] += 1
                    else:
                        print(f"      • {uuid.short_form}: {format_bytes(payload)}")
                except Exception:
                    print(f"      • {uuid_str}: {format_bytes(payload)}")

        # Try auto-parsing via registered interpreters
        if adv.manufacturer_data or service_data_uuids:
            context = PayloadContext(
                mac_address=address,
                rssi=adv.rssi or 0,
                timestamp=time.time(),
            )

            results = parse_advertising_payloads(
                manufacturer_data=adv.manufacturer_data or {},
                service_data=service_data_uuids,
                context=context,
            )

            if results:
                successful = [r for r in results if r.is_success]
                if successful:
                    print(f"   Auto-Parsed ({len(successful)} results):")
                    for result in successful:
                        print(f"      {result.data}")
                        parsed_results.append((address, name, result.data))
                        stats["parsed_payloads"] += 1

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total devices:            {len(devices_seen)}")
    print(f"With manufacturer data:   {stats['with_manufacturer_data']}")
    print(f"With service data:        {stats['with_service_data']}")
    print(f"With service UUIDs:       {stats['with_service_uuids']}")
    print(f"Parsed service data:      {stats['parsed_service_data']}")
    print(f"Auto-parsed payloads:     {stats['parsed_payloads']}")

    if parsed_results:
        print("\nSuccessfully Parsed Payloads:")
        for address, name, data in parsed_results:
            display = name or address
            print(f"   • {display}: {data}")


async def main() -> None:
    """Run the comprehensive BLE scanner."""
    await scan_devices(timeout=10.0)


if __name__ == "__main__":
    asyncio.run(main())

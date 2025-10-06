#!/usr/bin/env python3
"""Data parsing utilities for BLE examples.

This module provides common data parsing and display functions for BLE
characteristics.
"""

from __future__ import annotations

from typing import Any

from bluetooth_sig import BluetoothSIGTranslator


def short_uuid(uuid: str) -> str:
    """Normalize a UUID (full or short) to a short 16-bit uppercase string.

    Examples:
      '00002a19-0000-1000-8000-00805f9b34fb' -> '2A19'
      '2a19' -> '2A19'
    """
    if not uuid:
        return ""
    u = str(uuid).replace("-", "").lower()
    if len(u) == 32:
        return u[4:8].upper()
    if len(u) >= 4:
        return u[-4:].upper()
    return u.upper()


async def parse_and_display_results(
    raw_results: dict[str, tuple[bytes, float]], library_name: str = "BLE Library"
) -> dict[str, Any]:
    """Parse raw BLE data and display results using bluetooth_sig.

    Args:
        raw_results: Dict mapping UUID to (raw_data, read_time)
        library_name: Name of BLE library for display

    Returns:
        Dict of parsed results
    """
    translator = BluetoothSIGTranslator()
    parsed_results: dict[str, Any] = {}

    print(f"\n📊 {library_name} Results with SIG Parsing:")
    print("=" * 50)

    for uuid_short, (raw_data, read_time) in raw_results.items():
        try:
            # Parse with bluetooth_sig (connection-agnostic)
            result = translator.parse_characteristic(uuid_short, raw_data)

            if result.parse_success:
                unit_str = f" {result.unit}" if result.unit else ""
                print(f"   ✅ {result.name}: {result.value}{unit_str}")
                parsed_results[uuid_short] = {
                    "name": result.name,
                    "value": result.value,
                    "unit": result.unit,
                    "read_time": read_time,
                    "raw_data": raw_data,
                }
            else:
                print(f"   ❌ {uuid_short}: Parse failed - {result.error_message}")

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"   💥 {uuid_short}: Exception - {e}")

    return parsed_results


def _display_raw_data(_char_uuid_short: str, raw_bytes: bytes) -> None:
    """Display raw characteristic data in hex format."""
    if raw_bytes:
        hex_data = " ".join(f"{b:02X}" for b in raw_bytes)
        print(f"     Raw: [{hex_data}]")
    else:
        print("     Raw: [Empty]")


def _parse_characteristic_data(
    char_uuid_short: str, raw_data: bytes, translator: BluetoothSIGTranslator
) -> dict[str, Any] | None:
    """Parse characteristic data and return structured results."""
    try:
        result = translator.parse_characteristic(char_uuid_short, raw_data)

        if result.parse_success:
            return {
                "uuid": char_uuid_short,
                "name": result.name,
                "value": result.value,
                "unit": result.unit,
                "properties": getattr(result, "properties", []),
                "raw_data": raw_data,
            }

        print(f"     ❌ Parse failed: {result.error_message}")
        return None

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"     💥 Parsing exception: {e}")
        return None


def _perform_sig_analysis(results: dict[str, dict[str, Any]], _translator: BluetoothSIGTranslator) -> None:
    """Perform comprehensive SIG analysis on collected results."""
    print("\n🧬 Bluetooth SIG Analysis:")
    print("=" * 50)

    if not results:
        print("   ℹ️  No valid data to analyze")
        return

    print(f"   📊 Analyzed {len(results)} characteristics")

    # Group by service (first two characters of UUID)
    services: dict[str, list[str]] = {}
    for uuid in results:
        service_prefix = uuid[:2]
        if service_prefix not in services:
            services[service_prefix] = []
        services[service_prefix].append(uuid)

    print(f"   🏷️  Found {len(services)} service types:")
    for service_prefix, char_list in services.items():
        print(f"     {service_prefix}xx: {len(char_list)} characteristics")

    # Show data types found
    data_types: set[str] = set()
    for char_data in results.values():
        if "value" in char_data and char_data["value"] is not None:
            data_types.add(type(char_data["value"]).__name__)

    if data_types:
        print(f"   📈 Data types: {', '.join(sorted(data_types))}")

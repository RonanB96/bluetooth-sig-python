#!/usr/bin/env python3
"""Data parsing utilities for BLE examples.

This module provides common data parsing and display functions for BLE
characteristics.
"""

from __future__ import annotations

from typing import Any

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.data_types import CharacteristicData
from bluetooth_sig.types.uuid import BluetoothUUID
from examples.utils.models import ReadResult


async def parse_and_display_results(
    raw_results: dict[str, ReadResult], library_name: str = "BLE Library"
) -> dict[str, ReadResult]:
    """Parse raw BLE data and display results using bluetooth_sig.

    Args:
        raw_results: Dict mapping UUID to (raw_data, read_time)
        library_name: Name of BLE library for display

    Returns:
        Dict of parsed results

    """
    translator = BluetoothSIGTranslator()

    print(f"\n📊 {library_name} Results with SIG Parsing:")
    print("=" * 50)

    for uuid_short, read_result in raw_results.items():
        try:
            parse_outcome = translator.parse_characteristic(uuid_short, read_result.raw_data)
            read_result.parsed = parse_outcome
            if parse_outcome.parse_success:
                unit_str = f" {parse_outcome.unit}" if parse_outcome.unit else ""
                print(f"   ✅ {parse_outcome.name}: {parse_outcome.value}{unit_str}")
            else:
                read_result.error = parse_outcome.error_message
                print(f"   ❌ {uuid_short}: Parse failed - {parse_outcome.error_message}")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            read_result.error = str(exc)
            print(f"   💥 {uuid_short}: Exception - {exc}")

    return raw_results


# Legacy tuple-based parsing helper removed. Examples now use the
# ReadResult dataclass and the canonical async/sync parsing helpers
# (`parse_and_display_results` / `parse_and_display_results_sync`). This
# avoids maintaining a second, divergent representation of read results
# and eliminates soft typing in example APIs.


def parse_and_display_results_sync(
    raw_results: dict[str, ReadResult], library_name: str = "BLE Library"
) -> dict[str, ReadResult]:
    """Synchronous wrapper equivalent to :func:`parse_and_display_results`.

    This helper is intended for examples and integration code that run in
    synchronous contexts (e.g. SimplePyBLE helpers). It uses the same
    canonical parsing core so behaviour and output are identical.
    """
    # Reuse the async implementation but keep a convenient synchronous
    # wrapper for sync examples. The sync wrapper performs the same
    # mutation on ReadResult instances.
    translator = BluetoothSIGTranslator()

    print(f"\n📊 {library_name} Results with SIG Parsing:")
    print("=" * 50)

    for uuid_short, read_result in raw_results.items():
        try:
            parse_outcome = translator.parse_characteristic(uuid_short, read_result.raw_data)
            read_result.parsed = parse_outcome
            if parse_outcome.parse_success:
                unit_str = f" {parse_outcome.unit}" if parse_outcome.unit else ""
                print(f"   ✅ {parse_outcome.name}: {parse_outcome.value}{unit_str}")
            else:
                read_result.error = parse_outcome.error_message
                print(f"   ❌ {uuid_short}: Parse failed - {parse_outcome.error_message}")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            read_result.error = str(exc)
            print(f"   💥 {uuid_short}: Exception - {exc}")

    return raw_results


def _display_raw_data(_char_uuid_short: str, raw_bytes: bytes) -> None:
    """Display raw characteristic data in hex format."""
    if raw_bytes:
        hex_data = " ".join(f"{b:02X}" for b in raw_bytes)
        print(f"     Raw: [{hex_data}]")
    else:
        print("     Raw: [Empty]")


def display_parsed_results(
    results: dict[str, dict[str, Any] | CharacteristicData] | dict[BluetoothUUID, CharacteristicData],
    title: str = "Parsed Results",
) -> None:
    """Display parsed results when callers already have parsed output.

    Accepts either the structured dict format produced by
    :func:`parse_and_display_results` or a mapping from
    :class:`BluetoothUUID` to :class:`CharacteristicData`.
    """
    print(f"\n🔎 {title}")
    print("=" * 50)

    # Normalize BluetoothUUID keys to short-string form if necessary
    normalized: dict[str, dict[str, Any] | CharacteristicData] = {}
    for key, value in results.items():
        if isinstance(key, BluetoothUUID):
            key_str = str(key)
        else:
            key_str = str(key)
        normalized[key_str] = value

    for uuid_short, result in normalized.items():
        # CharacteristicData objects (from translator.parse_characteristic)
        if isinstance(result, CharacteristicData):
            if result.parse_success:
                unit_str = f" {result.unit}" if result.unit else ""
                print(f"   ✅ {result.name}: {result.value}{unit_str}")
            else:
                print(f"   ❌ {uuid_short}: Parse failed")

        # Structured dict output matching parse_and_display_results
        elif isinstance(result, dict):
            if result.get("error"):
                print(f"   ❌ {uuid_short}: {result.get('error')}")
            else:
                name = result.get("name", uuid_short)
                value_val = result.get("value")
                unit_val = result.get("unit")
                unit_str = f" {unit_val}" if unit_val else ""
                print(f"   ✅ {name}: {value_val}{unit_str}")
        # All expected value shapes are handled above. If a caller provides
        # an unexpected value type the behaviour is undefined — prefer a
        # strict failure mode to masking bugs.


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

#!/usr/bin/env python3
"""Data parsing utilities for BLE examples.

This module provides common data parsing and display functions for BLE
characteristics.
"""

from __future__ import annotations

from typing import Any

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.exceptions import (
    CharacteristicParseError,
    SpecialValueDetectedError,
)
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
            value = translator.parse_characteristic(uuid_short, read_result.raw_data)
            read_result.parsed = value
            # Get characteristic info for display
            char_info = translator.get_characteristic_info_by_uuid(uuid_short)
            name = char_info.name if char_info else uuid_short
            unit = char_info.unit if char_info else ""
            unit_str = f" {unit}" if unit else ""
            print(f"   ✅ {name}: {value}{unit_str}")
        except SpecialValueDetectedError as e:
            read_result.parsed = e.special_value
            print(f"   ⚠️ {e.name}: {e.special_value.meaning}")
        except CharacteristicParseError as e:
            read_result.error = str(e)
            print(f"   ❌ {uuid_short}: Parse failed - {e}")
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
            value = translator.parse_characteristic(uuid_short, read_result.raw_data)
            read_result.parsed = value
            # Get characteristic info for display
            char_info = translator.get_characteristic_info_by_uuid(uuid_short)
            name = char_info.name if char_info else uuid_short
            unit = char_info.unit if char_info else ""
            unit_str = f" {unit}" if unit else ""
            print(f"   ✅ {name}: {value}{unit_str}")
        except SpecialValueDetectedError as e:
            read_result.parsed = e.special_value
            print(f"   ⚠️ {e.name}: {e.special_value.meaning}")
        except CharacteristicParseError as e:
            read_result.error = str(e)
            print(f"   ❌ {uuid_short}: Parse failed - {e}")
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
    results: dict[str, dict[str, Any] | Any] | dict[BluetoothUUID, Any],
    title: str = "Parsed Results",
) -> None:
    """Display parsed results when callers already have parsed output.

    Accepts either the structured dict format produced by
    :func:`parse_and_display_results` or a mapping from
    :class:`BluetoothUUID` to parsed values.
    """
    print(f"\n🔎 {title}")
    print("=" * 50)

    # Normalize BluetoothUUID keys to short-string form if necessary
    normalized: dict[str, dict[str, Any] | Any] = {}
    for key, value in results.items():
        key_str = str(key)
        normalized[key_str] = value

    for uuid_short, result in normalized.items():
        # Structured dict output matching parse_and_display_results
        if isinstance(result, dict):
            if result.get("error"):
                print(f"   ❌ {uuid_short}: {result.get('error')}")
            else:
                name = result.get("name", uuid_short)
                value_val = result.get("value")
                unit_val = result.get("unit")
                unit_str = f" {unit_val}" if unit_val else ""
                print(f"   ✅ {name}: {value_val}{unit_str}")
        else:
            # Raw parsed value - display directly
            print(f"   ✅ {uuid_short}: {result}")


def _parse_characteristic_data(
    char_uuid_short: str, raw_data: bytes, translator: BluetoothSIGTranslator
) -> dict[str, Any] | None:
    """Parse characteristic data and return structured results."""
    try:
        value = translator.parse_characteristic(char_uuid_short, raw_data)
        char_info = translator.get_characteristic_info_by_uuid(char_uuid_short)
        return {
            "uuid": char_uuid_short,
            "name": char_info.name if char_info else char_uuid_short,
            "value": value,
            "unit": char_info.unit if char_info else "",
            "properties": [],
            "raw_data": raw_data,
        }
    except SpecialValueDetectedError as e:
        return {
            "uuid": char_uuid_short,
            "name": e.name,
            "value": e.special_value,
            "unit": "",
            "properties": [],
            "raw_data": raw_data,
        }
    except CharacteristicParseError as e:
        print(f"     ❌ Parse failed: {e}")
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

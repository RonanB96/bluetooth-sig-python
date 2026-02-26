#!/usr/bin/env python3
"""GATT implementation coverage report.

Compares YAML-defined UUIDs against Python implementations for
characteristics, services, and descriptors. Prints a summary with
gap details. Exit code is always 0 — this is informational, not a gate.

Usage:
    python scripts/gatt_coverage_report.py
    python scripts/gatt_coverage_report.py --verbose   # list every gap
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure src is importable when running as a script
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root / "src"))

from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry  # noqa: E402
from bluetooth_sig.gatt.descriptors import DescriptorRegistry  # noqa: E402
from bluetooth_sig.gatt.services.registry import GattServiceRegistry  # noqa: E402
from bluetooth_sig.gatt.uuid_registry import uuid_registry  # noqa: E402
from bluetooth_sig.types.uuid import BluetoothUUID  # noqa: E402


def _format_line(category: str, yaml_count: int, impl_count: int) -> str:
    pct = (impl_count / yaml_count * 100) if yaml_count else 0.0
    gap = yaml_count - impl_count
    return f"  {category:<20s} {impl_count:>4d}/{yaml_count:<4d}  ({pct:5.1f}%)  {gap:>4d} gaps"


def main(*, verbose: bool = False) -> None:
    """Print GATT coverage report."""
    # --- Characteristics ---
    char_yaml = uuid_registry._characteristics
    char_yaml_uuids = set(char_yaml.keys())
    char_reg = CharacteristicRegistry.get_instance()
    char_impl = {u.normalized for u in char_reg._get_sig_classes_map()}
    char_gaps = char_yaml_uuids - char_impl

    # --- Services ---
    svc_yaml = uuid_registry._services
    svc_yaml_uuids = set(svc_yaml.keys())
    svc_reg = GattServiceRegistry.get_instance()
    svc_impl = {u.normalized for u in svc_reg._get_sig_classes_map()}
    svc_gaps = svc_yaml_uuids - svc_impl

    # --- Descriptors ---
    desc_yaml = uuid_registry._descriptors
    desc_yaml_uuids = set(desc_yaml.keys())
    desc_impl = {BluetoothUUID(u).normalized for u in DescriptorRegistry._registry}
    desc_gaps = desc_yaml_uuids - desc_impl

    # --- Report ---
    print()
    print("=" * 60)
    print("  GATT Implementation Coverage Report")
    print("=" * 60)
    print(f"  {'Category':<20s} {'Impl':>4s}/{'YAML':<4s}  {'%':>6s}  {'Gaps':>4s}")
    print("-" * 60)
    print(_format_line("Characteristics", len(char_yaml_uuids), len(char_impl)))
    print(_format_line("Services", len(svc_yaml_uuids), len(svc_impl)))
    print(_format_line("Descriptors", len(desc_yaml_uuids), len(desc_impl)))
    print("=" * 60)

    if verbose:
        if char_gaps:
            print(f"\nUnimplemented characteristics ({len(char_gaps)}):")
            for name in sorted(char_yaml[u].name for u in char_gaps if u in char_yaml):
                print(f"  - {name}")

        if svc_gaps:
            print(f"\nUnimplemented services ({len(svc_gaps)}):")
            for name in sorted(svc_yaml[u].name for u in svc_gaps if u in svc_yaml):
                print(f"  - {name}")

        if desc_gaps:
            print(f"\nUnimplemented descriptors ({len(desc_gaps)}):")
            for name in sorted(desc_yaml[u].name for u in desc_gaps if u in desc_yaml):
                print(f"  - {name}")

    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GATT coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="List every gap")
    args = parser.parse_args()
    main(verbose=args.verbose)

"""GATT orphan detection — implementations without YAML entries.

Catches the reverse of the existing completeness tests: if a characteristic,
service, or descriptor class exists in code but has no corresponding YAML
UUID entry, that is a real bug (the class can never be discovered by UUID).
These tests gate PRs by failing on orphan classes.

For informational coverage reporting (YAML → implementation gap counts),
see ``scripts/gatt_coverage_report.py``.
"""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.gatt.descriptors import DescriptorRegistry
from bluetooth_sig.gatt.services.registry import GattServiceRegistry
from bluetooth_sig.gatt.uuid_registry import uuid_registry
from bluetooth_sig.types.uuid import BluetoothUUID


class TestOrphanCharacteristics:
    """Detect characteristic classes with no YAML UUID entry."""

    def test_all_implemented_characteristics_exist_in_yaml(self) -> None:
        """Every implemented characteristic UUID must have a YAML entry.

        An implementation without a YAML entry is a real bug — the class
        can never be resolved by UUID lookup, so it is invisible to the
        registry and will fail in batch parsing scenarios.
        """
        yaml_uuids = set(uuid_registry._characteristics.keys())
        registry = CharacteristicRegistry.get_instance()
        impl_uuids = {u.normalized for u in registry._get_sig_classes_map()}

        orphans = impl_uuids - yaml_uuids
        if orphans:
            orphan_details = []
            sig_map = registry._get_sig_classes_map()
            for bt_uuid, cls in sig_map.items():
                if bt_uuid.normalized in orphans:
                    orphan_details.append(f"{cls.__name__} (UUID: {bt_uuid})")
            pytest.fail(
                f"{len(orphans)} characteristic(s) implemented but missing from YAML:\n  "
                + "\n  ".join(sorted(orphan_details))
            )


class TestOrphanServices:
    """Detect service classes with no YAML UUID entry."""

    def test_all_implemented_services_exist_in_yaml(self) -> None:
        """Every implemented service UUID must have a YAML entry."""
        yaml_uuids = set(uuid_registry._services.keys())
        registry = GattServiceRegistry.get_instance()
        impl_uuids = {u.normalized for u in registry._get_sig_classes_map()}

        orphans = impl_uuids - yaml_uuids
        if orphans:
            orphan_details = []
            sig_map = registry._get_sig_classes_map()
            for bt_uuid, cls in sig_map.items():
                if bt_uuid.normalized in orphans:
                    orphan_details.append(f"{cls.__name__} (UUID: {bt_uuid})")
            pytest.fail(
                f"{len(orphans)} service(s) implemented but missing from YAML:\n  "
                + "\n  ".join(sorted(orphan_details))
            )


class TestOrphanDescriptors:
    """Detect descriptor classes with no YAML UUID entry."""

    def test_all_implemented_descriptors_exist_in_yaml(self) -> None:
        """Every implemented descriptor UUID must have a YAML entry."""
        yaml_uuids = set(uuid_registry._descriptors.keys())
        impl_uuids = {BluetoothUUID(uuid_str).normalized for uuid_str in DescriptorRegistry._registry}

        orphans = impl_uuids - yaml_uuids
        if orphans:
            pytest.fail(
                f"{len(orphans)} descriptor(s) implemented but missing from YAML:\n  " + "\n  ".join(sorted(orphans))
            )

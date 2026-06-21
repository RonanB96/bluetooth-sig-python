"""Tests for scripts/gatt_coverage_report.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from bluetooth_sig.gatt.descriptors import DescriptorRegistry
from bluetooth_sig.gatt.uuid_registry import get_uuid_registry
from bluetooth_sig.types.uuid import BluetoothUUID

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _PROJECT_ROOT / "scripts" / "gatt_coverage_report.py"


class TestGattCoverageReport:
    """Coverage report script loads descriptor registry before counting."""

    def test_descriptor_registry_loaded_before_count(self) -> None:
        """Descriptor count must reflect lazy-loaded registry, not empty pre-load state."""
        uuid_registry = get_uuid_registry()
        uuid_registry.ensure_loaded()
        desc_yaml_count = len(uuid_registry._descriptors)

        DescriptorRegistry._ensure_loaded()
        impl_count = len(DescriptorRegistry.list_registered_descriptors())

        assert impl_count > 0
        assert impl_count <= desc_yaml_count

    def test_script_reports_nonzero_descriptors(self) -> None:
        """Script stdout must show implemented descriptors, not 0/N."""
        result = subprocess.run(
            [sys.executable, str(_SCRIPT)],
            capture_output=True,
            text=True,
            check=False,
            cwd=_PROJECT_ROOT,
        )
        assert result.returncode == 0
        assert "Descriptors" in result.stdout

        for line in result.stdout.splitlines():
            if line.strip().startswith("Descriptors"):
                parts = line.split()
                impl_count = int(parts[1].split("/")[0])
                assert impl_count > 0, line
                break
        else:
            pytest.fail("Descriptors line not found in coverage report output")

    def test_verbose_lists_descriptor_gaps(self) -> None:
        """Verbose mode lists unimplemented descriptor names when gaps exist."""
        uuid_registry = get_uuid_registry()
        uuid_registry.ensure_loaded()
        DescriptorRegistry._ensure_loaded()
        desc_yaml_uuids = set(uuid_registry._descriptors.keys())
        desc_impl = {BluetoothUUID(u).normalized for u in DescriptorRegistry.list_registered_descriptors()}
        gaps = desc_yaml_uuids - desc_impl
        if not gaps:
            pytest.skip("No descriptor gaps to verify")

        result = subprocess.run(
            [sys.executable, str(_SCRIPT), "--verbose"],
            capture_output=True,
            text=True,
            check=False,
            cwd=_PROJECT_ROOT,
        )
        assert result.returncode == 0
        assert "Unimplemented descriptors" in result.stdout

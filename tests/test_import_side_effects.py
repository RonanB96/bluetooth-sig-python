"""Verify package import does not eagerly load YAML registries."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run_import_probe(script: str) -> subprocess.CompletedProcess[str]:
    env = {"PYTHONPATH": str(REPO_ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**dict(**__import__("os").environ), **env},
    )


class TestImportSideEffects:
    """Subprocess guards for import-time registry loading."""

    def test_root_import_does_not_load_uuid_registry(self) -> None:
        """Import bluetooth_sig must not parse UUID YAML."""
        script = """
from bluetooth_sig.gatt.uuid_registry import UuidRegistry
import bluetooth_sig  # noqa: F401
assert not UuidRegistry()._loaded, "UuidRegistry loaded at import time"
"""
        result = _run_import_probe(script)
        assert result.returncode == 0, result.stderr or result.stdout

    def test_root_import_does_not_load_characteristic_registry(self) -> None:
        """Import bluetooth_sig must not build characteristic class maps."""
        script = """
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
import bluetooth_sig  # noqa: F401
assert not CharacteristicRegistry.get_instance()._loaded
"""
        result = _run_import_probe(script)
        assert result.returncode == 0, result.stderr or result.stdout

    def test_root_import_module_count_bounded(self) -> None:
        """Root import must not load the full characteristic implementation graph."""
        script = """
import sys
import bluetooth_sig  # noqa: F401
char_mods = [m for m in sys.modules if m.startswith("bluetooth_sig.gatt.characteristics.")]
limit = 45
count = len(char_mods)
assert count <= limit, f"expected <= {limit} characteristic modules, got {count}"
print(count)
"""
        result = _run_import_probe(script)
        assert result.returncode == 0, result.stderr or result.stdout

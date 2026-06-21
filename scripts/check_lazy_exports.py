#!/usr/bin/env python3
"""Verify committed lazy export artifacts match generate_lazy_exports.py output."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_GENERATOR = _REPO_ROOT / "scripts" / "generate_lazy_exports.py"
_ARTIFACTS = (
    _REPO_ROOT / "src/bluetooth_sig/gatt/characteristics/_export_map.py",
    _REPO_ROOT / "src/bluetooth_sig/gatt/characteristics/__init__.pyi",
    _REPO_ROOT / "src/bluetooth_sig/gatt/services/_export_map.py",
    _REPO_ROOT / "src/bluetooth_sig/gatt/services/__init__.pyi",
    _REPO_ROOT / "src/bluetooth_sig/gatt/descriptors/_export_map.py",
    _REPO_ROOT / "src/bluetooth_sig/gatt/descriptors/__init__.pyi",
)
_REGENERATE_CMD = "PYTHONPATH=src python scripts/generate_lazy_exports.py"


def check_lazy_exports() -> list[Path]:
    """Regenerate lazy exports and return paths that were out of date.

    Restores original file contents when drift is detected so callers keep a
    clean working tree.
    """
    before = {path: path.read_bytes() for path in _ARTIFACTS}

    env = os.environ.copy()
    env["PYTHONPATH"] = str(_REPO_ROOT / "src")

    subprocess.run(
        [sys.executable, str(_GENERATOR)],
        cwd=_REPO_ROOT,
        check=True,
        env=env,
    )

    stale = [path for path in _ARTIFACTS if path.read_bytes() != before[path]]
    if stale:
        for path in _ARTIFACTS:
            path.write_bytes(before[path])
    return stale


def main() -> int:
    """Exit 0 when artifacts are current; 1 when regeneration is required."""
    stale = check_lazy_exports()
    if stale:
        print("Stale lazy export artifacts detected.", file=sys.stderr)
        print(f"Regenerate with: {_REGENERATE_CMD}", file=sys.stderr)
        for path in stale:
            print(f"  - {path.relative_to(_REPO_ROOT)}", file=sys.stderr)
        return 1

    print("Lazy export artifacts are up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Library detection utilities for BLE examples.

This module performs non-invasive detection of optional BLE back-ends
so example scripts can decide which integrations to run. It uses
``importlib.util.find_spec`` to detect presence and only imports the
actual module object when it's available.
"""

from __future__ import annotations

# Silence the isort/import-order diagnostic for this file only; the
# library-detection logic intentionally performs feature detection and
# conditional imports that can confuse simple alphabetical import sorting.
# Tell isort to avoid reordering this small detection import block.
# isort: off
import importlib
from importlib import util as importlib_util

# isort: on
# Public state describing available example back-ends
AVAILABLE_LIBRARIES: dict[str, dict[str, str | bool]] = {}

# Detect bleak / bleak-retry connector
_bleak_spec = importlib_util.find_spec("bleak")
_bleak_retry_spec = importlib_util.find_spec("bleak_retry_connector")

bleak_available: bool = bool(_bleak_spec)
bleak_retry_available: bool = bool(_bleak_retry_spec)

# Import module objects only when the spec indicated availability.
# If the import fails unexpectedly, treat the back-end as unavailable.
_bleak_module: object | None = None
if bleak_available:
    try:
        _bleak_module = importlib.import_module("bleak")
    except ImportError:
        bleak_available = False
        _bleak_module = None

_bleak_retry_module: object | None = None
if bleak_retry_available:
    try:
        _bleak_retry_module = importlib.import_module("bleak_retry_connector")
    except ImportError:
        bleak_retry_available = False
        _bleak_retry_module = None

# Detect SimplePyBLE
simplepyble_available: bool = bool(importlib_util.find_spec("simplepyble"))
simplepyble_module: object | None = None
if simplepyble_available:
    try:
        simplepyble_module = importlib.import_module("simplepyble")
    except ImportError:
        simplepyble_available = False
        simplepyble_module = None

# Populate the user-friendly AVAILABLE_LIBRARIES mapping
if bleak_retry_available:
    AVAILABLE_LIBRARIES["bleak-retry"] = {
        "module": "bleak_retry_connector",
        "async": True,
        "description": "Robust BLE connections with retry logic",
    }
elif bleak_available:
    AVAILABLE_LIBRARIES["bleak"] = {
        "module": "bleak",
        "async": True,
        "description": "Bleak (async) - cross-platform BLE library",
    }

if simplepyble_available:
    AVAILABLE_LIBRARIES["simplepyble"] = {
        "module": "simplepyble",
        "async": False,
        "description": "Cross-platform BLE library (requires commercial license for commercial use)",
    }


def show_library_availability() -> bool:
    """Display which BLE libraries are available for examples.

    Returns True if one or more libraries are available, False otherwise.
    """
    print("📚 BLE Library Availability Check")
    print("=" * 40)

    if not AVAILABLE_LIBRARIES:
        print("❌ No BLE libraries found. Install one or more:")
        print("   pip install .[examples]  # Install example back-ends and demo utilities")
        return False

    print("✅ Available BLE libraries:")
    for lib_name, info in AVAILABLE_LIBRARIES.items():
        async_str = "Async" if info["async"] else "Sync"
        print(f"   {lib_name}: {info['description']} ({async_str})")

    print(f"\n🎯 Will demonstrate bluetooth_sig parsing with {len(AVAILABLE_LIBRARIES)} libraries")
    return True


__all__ = [
    "AVAILABLE_LIBRARIES",
    "bleak_available",
    "bleak_retry_available",
    "show_library_availability",
    "simplepyble_available",
    "simplepyble_module",
]


if __name__ == "__main__":
    # Run a quick check and return non-zero exit code if no libraries are found
    import sys

    ok = show_library_availability()
    sys.exit(0 if ok else 1)

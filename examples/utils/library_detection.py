#!/usr/bin/env python3
"""Library detection utilities for BLE examples.

This module handles detection and availability checking of different BLE libraries.
"""

from __future__ import annotations

import importlib.util

# Check available BLE libraries
AVAILABLE_LIBRARIES: dict[str, dict[str, str | bool]] = {}

# Note: Plain bleak support removed - only bleak-retry-connector supported
BLEAK_AVAILABLE = False

# Check for Bleak-retry-connector
if importlib.util.find_spec("bleak_retry_connector") is not None:
    AVAILABLE_LIBRARIES["bleak-retry"] = {
        "module": "bleak_retry_connector",
        "async": True,
        "description": "Robust BLE connections with retry logic",
    }
    BLEAK_RETRY_AVAILABLE = True
else:
    BLEAK_RETRY_AVAILABLE = False

# Check for SimplePyBLE (correct package name)
SIMPLEPYBLE_AVAILABLE = False
SIMPLEPYBLE_MODULE = None
if importlib.util.find_spec("simplepyble") is not None:
    try:
        # Import at module scope using importlib to avoid unused-import pylint warnings
        SIMPLEPYBLE_MODULE = importlib.import_module("simplepyble")  # type: ignore
    except Exception:  # pylint: disable=broad-exception-caught
        SIMPLEPYBLE_MODULE = None
        SIMPLEPYBLE_AVAILABLE = False
    else:
        SIMPLEPYBLE_AVAILABLE = True
        AVAILABLE_LIBRARIES["simplepyble"] = {
            "module": "simplepyble",
            "async": False,
            "description": "Cross-platform BLE library (requires commercial license for commercial use)",
        }


def show_library_availability() -> bool:
    """Display which BLE libraries are available."""
    print("📚 BLE Library Availability Check")
    print("=" * 40)

    if not AVAILABLE_LIBRARIES:
        print("❌ No BLE libraries found. Install one or more:")
        print("   pip install bleak-retry-connector  # Enhanced Bleak with retry logic")
        print(
            "   pip install simplepyble  # Cross-platform (commercial license for commercial use)"
        )
        return False

    print("✅ Available BLE libraries:")
    for lib_name, info in AVAILABLE_LIBRARIES.items():
        async_str = "Async" if info["async"] else "Sync"
        print(f"   {lib_name}: {info['description']} ({async_str})")

    print(
        f"\n🎯 Will demonstrate bluetooth_sig parsing with {len(AVAILABLE_LIBRARIES)} libraries"
    )
    return True

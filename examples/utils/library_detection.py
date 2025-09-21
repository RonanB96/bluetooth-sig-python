#!/usr/bin/env python3
"""Library detection utilities for BLE examples.

This module handles detection and availability checking of different BLE libraries.
"""

from __future__ import annotations

# Direct imports - will fail at runtime if libraries are not installed
import bleak_retry_connector  # noqa: F401 # Import to test availability
import simplepyble as simplepyble_module  # noqa: F401 # Import to test availability

# Check available BLE libraries
AVAILABLE_LIBRARIES: dict[str, dict[str, str | bool]] = {}

# Note: Plain bleak support removed - only bleak-retry-connector supported
bleak_available = False

# Set up available libraries based on successful imports
AVAILABLE_LIBRARIES["bleak-retry"] = {
    "module": "bleak_retry_connector",
    "async": True,
    "description": "Robust BLE connections with retry logic",
}

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

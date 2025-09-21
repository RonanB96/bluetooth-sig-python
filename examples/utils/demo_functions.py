#!/usr/bin/env python3
"""Demo functions for BLE examples.

This module provides demo functions that were previously in ble_utils.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from .library_detection import (
    BLEAK_RETRY_AVAILABLE,
    SIMPLEPYBLE_AVAILABLE,
    SIMPLEPYBLE_MODULE,
)
from .simpleble_integration import comprehensive_device_analysis_simpleble


async def demo_library_comparison(
    address: str, target_uuids: list[str] | None = None
) -> dict[str, Any]:
    """Compare BLE libraries using comprehensive device analysis.

    Note: Only supports bleak-retry and simpleble (plain bleak removed).

    Args:
        address: Device address
        target_uuids: UUIDs to read, or None for comprehensive analysis

    Returns:
        Dict of results from each library
    """
    comparison_results = {}

    print("🔍 Comparing BLE Libraries (bleak-retry and simpleble only)")
    print("=" * 60)

    # Test Bleak-retry
    if BLEAK_RETRY_AVAILABLE:
        try:
            print("\n🔁 Running Bleak-retry analysis...")
            if target_uuids is None:
                target_uuids = ["2A19", "2A00"]  # Default UUIDs for demo

            # Note: This would need bleak-retry integration functions
            # For now just placeholder
            print("❌ Bleak-retry integration not yet implemented")
            comparison_results["bleak-retry"] = {"status": "not_implemented"}
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"❌ Bleak-retry analysis failed: {e}")

    await asyncio.sleep(1)

    # Test SimplePyBLE
    if SIMPLEPYBLE_AVAILABLE and SIMPLEPYBLE_MODULE:
        try:
            print("\n🔁 Running SimplePyBLE analysis...")
            simple_results = await asyncio.to_thread(
                comprehensive_device_analysis_simpleble,
                address,
                SIMPLEPYBLE_MODULE,
            )
            comparison_results["simplepyble"] = simple_results
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"❌ SimplePyBLE analysis failed: {e}")

    return comparison_results

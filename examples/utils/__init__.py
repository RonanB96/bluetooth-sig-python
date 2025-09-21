"""Utilities package for bluetooth_sig examples.

This package contains utilities split by functionality to improve maintainability
and reduce the size of individual modules.
"""

# Set up path for imports from src directory
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from .bleak_retry_integration import (
    discover_services_bleak_retry,
    handle_notifications_bleak_retry,
    read_characteristics_bleak_retry,
    scan_with_bleak_retry,
)
from .data_parsing import (
    parse_and_display_results,
    short_uuid,
)
from .demo_functions import (
    demo_library_comparison,
)
from .device_scanning import (
    safe_get_device_info,
)
from .library_detection import (
    AVAILABLE_LIBRARIES,
    bleak_retry_available,
    show_library_availability,
    simplepyble_available,
    simplepyble_module,
)
from .mock_data import (
    get_default_characteristic_uuids,
    mock_ble_data,
)

# Re-export most commonly used functions
__all__ = [
    # Library detection
    "AVAILABLE_LIBRARIES",
    "bleak_retry_available",
    "simplepyble_available",
    "simplepyble_module",
    "show_library_availability",
    # Bleak-retry integration
    "discover_services_bleak_retry",
    "handle_notifications_bleak_retry",
    "read_characteristics_bleak_retry",
    "scan_with_bleak_retry",
    # Data parsing
    "parse_and_display_results",
    "short_uuid",
    # Device scanning
    "safe_get_device_info",
    # Mock data
    "mock_ble_data",
    "get_default_characteristic_uuids",
    # Demo functions
    "demo_library_comparison",
]

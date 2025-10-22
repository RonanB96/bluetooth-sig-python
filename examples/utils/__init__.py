"""Utilities package for bluetooth-sig examples.

This package exposes only lightweight utilities that do not pull in
heavy external BLE libraries at import time. Adapter-specific modules
that require optional third-party backends live as submodules under
``examples.utils`` and should be imported explicitly by example
scripts (so imports fail fast when the environment is missing the
required dependency).

Note: This package intentionally avoids importing modules such as
``bleak_retry_integration`` or ``library_detection`` here to prevent
accidental import-time ImportError when unrelated example code is
imported. Import those submodules directly where they are required.
"""

from __future__ import annotations

# Keep path helper so examples executed as scripts still find the src
# package when running from the examples/ directory. Scripts should call
# `examples.ensure_example_import_paths()` before running example code if
# they require the repository layout to be added to sys.path.
# Re-export only small, safe helpers that don't depend on optional
# third-party BLE backends.
from .data_parsing import parse_and_display_results
from .device_scanning import safe_get_device_info
from .mock_data import get_default_characteristic_uuids, mock_ble_data

__all__ = [
    "parse_and_display_results",
    "get_default_characteristic_uuids",
    "mock_ble_data",
    "safe_get_device_info",
]


def main() -> None:
    """Print package information."""
    print("Examples utilities package. Exports: ", ", ".join(__all__))


if __name__ == "__main__":
    main()

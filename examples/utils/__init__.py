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
from .argparse_utils import CommonArgs, create_common_parser, create_connection_manager, validate_and_setup
from .data_parsing import parse_and_display_results
from .notification_utils import handle_notifications_generic

__all__ = [
    "CommonArgs",
    "create_common_parser",
    "create_connection_manager",
    "handle_notifications_generic",
    "parse_and_display_results",
    "validate_and_setup",
]


def main() -> None:
    """Print package information."""
    print("Examples utilities package. Exports: ", ", ".join(__all__))


if __name__ == "__main__":
    main()

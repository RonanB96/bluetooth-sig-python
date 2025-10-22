"""Examples package for bluetooth_sig.

This package contains example scripts demonstrating bluetooth_sig usage.
All examples automatically have the src and examples directories added
to the Python path.
"""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


if __name__ == "__main__":
    print("Examples package helper. Use the scripts in the examples/ directory to run demos.")

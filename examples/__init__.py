"""Examples package for bluetooth_sig.

This package contains example scripts demonstrating bluetooth_sig usage.
All examples automatically have the src and examples directories added to the Python path.
"""

# Set up path for imports from src directory and examples directory - centralized for all examples
import sys
from pathlib import Path

# Add src directory for bluetooth_sig imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Add examples directory for utils and shared_utils imports
sys.path.insert(0, str(Path(__file__).parent))

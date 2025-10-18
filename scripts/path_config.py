"""Import path configuration for scripts."""

import os
import sys
from pathlib import Path


def configure_path() -> None:
    """Add the src directory to Python path."""
    src_path = str(Path(__file__).parent.parent / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def configure_for_scripts() -> None:
    """Configure path for script imports."""
    # Get the absolute path of the project root
    project_root = Path(__file__).parent.parent

    # Add src directory to Python path
    src_path = str(project_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    # Set PYTHONPATH for subprocess calls
    python_path = os.environ.get("PYTHONPATH", "")
    if src_path not in python_path:
        path_value = f"{src_path}:{python_path}" if python_path else src_path
        os.environ["PYTHONPATH"] = path_value

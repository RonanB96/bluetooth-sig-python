# type: ignore
"""MkDocs hooks to automatically generate characteristics documentation before building."""

import subprocess
import sys
from pathlib import Path


def on_pre_build(config, **kwargs):
    """Run the generate script before building documentation."""
    script_path = Path(__file__).parent / "scripts" / "generate_char_service_list.py"

    if not script_path.exists():
        print(f"Warning: Generate script not found at {script_path}")
        return

    try:
        print("Running characteristics generation script...")
        subprocess.run(
            [sys.executable, str(script_path)], cwd=Path(__file__).parent, capture_output=True, text=True, check=True
        )
        print("✓ Characteristics documentation generated successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to generate characteristics: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise

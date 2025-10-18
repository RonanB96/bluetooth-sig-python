# type: ignore
"""MkDocs hooks to automatically generate characteristics documentation before building."""

import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def on_pre_build(config: Mapping[str, Any], **kwargs: object) -> None:
    """Run the generate script before building documentation.

    Args:
        config: MkDocs configuration mapping provided by MkDocs.
        **kwargs: Additional keyword arguments forwarded by the plugin API.
    """
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

    # Run diagrams generator (pyreverse + pydeps) prior to docs build. This is
    # intentionally best-effort by default; set STRICT_DIAGRAMS=1 to make the
    # build fail when diagram generation fails.
    diag_script = Path(__file__).parent / "scripts" / "generate_diagrams.py"
    if not diag_script.exists():
        print(f"Warning: Diagrams generation script not found at {diag_script}")
        return

    try:
        print("Running diagrams generation script...")
        # Diagrams are required for the published docs. Force strict behaviour
        # for the diagrams generation subprocess so that failures cause the
        # mkdocs pre-build hook to fail the overall build. We pass an explicit
        # environment to avoid mutating the calling process's environment.
        env = dict(os.environ)
        env["STRICT_DIAGRAMS"] = "1"
        subprocess.run(
            [sys.executable, str(diag_script)],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
        print("✓ Diagrams generated successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to generate diagrams: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise

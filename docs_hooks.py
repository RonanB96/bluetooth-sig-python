# type: ignore
"""MkDocs hooks to automatically generate documentation content before building.

This hook runs pre-build scripts to generate:
1. Characteristics/services list (docs/reference/characteristics.md)
2. Architecture diagrams (docs/diagrams/*.svg)

These generated files are tracked in git and can be regenerated at build time.
"""

import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def on_pre_build(config: Mapping[str, Any], **kwargs: object) -> None:
    """Run generation scripts before building documentation.

    Executes two pre-build steps:
    1. Generates comprehensive list of supported characteristics and services
       from the registry system → docs/supported-characteristics.md
    2. Generates class diagrams and dependency graphs using pyreverse and pydeps
       → docs/diagrams/*.svg (C4 model, package structure, etc.)

    Args:
        config: MkDocs configuration mapping provided by MkDocs.
        **kwargs: Additional keyword arguments forwarded by the plugin API.

    Raises:
        subprocess.CalledProcessError: If any generation script fails.
    """
    # =========================================================================
    # Step 1: Generate characteristics and services documentation
    # =========================================================================
    # Outputs to: docs/reference/characteristics.md
    # Purpose: Auto-generate comprehensive list of 162 characteristics and
    #          30+ services from the registry system, ensuring docs stay in
    #          sync with implementation.
    script_path = Path(__file__).parent / "scripts" / "generate_char_service_list.py"

    if not script_path.exists():
        print(f"Warning: Generate script not found at {script_path}")
        return

    try:
        print("Running characteristics generation script...")
        print("  → Outputs to: docs/reference/characteristics.md")
        subprocess.run(
            [sys.executable, str(script_path)], cwd=Path(__file__).parent, capture_output=True, text=True, check=True
        )
        print("✓ Characteristics documentation generated successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to generate characteristics: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise

    # =========================================================================
    # Step 2: Generate architecture diagrams
    # =========================================================================
    # Outputs to: docs/diagrams/*.svg (classes, packages, dependencies)
    # Purpose: Visual documentation of architecture using pyreverse (class
    #          diagrams) and pydeps (dependency graphs). Used in the
    #          explanation/architecture/ section.
    # Note: Requires pylint (pyreverse) and pydeps to be installed.
    #       Set STRICT_DIAGRAMS=1 to fail build if tools unavailable.
    diag_script = Path(__file__).parent / "scripts" / "generate_diagrams.py"
    if not diag_script.exists():
        print(f"Warning: Diagrams generation script not found at {diag_script}")
        return

    try:
        print("Running diagrams generation script...")
        print("  → Outputs to: docs/diagrams/*.svg")
        # Diagrams are required for the published docs. Force strict behaviour
        # for the diagrams generation subprocess so that failures cause the
        # mkdocs pre-build hook to fail the overall build. We pass an explicit
        # environment to avoid mutating the calling process's environment.
        env = dict(os.environ)
        env["STRICT_DIAGRAMS"] = "1"  # Fail build if diagram generation fails
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

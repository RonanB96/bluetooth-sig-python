"""Custom build hook to initialize git submodule before building.

This ensures the bluetooth_sig submodule containing Bluetooth SIG data files
is initialized and available when building distributions, allowing pip installs
from git or PyPI to work without manual submodule initialization.

Per Hatchling documentation: https://hatch.pypa.io/latest/plugins/build-hook/custom/
"""

import subprocess
import sys
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class SubmoduleBuildHook(BuildHookInterface):
    """Build hook that initializes git submodules before building."""

    def initialize(self, version: str, build_data: dict[str, any]) -> None:
        """Initialize git submodule before build if in a git repository.

        Args:
            version: The version of the project being built
            build_data: Build configuration data
        """
        submodule_path = Path(self.root) / "bluetooth_sig"

        # Check if submodule is already populated
        if submodule_path.exists() and any(submodule_path.iterdir()):
            self.app.display_info("Submodule already initialized")
            return

        # Check if we're in a git repository
        git_dir = Path(self.root) / ".git"
        if not git_dir.exists():
            self.app.display_warning(
                "Not in a git repository - submodule initialization skipped. "
                "This is expected for PyPI source distributions."
            )
            return

        # Initialize and update the submodule
        self.app.display_info("Initializing git submodule...")
        try:
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
            )
            self.app.display_success("Git submodule initialized successfully")
        except subprocess.CalledProcessError as e:
            self.app.display_error(f"Failed to initialize submodule: {e.stderr}")
            sys.exit(1)

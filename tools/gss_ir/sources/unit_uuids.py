"""Map unit identifiers to 16-bit UUIDs."""

from __future__ import annotations

from pathlib import Path

from .assigned_number import read_assigned_uuids


def read_unit_uuids(path: Path) -> dict[str, int]:
    """Read ``units.yaml``.

    Args:
        path: Assigned-number YAML file.

    Returns:
        Mapping of ``org.bluetooth.unit.*`` to a 16-bit UUID.

    Raises:
        GssSourceError: If the file is not the assigned-number list, or an id repeats.
        OSError: If the file cannot be read.
    """
    return read_assigned_uuids(path, key_name="unit UUID")

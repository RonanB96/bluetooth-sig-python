"""Map characteristic identifiers to 16-bit UUIDs."""

from __future__ import annotations

from pathlib import Path

from .assigned_number import AssignedUuid, read_assigned_entries, read_assigned_uuids


def read_characteristic_records(path: Path) -> tuple[AssignedUuid, ...]:
    """Read characteristic assigned numbers, including each display name.

    Args:
        path: ``characteristic_uuids.yaml``.

    Returns:
        Entries in file order.

    Raises:
        GssSourceError: If the file is not the assigned-number list, an id repeats, or a name is missing.
        OSError: If the file cannot be read.
    """
    return read_assigned_entries(path, key_name="characteristic UUID")


def read_characteristic_uuids(path: Path) -> dict[str, int]:
    """Read ``characteristic_uuids.yaml``.

    Args:
        path: Assigned-number YAML file.

    Returns:
        Mapping of ``org.bluetooth.characteristic.*`` to a 16-bit UUID.

    Raises:
        GssSourceError: If the file is not the assigned-number list, or an id repeats.
        OSError: If the file cannot be read.
    """
    return read_assigned_uuids(path, key_name="characteristic UUID")

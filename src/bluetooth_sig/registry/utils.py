"""Common utilities for registry modules."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import msgspec


def load_yaml_uuids(file_path: Path) -> list[dict[str, Any]]:
    """Load UUID entries from a YAML file.

    Args:
        file_path: Path to the YAML file

    Returns:
        List of UUID entry dictionaries
    """
    if not file_path.exists():
        return []

    with file_path.open("r", encoding="utf-8") as file_handle:
        data = msgspec.yaml.decode(file_handle.read())

    if not isinstance(data, dict):
        return []

    data_dict = cast(dict[str, Any], data)
    uuid_entries = data_dict.get("uuids")
    if not isinstance(uuid_entries, list):
        return []

    typed_entries: list[dict[str, Any]] = []
    for entry in uuid_entries:
        if isinstance(entry, dict):
            typed_entries.append(cast(dict[str, Any], entry))

    return typed_entries


def normalize_uuid_string(uuid: str | int) -> str:
    """Normalize a UUID string or int to uppercase hex without 0x prefix.

    Args:
        uuid: UUID as string (with or without 0x) or int

    Returns:
        Normalized UUID string
    """
    if isinstance(uuid, str):
        uuid = uuid.replace("0x", "").replace("0X", "")
    else:
        uuid = hex(uuid)[2:].upper()
    return uuid


def find_bluetooth_sig_path() -> Path | None:
    """Find the Bluetooth SIG assigned_numbers directory.

    Returns:
        Path to the uuids directory, or None if not found
    """
    # Try development location first (git submodule)
    project_root = Path(__file__).parent.parent.parent.parent
    base_path = project_root / "bluetooth_sig" / "assigned_numbers" / "uuids"

    if base_path.exists():
        return base_path

    # Try installed package location
    pkg_root = Path(__file__).parent.parent
    base_path = pkg_root / "bluetooth_sig" / "assigned_numbers" / "uuids"

    return base_path if base_path.exists() else None

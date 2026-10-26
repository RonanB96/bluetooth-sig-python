"""Handwritten codecs that replace a generated codec for the same characteristic."""

from __future__ import annotations

import re
import warnings
from pathlib import Path

from .gss import read_characteristic

_CHARACTERISTIC_ID = re.compile(r"org\.bluetooth\.characteristic\.[A-Za-z0-9_.-]+")


def handwritten_override_ids(override_root: Path) -> tuple[str, ...]:
    """Return characteristic ids declared by handwritten override sources.

    Args:
        override_root: Directory of ``<characteristic>/src/*.cpp`` override codecs.

    Returns:
        Identifiers in source order. A directory with no characteristic id is skipped.
    """
    if not override_root.is_dir():
        return ()
    found: list[str] = []
    seen: set[str] = set()
    for path in sorted(override_root.glob("*/src/*.cpp")):
        match = _CHARACTERISTIC_ID.search(path.read_text(encoding="utf-8"))
        if match is None or match.group(0) in seen:
            continue
        seen.add(match.group(0))
        found.append(match.group(0))
    return tuple(found)


def gss_characteristic_ids(gss_directory: Path) -> set[str]:
    """Return identifiers of GSS characteristic documents.

    Args:
        gss_directory: Directory of ``org.bluetooth.characteristic.*.yaml`` files.

    Returns:
        Identifiers read from those documents.

    Raises:
        GssSourceError: If a document is not a characteristic.
        OSError: If a file cannot be read.
    """
    identifiers: set[str] = set()
    for path in sorted(gss_directory.glob("org.bluetooth.characteristic.*.yaml")):
        characteristic = read_characteristic(path, source_path=path.name)
        identifiers.add(characteristic.identifier)
    return identifiers


def handwritten_gss_overlaps(override_ids: tuple[str, ...], gss_identifiers: set[str]) -> tuple[str, ...]:
    """Return handwritten ids that also have a GSS characteristic document.

    Args:
        override_ids: Characteristic ids declared by override sources.
        gss_identifiers: Identifiers read from GSS characteristic documents.

    Returns:
        Overlapping ids in override order.
    """
    return tuple(identifier for identifier in override_ids if identifier in gss_identifiers)


def warn_handwritten_gss_overlaps(root: Path) -> tuple[str, ...]:
    """Warn when a handwritten override exists for a characteristic that has GSS YAML.

    Args:
        root: Repository root containing ``btsig/override`` and ``bluetooth_sig/gss``.

    Returns:
        Overlapping characteristic ids. Each one is also reported with ``warnings.warn``.
    """
    overlaps = handwritten_gss_overlaps(
        handwritten_override_ids(root / "btsig" / "override"),
        gss_characteristic_ids(root / "bluetooth_sig" / "gss"),
    )
    for identifier in overlaps:
        warnings.warn(
            f"handwritten override for {identifier} also has a GSS document",
            stacklevel=2,
        )
    return overlaps

"""Phrase rules and IR assembly."""

from .assemble import iter_characteristic_paths, normalise_identifier, normalise_path, repository_root
from .result import Unsupported

__all__ = [
    "Unsupported",
    "iter_characteristic_paths",
    "normalise_identifier",
    "normalise_path",
    "repository_root",
]

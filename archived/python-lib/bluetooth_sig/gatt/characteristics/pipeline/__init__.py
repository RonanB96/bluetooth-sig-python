"""Pipeline components for characteristic parsing and encoding.

This package provides the multi-stage pipeline implementation for GATT
characteristic value parsing and encoding, extracted from ``BaseCharacteristic``
for separation of concerns.
"""

from __future__ import annotations

from .encode_pipeline import EncodePipeline
from .parse_pipeline import ParsePipeline
from .validation import CharacteristicValidator

__all__ = [
    "CharacteristicValidator",
    "EncodePipeline",
    "ParsePipeline",
]

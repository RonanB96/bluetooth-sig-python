"""Data types for Bluetooth SIG standards."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from ..types.context import CharacteristicContext


@dataclass
class SIGInfo:
    """Base information about Bluetooth SIG characteristics or services."""

    uuid: str
    name: str
    description: str = ""


@dataclass
class CharacteristicInfo(SIGInfo):
    """Information about a Bluetooth characteristic."""

    value_type: str = ""
    unit: str = ""
    properties: list[str] = field(default_factory=lambda: cast(list[str], []))


@dataclass
class ServiceInfo(SIGInfo):
    """Information about a Bluetooth service."""

    characteristics: list[str] = field(default_factory=lambda: cast(list[str], []))


@dataclass
class CharacteristicData(CharacteristicInfo):
    """Parsed characteristic data with validation results."""

    value: Any | None = None
    raw_data: bytes = b""
    parse_success: bool = False
    error_message: str = ""
    source_context: CharacteristicContext = field(default_factory=CharacteristicContext)


@dataclass
class ValidationResult(SIGInfo):
    """Result of data validation."""

    is_valid: bool = True
    expected_length: int | None = None
    actual_length: int | None = None
    error_message: str = ""

"""Data types for Bluetooth SIG standards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .gatt.context import CharacteristicContext


@dataclass
class SIGInfo:
    """Base information about Bluetooth SIG characteristics or services."""

    uuid: str
    name: str
    description: str | None = None


@dataclass
class CharacteristicInfo(SIGInfo):
    """Information about a Bluetooth characteristic."""

    value_type: str | None = None
    unit: str | None = None
    properties: list[str] | None = None


@dataclass
class ServiceInfo(SIGInfo):
    """Information about a Bluetooth service."""

    characteristics: list[str] | None = None


@dataclass
class CharacteristicData(CharacteristicInfo):
    """Result of parsing characteristic data."""

    value: Any | None = None
    raw_data: bytes | None = None
    parse_success: bool = True
    error_message: str | None = None
    # Optional context that produced this parsed result
    source_context: CharacteristicContext | None = None


@dataclass
class ValidationResult(SIGInfo):
    """Result of data validation."""

    is_valid: bool = True
    expected_length: int | None = None
    actual_length: int | None = None
    error_message: str | None = None

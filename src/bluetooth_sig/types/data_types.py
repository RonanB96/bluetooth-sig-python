"""Data types for Bluetooth SIG standards."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from .context import CharacteristicContext
from .gatt_enums import GattProperty, ValueType
from .uuid import BluetoothUUID


@dataclass
class SIGInfo:
    """Base information about Bluetooth SIG characteristics or services."""

    uuid: BluetoothUUID
    name: str
    description: str = ""


@dataclass
class CharacteristicInfo(SIGInfo):
    """Information about a Bluetooth characteristic."""

    value_type: ValueType = ValueType.UNKNOWN
    unit: str = ""
    properties: list[GattProperty] = field(default_factory=lambda: cast(list[GattProperty], []))


@dataclass
class ServiceInfo(SIGInfo):
    """Information about a Bluetooth service."""

    characteristics: list[CharacteristicInfo] = field(default_factory=lambda: cast(list[CharacteristicInfo], []))


@dataclass
class CharacteristicData:
    """Parsed characteristic data with validation results."""

    info: CharacteristicInfo
    value: Any | None = None
    raw_data: bytes = b""
    parse_success: bool = False
    error_message: str = ""
    source_context: CharacteristicContext = field(default_factory=CharacteristicContext)

    @property
    def name(self) -> str:
        """Get the characteristic name from info."""
        return self.info.name

    @property
    def properties(self) -> list[GattProperty]:
        """Get the properties as strings for protocol compatibility."""
        return self.info.properties

    @property
    def uuid(self) -> BluetoothUUID:
        """Get the characteristic UUID from info."""
        return self.info.uuid

    @property
    def unit(self) -> str:
        """Get the characteristic unit from info."""
        return self.info.unit


@dataclass
class ValidationResult(SIGInfo):
    """Result of data validation."""

    is_valid: bool = True
    expected_length: int | None = None
    actual_length: int | None = None
    error_message: str = ""


@dataclass
class CharacteristicRegistration:
    """Unified metadata for custom UUID registration"""

    uuid: BluetoothUUID
    name: str = ""
    id: str | None = None
    summary: str = ""
    unit: str = ""
    value_type: ValueType = ValueType.STRING


@dataclass
class ServiceRegistration:
    """Unified metadata for custom UUID registration"""

    uuid: BluetoothUUID
    name: str = ""
    id: str | None = None
    summary: str = ""

from __future__ import annotations

from enum import Enum

import msgspec

from bluetooth_sig.types.uuid import BluetoothUUID


class BaseUuidInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Minimal base info for all UUID-based registry entries."""

    uuid: BluetoothUUID
    name: str
    id: str | None = None


class FieldInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Field-related metadata from YAML."""

    data_type: str | None = None
    field_size: str | None = None


class UnitInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Unit-related metadata from YAML."""

    unit_id: str | None = None
    unit_symbol: str | None = None
    base_unit: str | None = None
    resolution_text: str | None = None


class CharacteristicSpec(msgspec.Struct, kw_only=True):
    """Characteristic specification from cross-file YAML references."""

    uuid: BluetoothUUID
    name: str
    field_info: FieldInfo = msgspec.field(default_factory=FieldInfo)
    unit_info: UnitInfo = msgspec.field(default_factory=UnitInfo)
    description: str | None = None

    # Convenience properties for backward compatibility with existing code
    @property
    def data_type(self) -> str | None:
        """Get data type from field info."""
        return self.field_info.data_type if self.field_info else None

    @property
    def field_size(self) -> str | None:
        """Get field size from field info."""
        return self.field_info.field_size if self.field_info else None

    @property
    def unit_id(self) -> str | None:
        """Get unit ID from unit info."""
        return self.unit_info.unit_id if self.unit_info else None

    @property
    def unit_symbol(self) -> str | None:
        """Get unit symbol from unit info."""
        return self.unit_info.unit_symbol if self.unit_info else None

    @property
    def base_unit(self) -> str | None:
        """Get base unit from unit info."""
        return self.unit_info.base_unit if self.unit_info else None

    @property
    def resolution_text(self) -> str | None:
        """Get resolution text from unit info."""
        return self.unit_info.resolution_text if self.unit_info else None


class UuidOrigin(Enum):
    """Origin of UUID information."""

    BLUETOOTH_SIG = "bluetooth_sig"
    RUNTIME = "runtime"


class UuidInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Default UUID info type for generic registries (extend as needed)."""

    unit: str | None = None
    value_type: str | None = None
    origin: UuidOrigin = UuidOrigin.BLUETOOTH_SIG


class CustomUuidEntry(msgspec.Struct, frozen=True, kw_only=True):
    """Entry for custom UUID registration."""

    uuid: BluetoothUUID
    name: str
    id: str | None = None
    summary: str | None = None
    unit: str | None = None
    value_type: str | None = None


def generate_basic_aliases(info: BaseUuidInfo) -> set[str]:
    """Generate a small set of common alias keys for a BaseUuidInfo.

    This intentionally keeps the behaviour conservative; domain-specific
    heuristics remain the responsibility of the registry.
    """
    aliases: set[str] = set()
    if info.name:
        aliases.add(info.name.lower())
        # Title-case variant for user-facing matches
        aliases.add(info.name.replace("_", " ").replace("-", " ").title())
    if info.id:
        aliases.add(info.id)
    return {a for a in aliases if a and a.strip()}

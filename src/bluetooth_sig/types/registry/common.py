"""Core common types for Bluetooth SIG registry data structures."""

from __future__ import annotations

import msgspec

from bluetooth_sig.types.registry.gss_characteristic import FieldSpec
from bluetooth_sig.types.uuid import BluetoothUUID


class FieldInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Field-related metadata from YAML."""

    name: str | None = None
    data_type: str | None = None
    field_size: str | None = None
    description: str | None = None


class UnitMetadata(msgspec.Struct, frozen=True, kw_only=True):
    """Unit-related metadata from characteristic YAML specifications.

    This is embedded metadata within characteristic specs, distinct from
    the Units registry which uses UUID-based entries.
    """

    unit_id: str | None = None
    unit_symbol: str | None = None
    base_unit: str | None = None
    resolution_text: str | None = None


class CharacteristicSpec(msgspec.Struct, kw_only=True):
    """Characteristic specification from cross-file YAML references."""

    uuid: BluetoothUUID
    name: str
    field_info: FieldInfo = msgspec.field(default_factory=FieldInfo)
    unit_info: UnitMetadata = msgspec.field(default_factory=UnitMetadata)
    description: str | None = None
    structure: list[FieldSpec] = msgspec.field(default_factory=list)

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


class BaseUuidInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Minimal base info for all UUID-based registry entries.

    Child classes should add an id field as needed (required or optional).
    """

    uuid: BluetoothUUID
    name: str


def generate_basic_aliases(info: BaseUuidInfo) -> set[str]:
    """Generate a small set of common alias keys for a BaseUuidInfo.

    Domain-specific heuristics remain the responsibility of the registry.
    """
    aliases: set[str] = set()
    if info.name:
        aliases.add(info.name.lower())
        aliases.add(info.name.replace("_", " ").replace("-", " ").title())
    id_val = getattr(info, "id", None)
    if id_val:
        aliases.add(id_val)
    return {a for a in aliases if a and a.strip()}


# Generic reusable Info classes for common YAML patterns


class UuidIdInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Standard registry info for simple UUID-based registries with org.bluetooth ID.

    Extends BaseUuidInfo (uuid, name) with an id field for org.bluetooth identifiers.
    Used by registries with uuid, name, id fields:
    - browse_group_identifiers (uuid, name, id)
    - declarations (uuid, name, id)
    ...
    """

    id: str


class ValueNameInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Generic info for registries with value and name fields.

    Used by: coding_format, core_version, diacs, mws_channel_type,
    namespace, namespaces, pcm_data_format, transport_layers, uri_schemes,
    company_identifiers, and many others.
    """

    value: int
    name: str

    @property
    def bit(self) -> int:
        """Alias for value when used as bit position."""
        return self.value


class ValueNameReferenceInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Generic info for registries with value, name, and reference fields.

    Used by: ad_types and similar registries with specification references.
    """

    value: int
    name: str
    reference: str


class NameValueInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Generic info for registries with name and value fields (reversed order).

    Used by: psm and similar registries where name comes before numeric value.
    """

    name: str
    value: int

    @property
    def psm(self) -> int:
        """Alias for value when used as PSM."""
        return self.value


class KeyNameInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Generic info for registries with key and name fields.

    Used by: security_keyIDs and similar registries with non-numeric keys.
    """

    key: str
    name: str


class NameUuidTypeInfo(BaseUuidInfo, frozen=True, kw_only=True):
    """Generic info for registries with name, uuid, and type fields.

    Used by: mesh model UUIDs and similar registries with type classification.
    Extends BaseUuidInfo to inherit uuid and name fields.
    """

    type: str


class NameOpcodeTypeInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Generic info for registries with name, opcode, and type fields.

    Used by: mesh opcodes and similar registries with opcode classification.
    """

    name: str
    opcode: int
    type: str

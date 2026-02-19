"""Type definitions for profile and service discovery registries."""

from __future__ import annotations

import msgspec


class PermittedCharacteristicEntry(msgspec.Struct, frozen=True, kw_only=True):
    """A service with its list of permitted characteristic identifiers.

    Loaded from profiles_and_services/{ess,uds,imds}/*_permitted_characteristics.yaml.
    Each YAML entry maps one service URI to a list of characteristic URIs.
    """

    service: str
    characteristics: tuple[str, ...]


class ProfileLookupEntry(msgspec.Struct, frozen=True, kw_only=True):
    """A generic name/value entry from a profile parameter YAML file.

    Covers the simple ``{name, value}`` and ``{value, description}`` patterns
    found across A2DP codecs, ESL display types, HFP bearer technologies,
    AVRCP types, MAP chat states, TDS organisation IDs, and similar files.

    Extra fields beyond name/value are stored in *metadata* so that a single
    struct can represent all simple-lookup schemas without a per-file class.
    """

    name: str
    value: int
    metadata: dict[str, str] = msgspec.field(default_factory=dict)


class AttributeIdEntry(msgspec.Struct, frozen=True, kw_only=True):
    """An SDP attribute identifier entry (name + hex value).

    Loaded from service_discovery/attribute_ids/*.yaml and
    service_discovery/attribute_id_offsets_for_strings.yaml.
    """

    name: str
    value: int


class ProtocolParameterEntry(msgspec.Struct, frozen=True, kw_only=True):
    """A protocol parameter entry from service_discovery/protocol_parameters.yaml.

    Each entry describes a named parameter for a specific protocol
    (e.g. L2CAP PSM, RFCOMM Channel).
    """

    protocol: str
    name: str
    index: int

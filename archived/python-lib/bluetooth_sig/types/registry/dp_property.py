"""Types for Bluetooth SIG Device Property registry."""

from __future__ import annotations

import msgspec


class PropertySpec(msgspec.Struct, frozen=True, kw_only=True):
    """Specification for a Bluetooth SIG property from DP."""

    identifier: str
    name: str
    group: str
    characteristic: str
    description: str


class DpPropertyData(msgspec.Struct, frozen=True, kw_only=True):
    """Top-level data structure for DP property YAML files."""

    property: PropertySpec

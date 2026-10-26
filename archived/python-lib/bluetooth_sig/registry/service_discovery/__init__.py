"""Service discovery registries from assigned_numbers/service_discovery/.

This module contains registries for SDP (Service Discovery Protocol) attribute
identifiers and protocol parameters loaded from the Bluetooth SIG assigned
numbers YAML files.
"""

from __future__ import annotations

from .attribute_ids import (
    ServiceDiscoveryAttributeRegistry,
    get_service_discovery_attribute_registry,
)

__all__ = [
    "ServiceDiscoveryAttributeRegistry",
    "get_service_discovery_attribute_registry",
]

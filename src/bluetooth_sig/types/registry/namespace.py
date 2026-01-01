"""Types for Bluetooth SIG Namespace registry."""

from __future__ import annotations

from .common import ValueNameInfo

NamespaceInfo = ValueNameInfo
"""Info for namespace values (0x01 = Bluetooth SIG)."""

NamespaceDescriptionInfo = ValueNameInfo
"""Info for namespace description values (e.g., 0x010D = 'left')."""

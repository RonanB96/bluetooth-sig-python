"""Types for Bluetooth SIG units registry."""

from __future__ import annotations

from bluetooth_sig.types.registry import UuidIdInfo

# Type alias for semantic clarity while reusing common structure
# Note: Distinct from UnitMetadata which is embedded in CharacteristicSpec
UnitInfo = UuidIdInfo

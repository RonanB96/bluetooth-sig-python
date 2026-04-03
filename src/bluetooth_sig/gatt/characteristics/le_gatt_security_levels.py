"""LE GATT Security Levels characteristic (0x2BF5).

BT Core Spec v6.0, Vol 3, Part C, Section 12.7:
  The Attribute Value is a sequence of Security Level Requirements,
  each with the type uint8[2]. Each Security Level Requirement consists
  of a Security Mode field followed by a Security Level field.

  The Security Mode and Security Level shall be expressed as the same
  number as used in their definitions; e.g., mode 1 is represented as
  0x01 and level 4 is represented as 0x04.

Security modes and levels defined in Section 10.2:
  Mode 1 (encryption-based):
    Level 1: No security (no authentication, no encryption)
    Level 2: Unauthenticated pairing with encryption
    Level 3: Authenticated pairing with encryption
    Level 4: Authenticated LE Secure Connections pairing with 128-bit encryption
  Mode 2 (data signing):
    Level 1: Unauthenticated pairing with data signing
    Level 2: Authenticated pairing with data signing
  Mode 3 (broadcast isochronous):
    Level 1: No security (no authentication, no encryption)
    Level 2: Use of unauthenticated Broadcast_Code
    Level 3: Use of authenticated Broadcast_Code
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class LESecurityMode(IntEnum):
    """LE security modes (BT Core Spec v6.0, Vol 3, Part C, Section 10.2)."""

    ENCRYPTION = 1
    DATA_SIGNING = 2
    BROADCAST_ISOCHRONOUS = 3


class LESecurityModeLevel(IntEnum):
    """Combined security mode+level values for LE GATT Security Levels.

    Each value encodes (mode << 8 | level) for unique identification.
    The raw wire mode/level bytes can be recovered via the mode and level
    properties.

    BT Core Spec v6.0, Vol 3, Part C, Section 10.2.
    """

    # Mode 1: Encryption-based security
    MODE1_NO_SECURITY = 0x0101
    MODE1_UNAUTH_ENCRYPTION = 0x0102
    MODE1_AUTH_ENCRYPTION = 0x0103
    MODE1_AUTH_SC_ENCRYPTION = 0x0104

    # Mode 2: Data signing
    MODE2_UNAUTH_SIGNING = 0x0201
    MODE2_AUTH_SIGNING = 0x0202

    # Mode 3: Broadcast isochronous
    MODE3_NO_SECURITY = 0x0301
    MODE3_UNAUTH_BROADCAST_CODE = 0x0302
    MODE3_AUTH_BROADCAST_CODE = 0x0303

    @property
    def security_mode(self) -> LESecurityMode:
        """The LE security mode number."""
        return LESecurityMode(self.value >> 8)

    @property
    def security_level(self) -> int:
        """The security level number within the mode."""
        return self.value & 0xFF

    @classmethod
    def from_mode_level(cls, mode: int, level: int) -> LESecurityModeLevel:
        """Construct from raw mode and level bytes."""
        return cls((mode << 8) | level)


class SecurityLevelRequirement(msgspec.Struct):
    """A single security level requirement (mode, level) pair."""

    mode: int
    level: int

    @property
    def mode_level(self) -> LESecurityModeLevel:
        """Combined mode+level enum value."""
        return LESecurityModeLevel.from_mode_level(self.mode, self.level)


class LEGATTSecurityLevelsCharacteristic(BaseCharacteristic[list[SecurityLevelRequirement]]):
    """LE GATT Security Levels characteristic (0x2BF5).

    org.bluetooth.characteristic.le_gatt_security_levels

    Sequence of (security_mode, security_level) pairs indicating
    the highest security requirements of the GATT server on an LE connection.
    """

    _characteristic_name = "LE GATT Security Levels"
    min_length: int = 2

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> list[SecurityLevelRequirement]:
        if len(data) % 2 != 0:
            msg = f"Data length must be even (pairs of uint8), got {len(data)}"
            raise ValueError(msg)
        return [SecurityLevelRequirement(mode=data[i], level=data[i + 1]) for i in range(0, len(data), 2)]

    def _encode_value(self, value: list[SecurityLevelRequirement]) -> bytearray:
        result = bytearray()
        for req in value:
            result.append(req.mode)
            result.append(req.level)
        return result

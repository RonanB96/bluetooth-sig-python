"""Battery Time Status characteristic implementation.

Implements the Battery Time Status characteristic (0x2BEE) from the Battery
Service.  An 8-bit flags field controls the presence of optional time fields.

All flag bits use **normal logic** (1 = present, 0 = absent).

The mandatory "Time until Discharged" field and both optional time fields
use uint24 in **minutes**.  Two sentinel values are defined:
  - 0xFFFFFF: Unknown
  - 0xFFFFFE: Greater than 0xFFFFFD

References:
    Bluetooth SIG Battery Service 1.1
    org.bluetooth.characteristic.battery_time_status (GSS YAML)
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import UINT24_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Sentinel values for time fields (uint24 minutes)
_TIME_UNKNOWN: int = 0xFFFFFF
_TIME_OVERFLOW: int = 0xFFFFFE


class BatteryTimeStatusFlags(IntFlag):
    """Battery Time Status flags as per Bluetooth SIG specification."""

    DISCHARGED_ON_STANDBY_PRESENT = 0x01
    RECHARGED_PRESENT = 0x02


class BatteryTimeStatus(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Battery Time Status characteristic.

    Attributes:
        flags: Raw 8-bit flags field.
        time_until_discharged: Estimated minutes until discharged.
            None if raw == 0xFFFFFF (Unknown).
        time_until_discharged_on_standby: Minutes until discharged on standby.
            None if absent or raw == 0xFFFFFF (Unknown).
        time_until_recharged: Minutes until recharged.
            None if absent or raw == 0xFFFFFF (Unknown).

    """

    flags: BatteryTimeStatusFlags
    time_until_discharged: int | None = None
    time_until_discharged_on_standby: int | None = None
    time_until_recharged: int | None = None

    def __post_init__(self) -> None:
        """Validate field ranges."""
        if self.time_until_discharged is not None and not 0 <= self.time_until_discharged <= UINT24_MAX:
            raise ValueError(f"Time until discharged must be 0-{UINT24_MAX}, got {self.time_until_discharged}")
        if (
            self.time_until_discharged_on_standby is not None
            and not 0 <= self.time_until_discharged_on_standby <= UINT24_MAX
        ):
            raise ValueError(
                f"Time until discharged on standby must be 0-{UINT24_MAX}, got {self.time_until_discharged_on_standby}"
            )
        if self.time_until_recharged is not None and not 0 <= self.time_until_recharged <= UINT24_MAX:
            raise ValueError(f"Time until recharged must be 0-{UINT24_MAX}, got {self.time_until_recharged}")


def _decode_time_minutes(data: bytearray, offset: int) -> tuple[int | None, int]:
    """Decode a uint24 time field in minutes with sentinel handling.

    Args:
        data: Raw BLE bytes.
        offset: Current read position.

    Returns:
        (value_or_none, new_offset).  Returns None for the 0xFFFFFF sentinel.

    """
    if len(data) < offset + 3:
        return None, offset
    raw = DataParser.parse_int24(data, offset, signed=False)
    if raw == _TIME_UNKNOWN:
        return None, offset + 3
    return raw, offset + 3


def _encode_time_minutes(value: int | None) -> bytearray:
    """Encode a time-in-minutes field to uint24, using sentinel for None.

    Args:
        value: Minutes value, or None for Unknown.

    Returns:
        3-byte encoded value.

    """
    if value is None:
        return DataParser.encode_int24(_TIME_UNKNOWN, signed=False)
    return DataParser.encode_int24(value, signed=False)


class BatteryTimeStatusCharacteristic(BaseCharacteristic[BatteryTimeStatus]):
    """Battery Time Status characteristic (0x2BEE).

    Reports estimated times for battery discharge and recharge.

    Flag-bit assignments (from GSS YAML):
        Bit 0: Time until Discharged on Standby present
        Bit 1: Time until Recharged present
        Bits 2-7: Reserved for Future Use

    The mandatory "Time until Discharged" field is always present after flags.

    """

    expected_type = BatteryTimeStatus
    min_length: int = 4  # 1 byte flags + 3 bytes mandatory time field
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> BatteryTimeStatus:
        """Parse Battery Time Status from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            BatteryTimeStatus with all present fields populated.

        """
        flags = BatteryTimeStatusFlags(DataParser.parse_int8(data, 0, signed=False))
        offset = 1

        # Mandatory: Time until Discharged (uint24, minutes)
        time_until_discharged, offset = _decode_time_minutes(data, offset)

        # Bit 0 -- Time until Discharged on Standby
        time_until_discharged_on_standby = None
        if flags & BatteryTimeStatusFlags.DISCHARGED_ON_STANDBY_PRESENT:
            time_until_discharged_on_standby, offset = _decode_time_minutes(data, offset)

        # Bit 1 -- Time until Recharged
        time_until_recharged = None
        if flags & BatteryTimeStatusFlags.RECHARGED_PRESENT:
            time_until_recharged, offset = _decode_time_minutes(data, offset)

        return BatteryTimeStatus(
            flags=flags,
            time_until_discharged=time_until_discharged,
            time_until_discharged_on_standby=time_until_discharged_on_standby,
            time_until_recharged=time_until_recharged,
        )

    def _encode_value(self, data: BatteryTimeStatus) -> bytearray:
        """Encode BatteryTimeStatus back to BLE bytes.

        Args:
            data: BatteryTimeStatus instance.

        Returns:
            Encoded bytearray matching the BLE wire format.

        """
        flags = BatteryTimeStatusFlags(0)

        if data.time_until_discharged_on_standby is not None:
            flags |= BatteryTimeStatusFlags.DISCHARGED_ON_STANDBY_PRESENT
        if data.time_until_recharged is not None:
            flags |= BatteryTimeStatusFlags.RECHARGED_PRESENT

        result = DataParser.encode_int8(int(flags), signed=False)

        # Mandatory: Time until Discharged
        result.extend(_encode_time_minutes(data.time_until_discharged))

        if data.time_until_discharged_on_standby is not None:
            result.extend(_encode_time_minutes(data.time_until_discharged_on_standby))
        if data.time_until_recharged is not None:
            result.extend(_encode_time_minutes(data.time_until_recharged))

        return result

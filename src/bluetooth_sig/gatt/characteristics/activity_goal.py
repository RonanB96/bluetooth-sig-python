"""Activity Goal characteristic (0x2B4E)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..constants import UINT16_MAX
from ..context import CharacteristicContext
from ..exceptions import InsufficientDataError, ValueRangeError
from .base import BaseCharacteristic
from .utils import DataParser


# Hard type for presence flags bit field
class ActivityGoalPresenceFlags(IntFlag):
    """Presence flags for Activity Goal characteristic."""

    TOTAL_ENERGY_EXPENDITURE = 1 << 0
    NORMAL_WALKING_STEPS = 1 << 1
    INTENSITY_STEPS = 1 << 2
    FLOOR_STEPS = 1 << 3
    DISTANCE = 1 << 4
    DURATION_NORMAL_WALKING = 1 << 5
    DURATION_INTENSITY_WALKING = 1 << 6


class ActivityGoalData(msgspec.Struct, frozen=True, kw_only=True):
    """Activity Goal data structure."""

    presence_flags: ActivityGoalPresenceFlags
    total_energy_expenditure: int | None = None
    normal_walking_steps: int | None = None
    intensity_steps: int | None = None
    floor_steps: int | None = None
    distance: int | None = None
    duration_normal_walking: int | None = None
    duration_intensity_walking: int | None = None


class ActivityGoalCharacteristic(BaseCharacteristic[ActivityGoalData]):
    """Activity Goal characteristic (0x2B4E).

    org.bluetooth.characteristic.activity_goal

    The Activity Goal characteristic is used to represent the goal or target of a user,
    such as number of steps or total energy expenditure, related to a physical activity session.
    """

    min_length: int = 1  # At least presence flags byte
    max_length: int = 22  # Max length with all optional fields present
    allow_variable_length: bool = True  # Variable based on presence flags

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ActivityGoalData:
        """Decode Activity Goal from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic
            ctx: Optional context for parsing

        Returns:
            ActivityGoalData: Parsed activity goal

        Raises:
            InsufficientDataError: If data is insufficient for parsing
        """  # pylint: disable=too-many-branches
        # NOTE: Required by Bluetooth SIG Activity Goal characteristic specification
        # Each branch corresponds to a mandatory presence flag check per spec
        # Refactoring would violate spec compliance and reduce readability

        presence_flags = data[0]

        # Start after presence flags
        pos = 1

        # Parse conditional fields based on presence flags
        total_energy_expenditure = None
        if presence_flags & ActivityGoalPresenceFlags.TOTAL_ENERGY_EXPENDITURE:
            if len(data) < pos + 2:
                raise InsufficientDataError("Activity Goal", data, pos + 2)
            total_energy_expenditure = DataParser.parse_int16(data, offset=pos, signed=False)
            pos += 2

        normal_walking_steps = None
        if presence_flags & ActivityGoalPresenceFlags.NORMAL_WALKING_STEPS:
            if len(data) < pos + 3:
                raise InsufficientDataError("Activity Goal", data, pos + 3)
            normal_walking_steps = DataParser.parse_int24(data, offset=pos, signed=False)
            pos += 3

        intensity_steps = None
        if presence_flags & ActivityGoalPresenceFlags.INTENSITY_STEPS:
            if len(data) < pos + 3:
                raise InsufficientDataError("Activity Goal", data, pos + 3)
            intensity_steps = DataParser.parse_int24(data, offset=pos, signed=False)
            pos += 3

        floor_steps = None
        if presence_flags & ActivityGoalPresenceFlags.FLOOR_STEPS:
            if len(data) < pos + 3:
                raise InsufficientDataError("Activity Goal", data, pos + 3)
            floor_steps = DataParser.parse_int24(data, offset=pos, signed=False)
            pos += 3

        distance = None
        if presence_flags & ActivityGoalPresenceFlags.DISTANCE:
            if len(data) < pos + 3:
                raise InsufficientDataError("Activity Goal", data, pos + 3)
            distance = DataParser.parse_int24(data, offset=pos, signed=False)
            pos += 3

        duration_normal_walking = None
        if presence_flags & ActivityGoalPresenceFlags.DURATION_NORMAL_WALKING:
            if len(data) < pos + 3:
                raise InsufficientDataError("Activity Goal", data, pos + 3)
            duration_normal_walking = DataParser.parse_int24(data, offset=pos, signed=False)
            pos += 3

        duration_intensity_walking = None
        if presence_flags & ActivityGoalPresenceFlags.DURATION_INTENSITY_WALKING:
            if len(data) < pos + 3:
                raise InsufficientDataError("Activity Goal", data, pos + 3)
            duration_intensity_walking = DataParser.parse_int24(data, offset=pos, signed=False)
            pos += 3

        return ActivityGoalData(
            presence_flags=ActivityGoalPresenceFlags(presence_flags),
            total_energy_expenditure=total_energy_expenditure,
            normal_walking_steps=normal_walking_steps,
            intensity_steps=intensity_steps,
            floor_steps=floor_steps,
            distance=distance,
            duration_normal_walking=duration_normal_walking,
            duration_intensity_walking=duration_intensity_walking,
        )

    def _encode_value(self, data: ActivityGoalData) -> bytearray:
        """Encode Activity Goal to raw bytes.

        Args:
            data: ActivityGoalData to encode

        Returns:
            bytearray: Encoded bytes
        """  # pylint: disable=too-many-branches
        # NOTE: Required by Bluetooth SIG Activity Goal characteristic specification
        # Each branch corresponds to a mandatory presence flag encoding per spec
        # Refactoring would violate spec compliance and reduce readability
        result = bytearray()

        result.append(data.presence_flags)

        # Encode conditional fields based on presence flags
        if data.presence_flags & ActivityGoalPresenceFlags.TOTAL_ENERGY_EXPENDITURE:
            if data.total_energy_expenditure is None:
                raise ValueRangeError("total_energy_expenditure", data.total_energy_expenditure, 0, UINT16_MAX)
            if not 0 <= data.total_energy_expenditure <= UINT16_MAX:
                raise ValueRangeError("total_energy_expenditure", data.total_energy_expenditure, 0, UINT16_MAX)
            result.extend(data.total_energy_expenditure.to_bytes(2, byteorder="little", signed=False))

        if data.presence_flags & ActivityGoalPresenceFlags.NORMAL_WALKING_STEPS:
            if data.normal_walking_steps is None:
                raise ValueRangeError("normal_walking_steps", data.normal_walking_steps, 0, UINT16_MAX)
            if not 0 <= data.normal_walking_steps <= UINT16_MAX:
                raise ValueRangeError("normal_walking_steps", data.normal_walking_steps, 0, UINT16_MAX)
            result.extend(data.normal_walking_steps.to_bytes(3, byteorder="little", signed=False))

        if data.presence_flags & ActivityGoalPresenceFlags.INTENSITY_STEPS:
            if data.intensity_steps is None:
                raise ValueRangeError("intensity_steps", data.intensity_steps, 0, UINT16_MAX)
            if not 0 <= data.intensity_steps <= UINT16_MAX:
                raise ValueRangeError("intensity_steps", data.intensity_steps, 0, UINT16_MAX)
            result.extend(data.intensity_steps.to_bytes(3, byteorder="little", signed=False))

        if data.presence_flags & ActivityGoalPresenceFlags.FLOOR_STEPS:
            if data.floor_steps is None:
                raise ValueRangeError("floor_steps", data.floor_steps, 0, UINT16_MAX)
            if not 0 <= data.floor_steps <= UINT16_MAX:
                raise ValueRangeError("floor_steps", data.floor_steps, 0, UINT16_MAX)
            result.extend(data.floor_steps.to_bytes(3, byteorder="little", signed=False))

        if data.presence_flags & ActivityGoalPresenceFlags.DISTANCE:
            if data.distance is None:
                raise ValueRangeError("distance", data.distance, 0, UINT16_MAX)
            if not 0 <= data.distance <= UINT16_MAX:
                raise ValueRangeError("distance", data.distance, 0, UINT16_MAX)
            result.extend(data.distance.to_bytes(3, byteorder="little", signed=False))

        if data.presence_flags & ActivityGoalPresenceFlags.DURATION_NORMAL_WALKING:
            if data.duration_normal_walking is None:
                raise ValueRangeError("duration_normal_walking", data.duration_normal_walking, 0, UINT16_MAX)
            if not 0 <= data.duration_normal_walking <= UINT16_MAX:
                raise ValueRangeError("duration_normal_walking", data.duration_normal_walking, 0, UINT16_MAX)
            result.extend(data.duration_normal_walking.to_bytes(3, byteorder="little", signed=False))

        if data.presence_flags & ActivityGoalPresenceFlags.DURATION_INTENSITY_WALKING:
            if data.duration_intensity_walking is None:
                raise ValueRangeError("duration_intensity_walking", data.duration_intensity_walking, 0, UINT16_MAX)
            if not 0 <= data.duration_intensity_walking <= UINT16_MAX:
                raise ValueRangeError("duration_intensity_walking", data.duration_intensity_walking, 0, UINT16_MAX)
            result.extend(data.duration_intensity_walking.to_bytes(3, byteorder="little", signed=False))

        return result

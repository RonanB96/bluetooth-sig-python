"""Composite multi-field templates for time and vector data.

Covers TimeDataTemplate, VectorTemplate, and Vector2DTemplate.
These templates handle multi-field structures and do NOT expose extractor/translator
since there is no single raw value to intercept.
"""

from __future__ import annotations

from ....types.gatt_enums import AdjustReason, DayOfWeek
from ...context import CharacteristicContext
from ...exceptions import InsufficientDataError, ValueRangeError
from ..utils import DataParser, IEEE11073Parser
from .base import CodingTemplate
from .data_structures import TimeData, Vector2DData, VectorData


class TimeDataTemplate(CodingTemplate[TimeData]):
    """Template for Bluetooth SIG time data parsing (10 bytes).

    Used for Current Time and Time with DST characteristics.
    Structure: Date Time (7 bytes) + Day of Week (1) + Fractions256 (1) + Adjust Reason (1)
    """

    LENGTH = 10
    DAY_OF_WEEK_MAX = 7
    FRACTIONS256_MAX = 255
    ADJUST_REASON_MAX = 255

    @property
    def data_size(self) -> int:
        """Size: 10 bytes."""
        return self.LENGTH

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> TimeData:
        """Parse time data from bytes."""
        if validate and len(data) < offset + self.LENGTH:
            raise InsufficientDataError("time data", data[offset:], self.LENGTH)

        # Parse Date Time (7 bytes)
        year = DataParser.parse_int16(data, offset, signed=False)
        month = data[offset + 2]
        day = data[offset + 3]

        date_time = None if year == 0 or month == 0 or day == 0 else IEEE11073Parser.parse_timestamp(data, offset)

        # Parse Day of Week (1 byte)
        day_of_week_raw = data[offset + 7]
        if validate and day_of_week_raw > self.DAY_OF_WEEK_MAX:
            raise ValueRangeError("day_of_week", day_of_week_raw, 0, self.DAY_OF_WEEK_MAX)
        day_of_week = DayOfWeek(day_of_week_raw)

        # Parse Fractions256 (1 byte)
        fractions256 = data[offset + 8]

        # Parse Adjust Reason (1 byte)
        adjust_reason = AdjustReason.from_raw(data[offset + 9])

        return TimeData(
            date_time=date_time, day_of_week=day_of_week, fractions256=fractions256, adjust_reason=adjust_reason
        )

    def encode_value(self, value: TimeData, *, validate: bool = True) -> bytearray:
        """Encode time data to bytes."""
        result = bytearray()

        # Encode Date Time (7 bytes)
        if value.date_time is None:
            result.extend(bytearray(IEEE11073Parser.TIMESTAMP_LENGTH))
        else:
            result.extend(IEEE11073Parser.encode_timestamp(value.date_time))

        # Encode Day of Week (1 byte)
        day_of_week_value = int(value.day_of_week)
        if validate and day_of_week_value > self.DAY_OF_WEEK_MAX:
            raise ValueRangeError("day_of_week", day_of_week_value, 0, self.DAY_OF_WEEK_MAX)
        result.append(day_of_week_value)

        # Encode Fractions256 (1 byte)
        if validate and value.fractions256 > self.FRACTIONS256_MAX:
            raise ValueRangeError("fractions256", value.fractions256, 0, self.FRACTIONS256_MAX)
        result.append(value.fractions256)

        # Encode Adjust Reason (1 byte)
        if validate and int(value.adjust_reason) > self.ADJUST_REASON_MAX:
            raise ValueRangeError("adjust_reason", int(value.adjust_reason), 0, self.ADJUST_REASON_MAX)
        result.append(int(value.adjust_reason))

        return result


class VectorTemplate(CodingTemplate[VectorData]):
    """Template for 3D vector measurements (x, y, z float32 components)."""

    @property
    def data_size(self) -> int:
        """Size: 12 bytes (3 x float32)."""
        return 12

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VectorData:
        """Parse 3D vector data."""
        if validate and len(data) < offset + 12:
            raise InsufficientDataError("3D vector", data[offset:], 12)

        x_axis = DataParser.parse_float32(data, offset)
        y_axis = DataParser.parse_float32(data, offset + 4)
        z_axis = DataParser.parse_float32(data, offset + 8)

        return VectorData(x_axis=x_axis, y_axis=y_axis, z_axis=z_axis)

    def encode_value(self, value: VectorData, *, validate: bool = True) -> bytearray:
        """Encode 3D vector data to bytes."""
        result = bytearray()
        result.extend(DataParser.encode_float32(value.x_axis))
        result.extend(DataParser.encode_float32(value.y_axis))
        result.extend(DataParser.encode_float32(value.z_axis))
        return result


class Vector2DTemplate(CodingTemplate[Vector2DData]):
    """Template for 2D vector measurements (x, y float32 components)."""

    @property
    def data_size(self) -> int:
        """Size: 8 bytes (2 x float32)."""
        return 8

    def decode_value(
        self, data: bytearray, offset: int = 0, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> Vector2DData:
        """Parse 2D vector data."""
        if validate and len(data) < offset + 8:
            raise InsufficientDataError("2D vector", data[offset:], 8)

        x_axis = DataParser.parse_float32(data, offset)
        y_axis = DataParser.parse_float32(data, offset + 4)

        return Vector2DData(x_axis=x_axis, y_axis=y_axis)

    def encode_value(self, value: Vector2DData, *, validate: bool = True) -> bytearray:
        """Encode 2D vector data to bytes."""
        result = bytearray()
        result.extend(DataParser.encode_float32(value.x_axis))
        result.extend(DataParser.encode_float32(value.y_axis))
        return result

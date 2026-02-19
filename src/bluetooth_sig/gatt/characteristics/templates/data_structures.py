"""Data structures used by templates.

Frozen msgspec.Struct types for structured template return values.
"""

from __future__ import annotations

from datetime import datetime

import msgspec

from ....types.gatt_enums import AdjustReason, DayOfWeek


class VectorData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """3D vector measurement data."""

    x_axis: float
    y_axis: float
    z_axis: float


class Vector2DData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """2D vector measurement data."""

    x_axis: float
    y_axis: float


class TimeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Time characteristic data structure."""

    date_time: datetime | None
    day_of_week: DayOfWeek
    fractions256: int
    adjust_reason: AdjustReason

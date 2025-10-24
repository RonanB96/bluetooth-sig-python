"""Observation Schedule Descriptor implementation."""

from __future__ import annotations

import msgspec

from .base import BaseDescriptor


class ObservationScheduleData(msgspec.Struct, frozen=True, kw_only=True):
    """Observation Schedule descriptor data."""

    schedule: bytes  # Variable format depending on sensor type


class ObservationScheduleDescriptor(BaseDescriptor):
    """Observation Schedule Descriptor (0x2910).

    Defines the observation schedule for sensor measurements.
    Format varies depending on the sensor type and requirements.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "bytes"

    def _parse_descriptor_value(self, data: bytes) -> ObservationScheduleData:
        """Parse Observation Schedule value.

        Args:
            data: Raw schedule data (variable length)

        Returns:
            ObservationScheduleData with schedule information
        """
        return ObservationScheduleData(schedule=data)

    def get_schedule_data(self, data: bytes) -> bytes:
        """Get the raw schedule data."""
        parsed = self._parse_descriptor_value(data)
        return parsed.schedule

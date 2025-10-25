"""Measurement Description Descriptor implementation."""

from __future__ import annotations

import msgspec

from .base import BaseDescriptor


class MeasurementDescriptionData(msgspec.Struct, frozen=True, kw_only=True):
    """Measurement Description descriptor data."""

    description: str


class MeasurementDescriptionDescriptor(BaseDescriptor):
    """Measurement Description Descriptor (0x2912).

    Contains a human-readable description of the measurement.
    UTF-8 encoded string describing what the measurement represents.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "utf8"

    def _parse_descriptor_value(self, data: bytes) -> MeasurementDescriptionData:
        """Parse Measurement Description value.

        Args:
            data: Raw UTF-8 bytes

        Returns:
            MeasurementDescriptionData with the description string
        """
        try:
            description = data.decode("utf-8")
            return MeasurementDescriptionData(description=description)
        except UnicodeDecodeError as e:
            raise ValueError(f"Invalid UTF-8 data in Measurement Description: {e}") from e

    def get_description(self, data: bytes) -> str:
        """Get the measurement description string."""
        parsed = self._parse_descriptor_value(data)
        return parsed.description

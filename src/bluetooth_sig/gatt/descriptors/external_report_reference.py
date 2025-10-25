"""External Report Reference Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class ExternalReportReferenceData(msgspec.Struct, frozen=True, kw_only=True):
    """External Report Reference descriptor data."""

    external_report_id: int


class ExternalReportReferenceDescriptor(BaseDescriptor):
    """External Report Reference Descriptor (0x2907).

    References an external report by ID.
    Used in HID (Human Interface Device) profiles.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "uint16"

    def _parse_descriptor_value(self, data: bytes) -> ExternalReportReferenceData:
        """Parse External Report Reference value.

        Args:
            data: Raw bytes (should be 2 bytes for uint16)

        Returns:
            ExternalReportReferenceData with external report ID

        Raises:
            ValueError: If data is not exactly 2 bytes
        """
        if len(data) != 2:
            raise ValueError(f"External Report Reference data must be exactly 2 bytes, got {len(data)}")

        external_report_id = DataParser.parse_int16(data, endian="little")

        return ExternalReportReferenceData(external_report_id=external_report_id)

    def get_external_report_id(self, data: bytes) -> int:
        """Get the external report ID."""
        parsed = self._parse_descriptor_value(data)
        return parsed.external_report_id

"""Report Reference Descriptor implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class ReportType(IntEnum):
    """Report type values for Report Reference descriptor."""

    INPUT_REPORT = 0x01
    OUTPUT_REPORT = 0x02
    FEATURE_REPORT = 0x03


class ReportReferenceData(msgspec.Struct, frozen=True, kw_only=True):
    """Report Reference descriptor data."""

    report_id: int
    report_type: int


class ReportReferenceDescriptor(BaseDescriptor):
    """Report Reference Descriptor (0x2908).

    Contains report ID and report type information.
    Used in HID (Human Interface Device) profiles.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "struct"

    def _parse_descriptor_value(self, data: bytes) -> ReportReferenceData:
        """Parse Report Reference value.

        Format: 2 bytes
        - Report ID (1 byte)
        - Report Type (1 byte)

        Args:
            data: Raw bytes (should be 2 bytes)

        Returns:
            ReportReferenceData with report ID and type

        Raises:
            ValueError: If data is not exactly 2 bytes
        """
        if len(data) != 2:
            raise ValueError(f"Report Reference data must be exactly 2 bytes, got {len(data)}")

        return ReportReferenceData(
            report_id=DataParser.parse_int8(data, offset=0),
            report_type=DataParser.parse_int8(data, offset=1),
        )

    def get_report_id(self, data: bytes) -> int:
        """Get the report ID."""
        parsed = self._parse_descriptor_value(data)
        return parsed.report_id

    def get_report_type(self, data: bytes) -> int:
        """Get the report type."""
        parsed = self._parse_descriptor_value(data)
        return parsed.report_type

    def is_input_report(self, data: bytes) -> bool:
        """Check if this is an input report."""
        return self.get_report_type(data) == ReportType.INPUT_REPORT

    def is_output_report(self, data: bytes) -> bool:
        """Check if this is an output report."""
        return self.get_report_type(data) == ReportType.OUTPUT_REPORT

    def is_feature_report(self, data: bytes) -> bool:
        """Check if this is a feature report."""
        return self.get_report_type(data) == ReportType.FEATURE_REPORT

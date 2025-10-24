"""Complete BR-EDR Transport Block Data Descriptor implementation."""

from __future__ import annotations

import msgspec

from .base import BaseDescriptor


class CompleteBREDRTransportBlockDataData(msgspec.Struct, frozen=True, kw_only=True):
    """Complete BR-EDR Transport Block Data descriptor data."""

    transport_data: bytes


class CompleteBREDRTransportBlockDataDescriptor(BaseDescriptor):
    """Complete BR-EDR Transport Block Data Descriptor (0x290F).

    Contains complete BR-EDR transport block data.
    Used for transporting large data blocks over BR-EDR.
    """

    _descriptor_name = "Complete BR-EDR Transport Block Data"

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "bytes"

    def _parse_descriptor_value(self, data: bytes) -> CompleteBREDRTransportBlockDataData:
        """Parse Complete BR-EDR Transport Block Data value.

        Args:
            data: Raw transport block data

        Returns:
            CompleteBREDRTransportBlockDataData with transport data
        """
        return CompleteBREDRTransportBlockDataData(transport_data=data)

    def get_transport_data(self, data: bytes) -> bytes:
        """Get the transport block data."""
        parsed = self._parse_descriptor_value(data)
        return parsed.transport_data

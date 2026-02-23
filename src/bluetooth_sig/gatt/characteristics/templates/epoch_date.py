"""Epoch-date template returning ``datetime.date`` for BLE date characteristics.

Wraps a 24-bit unsigned integer (days since 1970-01-01) and converts to/from
:class:`datetime.date` so callers receive a proper Python date type.
"""

from __future__ import annotations

from datetime import date, timedelta

from ...context import CharacteristicContext
from ...exceptions import InsufficientDataError
from ..utils.extractors import UINT24, RawExtractor
from .base import CodingTemplate

_EPOCH = date(1970, 1, 1)


class EpochDateTemplate(CodingTemplate[date]):
    """Template for epoch-day date characteristics that return ``datetime.date``.

    The raw wire value is a 24-bit unsigned integer counting the number of
    days elapsed since 1970-01-01 (the Unix epoch).

    Pipeline Integration:
        bytes → [UINT24 extractor] → day_count → date(1970,1,1) + timedelta(days=…)

    Examples:
        >>> template = EpochDateTemplate()
        >>> template.decode_value(bytearray([0x61, 0x4D, 0x00]))
        datetime.date(2024, 2, 19)
    """

    @property
    def data_size(self) -> int:
        """Size: 3 bytes (uint24)."""
        return 3

    @property
    def extractor(self) -> RawExtractor:
        """Return uint24 extractor for pipeline access."""
        return UINT24

    def decode_value(
        self,
        data: bytearray,
        offset: int = 0,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> date:
        """Decode 24-bit day count to ``datetime.date``.

        Args:
            data: Raw bytes from BLE characteristic.
            offset: Starting offset in data buffer.
            ctx: Optional context for parsing.
            validate: Whether to validate data length (default True).

        Returns:
            ``datetime.date`` representing the decoded date.

        Raises:
            InsufficientDataError: If data too short.

        """
        if validate and len(data) < offset + self.data_size:
            raise InsufficientDataError("EpochDate", data[offset:], self.data_size)

        days = UINT24.extract(data, offset)
        return _EPOCH + timedelta(days=days)

    def encode_value(self, value: date | int, *, validate: bool = True) -> bytearray:
        """Encode ``datetime.date`` (or raw day count) to 3 bytes.

        Args:
            value: ``datetime.date`` or integer day count since epoch.
            validate: Whether to validate (default True).

        Returns:
            Encoded bytes (3 bytes, little-endian).

        """
        days = (value - _EPOCH).days if isinstance(value, date) else int(value)

        if validate and days < 0:
            raise ValueError(f"Date {value} is before epoch (1970-01-01)")

        return UINT24.pack(days)

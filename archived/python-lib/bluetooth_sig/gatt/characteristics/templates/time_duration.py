"""Time-duration template returning ``timedelta`` for BLE time characteristics.

Wraps a numeric extractor and converts raw integer counts (seconds,
milliseconds, hours, …) into :class:`datetime.timedelta` instances so
that callers receive a proper Python time type instead of a plain ``int``.
"""

from __future__ import annotations

import math
from datetime import timedelta

from ...context import CharacteristicContext
from ...exceptions import InsufficientDataError
from ..utils.extractors import (
    UINT8,
    UINT16,
    UINT24,
    UINT32,
    RawExtractor,
)
from .base import CodingTemplate


class TimeDurationTemplate(CodingTemplate[timedelta]):
    r"""Template for time-duration characteristics that return ``timedelta``.

    Encodes/decodes a raw integer count in a given time unit (seconds,
    milliseconds, hours, ...) to/from a ``timedelta``.

    Pipeline Integration:
        bytes -> [extractor] -> raw_int -> x scale -> timedelta(seconds=...)

    Examples:
        >>> template = TimeDurationTemplate.seconds_uint16()
        >>> template.decode_value(bytearray([0x2A, 0x00]))
        datetime.timedelta(seconds=42)
        >>>
        >>> template.encode_value(timedelta(seconds=42))
        bytearray(b'*\\x00')
    """

    def __init__(
        self,
        extractor: RawExtractor,
        *,
        seconds_per_unit: float = 1.0,
    ) -> None:
        """Initialise with extractor and time-unit conversion factor.

        Args:
            extractor: Raw extractor defining byte size and signedness.
            seconds_per_unit: How many seconds one raw count represents.
                              E.g. ``1.0`` for seconds, ``0.001`` for ms,
                              ``3600.0`` for hours, ``360.0`` for deci-hours.

        """
        self._extractor = extractor
        self._seconds_per_unit = seconds_per_unit

    @property
    def data_size(self) -> int:
        """Return byte size required for encoding."""
        return self._extractor.byte_size

    @property
    def extractor(self) -> RawExtractor:
        """Return extractor for pipeline access."""
        return self._extractor

    def decode_value(
        self,
        data: bytearray,
        offset: int = 0,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> timedelta:
        """Decode bytes to ``timedelta``.

        Args:
            data: Raw bytes from BLE characteristic.
            offset: Starting offset in data buffer.
            ctx: Optional context for parsing.
            validate: Whether to validate data length (default True).

        Returns:
            ``timedelta`` representing the decoded duration.

        Raises:
            InsufficientDataError: If data too short for required byte size.

        """
        if validate and len(data) < offset + self.data_size:
            raise InsufficientDataError("TimeDuration", data[offset:], self.data_size)

        raw = self._extractor.extract(data, offset)
        return timedelta(seconds=raw * self._seconds_per_unit)

    def encode_value(self, value: timedelta | int | float, *, validate: bool = True) -> bytearray:
        """Encode ``timedelta`` (or numeric seconds) to bytes.

        Args:
            value: ``timedelta``, or a numeric value treated as the raw count.
            validate: Whether to validate (default True).

        Returns:
            Encoded bytes.

        """
        raw = round(value.total_seconds() / self._seconds_per_unit) if isinstance(value, timedelta) else int(value)

        return self._extractor.pack(raw)

    # -----------------------------------------------------------------
    # Factory methods
    # -----------------------------------------------------------------

    @classmethod
    def seconds_uint8(cls) -> TimeDurationTemplate:
        """1-byte unsigned, 1-second resolution."""
        return cls(UINT8, seconds_per_unit=1.0)

    @classmethod
    def seconds_uint16(cls) -> TimeDurationTemplate:
        """2-byte unsigned, 1-second resolution."""
        return cls(UINT16, seconds_per_unit=1.0)

    @classmethod
    def seconds_uint24(cls) -> TimeDurationTemplate:
        """3-byte unsigned, 1-second resolution."""
        return cls(UINT24, seconds_per_unit=1.0)

    @classmethod
    def seconds_uint32(cls) -> TimeDurationTemplate:
        """4-byte unsigned, 1-second resolution."""
        return cls(UINT32, seconds_per_unit=1.0)

    @classmethod
    def milliseconds_uint24(cls) -> TimeDurationTemplate:
        """3-byte unsigned, 1-millisecond resolution."""
        return cls(UINT24, seconds_per_unit=0.001)

    @classmethod
    def hours_uint24(cls) -> TimeDurationTemplate:
        """3-byte unsigned, 1-hour resolution."""
        return cls(UINT24, seconds_per_unit=3600.0)

    @classmethod
    def decihours_uint8(cls) -> TimeDurationTemplate:
        """1-byte unsigned, 0.1-hour (6-minute) resolution."""
        return cls(UINT8, seconds_per_unit=360.0)


class TimeExponentialTemplate(CodingTemplate[timedelta]):
    """Template for exponentially-encoded time (Time Exponential 8).

    Encoding: ``value = 1.1^(N - 64)`` seconds.
    Special values: ``0x00`` = 0 s, ``0xFE`` = device lifetime, ``0xFF`` = unknown.
    """

    @property
    def data_size(self) -> int:
        """Size: 1 byte."""
        return 1

    @property
    def extractor(self) -> RawExtractor:
        """Return uint8 extractor for pipeline access."""
        return UINT8

    def decode_value(
        self,
        data: bytearray,
        offset: int = 0,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> timedelta:
        """Decode exponentially-encoded time to ``timedelta``.

        Args:
            data: Raw bytes from BLE characteristic.
            offset: Starting offset in data buffer.
            ctx: Optional context for parsing.
            validate: Whether to validate data length (default True).

        Returns:
            ``timedelta`` representing the decoded duration.

        Raises:
            InsufficientDataError: If data too short.

        """
        if validate and len(data) < offset + self.data_size:
            raise InsufficientDataError("TimeExponential8", data[offset:], 1)

        raw = UINT8.extract(data, offset)
        if raw == 0:
            return timedelta(seconds=0)
        seconds = 1.1 ** (raw - 64)
        return timedelta(seconds=seconds)

    def encode_value(self, value: timedelta | float, *, validate: bool = True) -> bytearray:
        """Encode a time duration using exponential encoding.

        Args:
            value: ``timedelta`` or numeric seconds.
            validate: Whether to validate (default True).

        Returns:
            Encoded byte.

        """
        seconds = value.total_seconds() if isinstance(value, timedelta) else float(value)

        if seconds <= 0.0:
            return UINT8.pack(0)

        n = round(math.log(seconds) / math.log(1.1) + 64)
        n = max(1, min(n, 0xFD))
        return UINT8.pack(n)

#!/usr/bin/env python3
"""Typed models used by the examples utilities.

These small dataclasses provide a clear, typed surface for example
helpers to return structured data instead of opaque tuples and dicts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Union


@dataclass
class ReadResult:
    """Structured result for a single characteristic read.

    Attributes:
        raw_data: Raw bytes read from the characteristic.
        read_time: Time taken to read (seconds) or a timestamp depending on
            the caller's convention. Examples use elapsed time.
        parsed: Result of parsing via BluetoothSIGTranslator (if set).
        error: Optional string describing any error encountered while
            reading or parsing.
    """

    raw_data: bytes
    read_time: float
    parsed: Any | None = None
    error: str | None = None


@dataclass
class DeviceInfo:
    """Structured information about a discovered BLE device.

    Keep this small and stable for example callers; adapters may provide
    richer objects but examples should normalise them to this shape.
    """

    name: str | None
    address: str
    rssi: int | None
    raw: Any | None = None


__all__ = ["ReadResult", "DeviceInfo"]


ComparisonData = Union[dict[str, ReadResult], dict[str, Any]]


@dataclass
class LibraryComparisonResult:
    """Structured result for library comparison demo helpers.

    Attributes:
        status: Short status string (e.g. 'ok', 'not_implemented', 'failed')
        data: Optional payload produced by the library (e.g. reads or discovery)
        note: Optional human-friendly note for display
    """

    status: str
    data: ComparisonData | None = None
    note: str | None = None


__all__.extend(["LibraryComparisonResult", "ComparisonData"])

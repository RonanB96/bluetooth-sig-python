"""Stream helpers for pairing dependent characteristic notifications.

This module provides a generic, backend-agnostic buffer that correlates
dependent characteristic notifications based on caller-defined grouping keys.
Useful for Bluetooth SIG profiles where characteristics must be paired by
sequence numbers, timestamps, or other identifiers.

"""

from __future__ import annotations

import time
from collections.abc import Callable, Hashable
from typing import Any

import msgspec

from ..core.translator import BluetoothSIGTranslator


class BufferStats(msgspec.Struct, frozen=True, kw_only=True):
    """Snapshot of pairing buffer statistics.

    Attributes:
        pending: Number of incomplete groups currently buffered.
        completed: Total number of groups successfully paired since creation.
        evicted: Total number of groups evicted due to TTL expiry since creation.
    """

    pending: int
    completed: int
    evicted: int


class DependencyPairingBuffer:
    """Buffer and pair dependent characteristic notifications.

    Buffers incoming notifications until all required UUIDs for a grouping key
    are present, then batch-parses and invokes the callback. Order-independent.

    Args:
        translator: BluetoothSIGTranslator instance for parsing characteristics.
        required_uuids: Set of UUID strings that must be present to form a complete pair.
        group_key: Function that extracts a grouping key from each parsed notification.
            Called as ``group_key(uuid, parsed_result)`` and must return a hashable value.
        on_pair: Callback invoked with complete parsed pairs as
            ``on_pair(results: dict[str, Any])``.
        max_age_seconds: Maximum age in seconds for buffered groups before eviction.
            ``None`` disables TTL eviction (default).
        clock: Callable returning current time as a float (seconds). Defaults to
            ``time.monotonic``. Override in tests for deterministic timing.

    Note:
        Does not manage BLE subscriptions. Callers handle connection and notification setup.
    """

    def __init__(
        self,
        *,
        translator: BluetoothSIGTranslator,
        required_uuids: set[str],
        group_key: Callable[[str, Any], Hashable],
        on_pair: Callable[[dict[str, Any]], None],
        max_age_seconds: float | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialize the pairing buffer."""
        self._translator = translator
        self._required = set(required_uuids)
        self._group_key = group_key
        self._on_pair = on_pair
        self._max_age_seconds = max_age_seconds
        self._clock = clock
        self._buffer: dict[Hashable, dict[str, bytes]] = {}
        self._group_timestamps: dict[Hashable, float] = {}
        self._completed_count: int = 0
        self._evicted_count: int = 0

    def ingest(self, uuid: str, data: bytes) -> None:
        """Ingest a single characteristic notification.

        Evicts stale groups (if TTL is configured) before processing.

        Args:
            uuid: Characteristic UUID string (16-bit or 128-bit).
            data: Raw bytes from the characteristic notification.
        """
        self._evict_stale()

        parsed = self._translator.parse_characteristic(uuid, data)
        group_id = self._group_key(uuid, parsed)

        group = self._buffer.setdefault(group_id, {})
        if group_id not in self._group_timestamps:
            self._group_timestamps[group_id] = self._clock()
        group[uuid] = data

        if self._required.issubset(group.keys()):
            batch = dict(group)
            del self._buffer[group_id]
            del self._group_timestamps[group_id]
            self._completed_count += 1

            results = self._translator.parse_characteristics(batch)
            self._on_pair(results)

    def stats(self) -> BufferStats:
        """Return a snapshot of buffer statistics.

        Returns:
            BufferStats with current pending count and lifetime completed/evicted totals.
        """
        return BufferStats(
            pending=len(self._buffer),
            completed=self._completed_count,
            evicted=self._evicted_count,
        )

    def _evict_stale(self) -> None:
        """Remove groups older than max_age_seconds."""
        if self._max_age_seconds is None:
            return

        now = self._clock()
        cutoff = now - self._max_age_seconds
        stale_keys = [key for key, timestamp in self._group_timestamps.items() if timestamp <= cutoff]

        for key in stale_keys:
            del self._buffer[key]
            del self._group_timestamps[key]
            self._evicted_count += 1

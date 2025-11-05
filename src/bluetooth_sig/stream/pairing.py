"""Stream helpers for pairing dependent characteristic notifications.

This module provides a generic, backend-agnostic buffer that correlates
dependent characteristic notifications based on caller-defined grouping keys.
Useful for Bluetooth SIG profiles where characteristics must be paired by
sequence numbers, timestamps, or other identifiers.

"""

from __future__ import annotations

from collections.abc import Hashable
from typing import Callable

from ..core.translator import BluetoothSIGTranslator
from ..types import CharacteristicData


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
            ``on_pair(results: dict[str, CharacteristicData])``.

    Note:
        Does not manage BLE subscriptions. Callers handle connection and notification setup.
    """

    def __init__(
        self,
        *,
        translator: BluetoothSIGTranslator,
        required_uuids: set[str],
        group_key: Callable[[str, CharacteristicData], Hashable],
        on_pair: Callable[[dict[str, CharacteristicData]], None],
    ) -> None:
        """Initialize the pairing buffer."""
        self._translator = translator
        self._required = set(required_uuids)
        self._group_key = group_key
        self._on_pair = on_pair
        self._buffer: dict[Hashable, dict[str, bytes]] = {}

    def ingest(self, uuid: str, data: bytes) -> None:
        """Ingest a single characteristic notification.

        Args:
            uuid: Characteristic UUID string (16-bit or 128-bit).
            data: Raw bytes from the characteristic notification.
        """
        parsed = self._translator.parse_characteristic(uuid, data)
        group_id = self._group_key(uuid, parsed)

        group = self._buffer.setdefault(group_id, {})
        group[uuid] = data

        if self._required.issubset(group.keys()):
            batch = dict(group)
            del self._buffer[group_id]

            results = self._translator.parse_characteristics(batch)
            self._on_pair(results)

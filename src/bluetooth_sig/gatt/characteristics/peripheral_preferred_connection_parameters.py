"""Peripheral Preferred Connection Parameters characteristic implementation."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ConnectionParametersData(msgspec.Struct, frozen=True, kw_only=True):
    """Connection parameters data.

    Attributes:
        min_interval: Minimum connection interval in ms
        max_interval: Maximum connection interval in ms
        latency: Slave latency (number of events)
        timeout: Connection supervision timeout in ms
    """

    min_interval: float
    max_interval: float
    latency: int
    timeout: int


class PeripheralPreferredConnectionParametersCharacteristic(BaseCharacteristic):
    """Peripheral Preferred Connection Parameters characteristic (0x2A04).

    org.bluetooth.characteristic.gap.peripheral_preferred_connection_parameters

    Contains the preferred connection parameters (8 bytes).
    """

    _manual_value_type = "ConnectionParametersData"
    expected_length = 8

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ConnectionParametersData:
        """Parse connection parameters.

        Args:
            data: Raw bytearray (8 bytes).
            ctx: Optional CharacteristicContext.

        Returns:
            ConnectionParametersData with min_interval, max_interval, latency, timeout.
        """
        min_interval_raw = DataParser.parse_int16(data, 0, signed=False)
        max_interval_raw = DataParser.parse_int16(data, 2, signed=False)
        latency = DataParser.parse_int16(data, 4, signed=False)
        timeout_raw = DataParser.parse_int16(data, 6, signed=False)

        return ConnectionParametersData(
            min_interval=min_interval_raw * 1.25,
            max_interval=max_interval_raw * 1.25,
            latency=latency,
            timeout=timeout_raw * 10,
        )

    def encode_value(self, data: ConnectionParametersData) -> bytearray:
        """Encode connection parameters.

        Args:
            data: ConnectionParametersData to encode

        Returns:
            Encoded bytes
        """
        result = bytearray()
        result.extend(DataParser.encode_int16(int(data.min_interval / 1.25), signed=False))
        result.extend(DataParser.encode_int16(int(data.max_interval / 1.25), signed=False))
        result.extend(DataParser.encode_int16(data.latency, signed=False))
        result.extend(DataParser.encode_int16(int(data.timeout / 10), signed=False))
        return result

"""Appearance characteristic implementation."""

from __future__ import annotations

from ...registry.core.appearance_values import appearance_values_registry
from ...types.appearance import AppearanceData
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class AppearanceCharacteristic(BaseCharacteristic[AppearanceData]):
    """Appearance characteristic (0x2A01).

    org.bluetooth.characteristic.gap.appearance

    Appearance characteristic with human-readable device type information.
    """

    _manual_value_type = "AppearanceData"
    expected_length = 2

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> AppearanceData:
        """Parse appearance value with human-readable info.

        Args:
            data: Raw bytearray from BLE characteristic (2 bytes).
            ctx: Optional CharacteristicContext providing surrounding context (may be None).
            validate: Whether to validate ranges (default True)

        Returns:
            AppearanceData with raw value and optional human-readable info.
        """
        raw_value = DataParser.parse_int16(data, 0, signed=False)
        appearance_info = appearance_values_registry.get_appearance_info(raw_value)

        return AppearanceData(
            raw_value=raw_value,
            info=appearance_info,
        )

    def _encode_value(self, data: AppearanceData) -> bytearray:
        """Encode appearance value back to bytes.

        Args:
            data: Appearance value as AppearanceData


        Returns:
            Encoded bytes representing the appearance
        """
        return DataParser.encode_int16(data.raw_value, signed=False)

"""PLX Features characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

from bluetooth_sig.gatt.context import CharacteristicContext

from .base import BaseCharacteristic
from .utils import DataParser


class PLXFeatureFlags(IntFlag):
    """PLX Features flags per Bluetooth SIG specification.

    Spec: Bluetooth SIG Assigned Numbers, PLX Features characteristic
    """

    MEASUREMENT_STATUS_SUPPORT = 0x0001
    DEVICE_AND_SENSOR_STATUS_SUPPORT = 0x0002
    MEASUREMENT_STORAGE_SUPPORT = 0x0004
    TIMESTAMP_SUPPORT = 0x0008
    SPO2PR_FAST_SUPPORT = 0x0010
    SPO2PR_SLOW_SUPPORT = 0x0020
    PULSE_AMPLITUDE_INDEX_SUPPORT = 0x0040
    MULTIPLE_BONDS_SUPPORT = 0x0080
    # Bits 8-15 are reserved for future use


class PLXFeaturesCharacteristic(BaseCharacteristic):
    """PLX Features characteristic (0x2A60).

    Describes the supported features of a pulse oximeter device.
    Returns a 16-bit feature flags value.

    Spec: Bluetooth SIG Assigned Numbers, PLX Features characteristic
    """

    expected_length: int = 2
    expected_type: type = int

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> PLXFeatureFlags:
        """Decode PLX features from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (2 bytes minimum)
            ctx: Unused, for signature compatibility

        Returns:
            PLXFeatureFlags enum with supported features

        Raises:
            ValueError: If data length is less than 2 bytes

        """
        del ctx  # Unused parameter
        if len(data) < 2:
            raise ValueError(f"PLX Features requires at least 2 bytes, got {len(data)}")

        raw_value = DataParser.parse_int16(data, 0, signed=False)
        return PLXFeatureFlags(raw_value)

    def encode_value(self, data: PLXFeatureFlags | int) -> bytearray:
        """Encode PLX features to bytes.

        Args:
            data: PLXFeatureFlags enum or 16-bit feature flags as integer

        Returns:
            Encoded bytes (2 bytes, little-endian)

        """
        value = data.value if isinstance(data, PLXFeatureFlags) else data
        return DataParser.encode_int16(value, signed=False)

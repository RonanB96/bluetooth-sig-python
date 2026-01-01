"""Sport Type for Aerobic and Anaerobic Thresholds characteristic (0x2A93)."""

from __future__ import annotations

from enum import IntEnum

from bluetooth_sig.gatt.context import CharacteristicContext

from .base import BaseCharacteristic


class SportType(IntEnum):
    """Sport type enumeration for aerobic and anaerobic thresholds."""

    UNSPECIFIED = 0
    RUNNING_TREADMILL = 1
    CYCLING_ERGOMETER = 2
    ROWING_ERGOMETER = 3
    CROSS_TRAINING_ELLIPTICAL = 4
    CLIMBING = 5
    SKIING = 6
    SKATING = 7
    ARM_EXERCISING = 8
    LOWER_BODY_EXERCISING = 9
    UPPER_BODY_EXERCISING = 10
    WHOLE_BODY_EXERCISING = 11


class SportTypeForAerobicAndAnaerobicThresholdsCharacteristic(BaseCharacteristic):
    """Sport Type for Aerobic and Anaerobic Thresholds characteristic (0x2A93).

    org.bluetooth.characteristic.sport_type_for_aerobic_and_anaerobic_thresholds

    The Sport Type for Aerobic and Anaerobic Thresholds characteristic is used to represent
    the sport type applicable to aerobic and anaerobic thresholds for a user.
    """

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> SportType:
        """Decode sport type from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (1 byte)
            ctx: Optional context for parsing

        Returns:
            SportType enum value

        Raises:
            ValueError: If data length is not exactly 1 byte or value is invalid
        """
        sport_type_value = int(data[0])
        try:
            return SportType(sport_type_value)
        except ValueError as e:
            raise ValueError(f"Invalid Sport Type value: {sport_type_value} (valid range: 0-11)") from e

    def encode_value(self, data: SportType) -> bytearray:
        """Encode sport type to raw bytes.

        Args:
            data: SportType enum value

        Returns:
            bytearray: Encoded bytes
        """
        return bytearray([data.value])

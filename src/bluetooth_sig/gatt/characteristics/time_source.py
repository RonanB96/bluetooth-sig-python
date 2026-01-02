"""Time Source characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class TimeSource(IntEnum):
    """Time source enumeration.

    Indicates the type of time source used for reference time.
    """

    UNKNOWN = 0
    NETWORK_TIME_PROTOCOL = 1  # NTP, SNTP
    GPS = 2  # GPS, Galileo, GLONASS, BeiDou
    RADIO_TIME_SIGNAL = 3  # Atomic clock synchronized through RF
    MANUAL = 4  # Manually set time
    ATOMIC_CLOCK = 5  # Legacy, usually same as RADIO_TIME_SIGNAL
    CELLULAR_NETWORK = 6  # GSM, CDMA, 4G
    NOT_SYNCHRONIZED = 7


class TimeSourceCharacteristic(BaseCharacteristic):
    """Time Source characteristic (0x2A13).

    org.bluetooth.characteristic.time_source

    Indicates the source of the time information as an 8-bit enumeration.
    """

    _template = EnumTemplate.uint8(TimeSource)

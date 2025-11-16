"""Location and Navigation types and enumerations.

Provides common types used across location and navigation related characteristics.
Based on Bluetooth SIG GATT Specification for Location and Navigation Service (0x1819).
"""

from __future__ import annotations

from enum import IntEnum


class PositionStatus(IntEnum):
    """Position status enumeration.

    Used by Navigation and Position Quality characteristics to indicate
    the status/quality of position data.

    Per Bluetooth SIG Location and Navigation Service specification.
    """

    NO_POSITION = 0
    POSITION_OK = 1
    ESTIMATED_POSITION = 2
    LAST_KNOWN_POSITION = 3

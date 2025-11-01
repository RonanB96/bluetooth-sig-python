"""Alert Notification types and enumerations.

Provides common types used across Alert Notification Service characteristics.
Based on Bluetooth SIG GATT Specification for Alert Notification Service (0x1811).
"""

from __future__ import annotations

from enum import IntEnum, IntFlag

# Alert Category ID value ranges
ALERT_CATEGORY_DEFINED_MAX = 9  # 0-9 are defined categories
ALERT_CATEGORY_RESERVED_MIN = 10  # 10-250 are reserved
ALERT_CATEGORY_RESERVED_MAX = 250
ALERT_CATEGORY_SERVICE_SPECIFIC_MIN = 251  # 251-255 are service-specific

# Alert text constraints
ALERT_TEXT_MAX_LENGTH = 18  # Maximum UTF-8 text length in bytes

# Unread count special values
UNREAD_COUNT_MAX = 254  # 0-254 explicit count
UNREAD_COUNT_MORE_THAN_MAX = 255  # 255 means >254 unread

# Control point command range
ALERT_COMMAND_MAX = 5  # Valid command IDs are 0-5


class AlertCategoryID(IntEnum):
    """Alert category enumeration per Bluetooth SIG specification.

    Values 0-9 are defined, 10-250 reserved, 251-255 service-specific.
    """

    SIMPLE_ALERT = 0
    EMAIL = 1
    NEWS = 2
    CALL = 3
    MISSED_CALL = 4
    SMS_MMS = 5
    VOICE_MAIL = 6
    SCHEDULE = 7
    HIGH_PRIORITIZED_ALERT = 8
    INSTANT_MESSAGE = 9


class AlertCategoryBitMask(IntFlag):
    """Alert category bit mask flags.

    Each bit represents support for a specific alert category.
    Bits 10-15 are reserved for future use.
    """

    SIMPLE_ALERT = 1 << 0
    EMAIL = 1 << 1
    NEWS = 1 << 2
    CALL = 1 << 3
    MISSED_CALL = 1 << 4
    SMS_MMS = 1 << 5
    VOICE_MAIL = 1 << 6
    SCHEDULE = 1 << 7
    HIGH_PRIORITIZED_ALERT = 1 << 8
    INSTANT_MESSAGE = 1 << 9


class AlertNotificationCommandID(IntEnum):
    """Alert Notification Control Point command enumeration."""

    ENABLE_NEW_ALERT = 0
    ENABLE_UNREAD_STATUS = 1
    DISABLE_NEW_ALERT = 2
    DISABLE_UNREAD_STATUS = 3
    NOTIFY_NEW_ALERT_IMMEDIATELY = 4
    NOTIFY_UNREAD_STATUS_IMMEDIATELY = 5


def validate_category_id(category_id_raw: int) -> AlertCategoryID:
    """Validate and convert raw category ID value.

    Args:
        category_id_raw: Raw category ID value (0-255)

    Returns:
        AlertCategoryID enum value

    Raises:
        ValueError: If category ID is in reserved range (10-250)

    """
    if not (category_id_raw <= ALERT_CATEGORY_DEFINED_MAX or category_id_raw >= ALERT_CATEGORY_SERVICE_SPECIFIC_MIN):
        raise ValueError(
            f"Invalid category ID: {category_id_raw} "
            f"(valid: 0-{ALERT_CATEGORY_DEFINED_MAX} or "
            f"{ALERT_CATEGORY_SERVICE_SPECIFIC_MIN}-255)"
        )
    return (
        AlertCategoryID(category_id_raw)
        if category_id_raw <= ALERT_CATEGORY_DEFINED_MAX
        else AlertCategoryID.SIMPLE_ALERT
    )

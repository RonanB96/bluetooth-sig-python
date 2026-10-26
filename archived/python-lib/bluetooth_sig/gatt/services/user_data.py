"""User Data Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class UserDataService(BaseGattService):
    """User Data Service implementation.

    Contains characteristics related to user profile and fitness data:
    - First Name - Optional
    - Last Name - Optional
    - Email Address - Optional
    - Age - Optional
    - Date of Birth - Optional
    - Gender - Optional
    - Weight - Optional
    - Height - Optional
    - VO2 Max - Optional
    - Heart Rate Max - Optional
    - Resting Heart Rate - Optional
    - Maximum Recommended Heart Rate - Optional
    - Aerobic Threshold - Optional
    - Anaerobic Threshold - Optional
    - Sport Type for Aerobic and Anaerobic Thresholds - Optional
    - Date of Threshold Assessment - Optional
    - Waist Circumference - Optional
    - Hip Circumference - Optional
    - Fat Burn Heart Rate Lower Limit - Optional
    - Fat Burn Heart Rate Upper Limit - Optional
    - Aerobic Heart Rate Lower Limit - Optional
    - Aerobic Heart Rate Upper Limit - Optional
    - Anaerobic Heart Rate Lower Limit - Optional
    - Anaerobic Heart Rate Upper Limit - Optional
    - Two Zone Heart Rate Limits - Optional
    - Three Zone Heart Rate Limits - Optional
    - Four Zone Heart Rate Limits - Optional
    - Five Zone Heart Rate Limits - Optional
    - High Intensity Exercise Threshold - Optional
    - Activity Goal - Optional
    - Sedentary Interval Notification - Optional
    - Caloric Intake - Optional
    - Stride Length - Optional
    - Preferred Units - Optional
    - Language - Optional
    - Handedness - Optional
    - Device Wearing Position - Optional
    - Middle Name - Optional
    - High Resolution Height - Optional
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.DATABASE_CHANGE_INCREMENT: True,
        CharacteristicName.USER_INDEX: True,
        CharacteristicName.USER_CONTROL_POINT: True,
        CharacteristicName.REGISTERED_USER: False,
        # UDS permitted characteristics (at least one required if service is present)
        CharacteristicName.FIRST_NAME: False,
        CharacteristicName.LAST_NAME: False,
        CharacteristicName.EMAIL_ADDRESS: False,
        CharacteristicName.AGE: False,
        CharacteristicName.DATE_OF_BIRTH: False,
        CharacteristicName.GENDER: False,
        CharacteristicName.WEIGHT: False,
        CharacteristicName.HEIGHT: False,
        CharacteristicName.VO2_MAX: False,
        CharacteristicName.HEART_RATE_MAX: False,
        CharacteristicName.RESTING_HEART_RATE: False,
        CharacteristicName.MAXIMUM_RECOMMENDED_HEART_RATE: False,
        CharacteristicName.AEROBIC_THRESHOLD: False,
        CharacteristicName.ANAEROBIC_THRESHOLD: False,
        CharacteristicName.SPORT_TYPE_FOR_AEROBIC_AND_ANAEROBIC_THRESHOLDS: False,
        CharacteristicName.DATE_OF_THRESHOLD_ASSESSMENT: False,
        CharacteristicName.WAIST_CIRCUMFERENCE: False,
        CharacteristicName.HIP_CIRCUMFERENCE: False,
        CharacteristicName.FAT_BURN_HEART_RATE_LOWER_LIMIT: False,
        CharacteristicName.FAT_BURN_HEART_RATE_UPPER_LIMIT: False,
        CharacteristicName.AEROBIC_HEART_RATE_LOWER_LIMIT: False,
        CharacteristicName.AEROBIC_HEART_RATE_UPPER_LIMIT: False,
        CharacteristicName.ANAEROBIC_HEART_RATE_LOWER_LIMIT: False,
        CharacteristicName.ANAEROBIC_HEART_RATE_UPPER_LIMIT: False,
        CharacteristicName.TWO_ZONE_HEART_RATE_LIMITS: False,
        CharacteristicName.THREE_ZONE_HEART_RATE_LIMITS: False,
        CharacteristicName.FOUR_ZONE_HEART_RATE_LIMITS: False,
        CharacteristicName.FIVE_ZONE_HEART_RATE_LIMITS: False,
        CharacteristicName.HIGH_INTENSITY_EXERCISE_THRESHOLD: False,
        CharacteristicName.ACTIVITY_GOAL: False,
        CharacteristicName.SEDENTARY_INTERVAL_NOTIFICATION: False,
        CharacteristicName.CALORIC_INTAKE: False,
        CharacteristicName.STRIDE_LENGTH: False,
        CharacteristicName.PREFERRED_UNITS: False,
        CharacteristicName.LANGUAGE: False,
        CharacteristicName.HANDEDNESS: False,
        CharacteristicName.DEVICE_WEARING_POSITION: False,
        CharacteristicName.MIDDLE_NAME: False,
        CharacteristicName.HIGH_RESOLUTION_HEIGHT: False,
    }

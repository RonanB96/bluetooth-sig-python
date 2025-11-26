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
        CharacteristicName.FIRST_NAME: False,  # optional
        CharacteristicName.LAST_NAME: False,  # optional
        CharacteristicName.EMAIL_ADDRESS: False,  # optional
        CharacteristicName.AGE: False,  # optional
        CharacteristicName.DATE_OF_BIRTH: False,  # optional
        CharacteristicName.GENDER: False,  # optional
        CharacteristicName.WEIGHT: False,  # optional
        CharacteristicName.HEIGHT: False,  # optional
        CharacteristicName.VO2_MAX: False,  # optional
        CharacteristicName.HEART_RATE_MAX: False,  # optional
        CharacteristicName.RESTING_HEART_RATE: False,  # optional
        CharacteristicName.MAXIMUM_RECOMMENDED_HEART_RATE: False,  # optional
        CharacteristicName.AEROBIC_THRESHOLD: False,  # optional
        CharacteristicName.ANAEROBIC_THRESHOLD: False,  # optional
        CharacteristicName.SPORT_TYPE_FOR_AEROBIC_AND_ANAEROBIC_THRESHOLDS: False,  # optional
        CharacteristicName.DATE_OF_THRESHOLD_ASSESSMENT: False,  # optional
        CharacteristicName.WAIST_CIRCUMFERENCE: False,  # optional
        CharacteristicName.HIP_CIRCUMFERENCE: False,  # optional
        CharacteristicName.FAT_BURN_HEART_RATE_LOWER_LIMIT: False,  # optional
        CharacteristicName.FAT_BURN_HEART_RATE_UPPER_LIMIT: False,  # optional
        CharacteristicName.AEROBIC_HEART_RATE_LOWER_LIMIT: False,  # optional
        CharacteristicName.AEROBIC_HEART_RATE_UPPER_LIMIT: False,  # optional
        CharacteristicName.ANAEROBIC_HEART_RATE_LOWER_LIMIT: False,  # optional
        CharacteristicName.ANAEROBIC_HEART_RATE_UPPER_LIMIT: False,  # optional
        CharacteristicName.TWO_ZONE_HEART_RATE_LIMITS: False,  # optional
        CharacteristicName.THREE_ZONE_HEART_RATE_LIMITS: False,  # optional
        CharacteristicName.FOUR_ZONE_HEART_RATE_LIMITS: False,  # optional
        CharacteristicName.FIVE_ZONE_HEART_RATE_LIMITS: False,  # optional
        CharacteristicName.HIGH_INTENSITY_EXERCISE_THRESHOLD: False,  # optional
        CharacteristicName.ACTIVITY_GOAL: False,  # optional
        CharacteristicName.SEDENTARY_INTERVAL_NOTIFICATION: False,  # optional
        CharacteristicName.CALORIC_INTAKE: False,  # optional
        CharacteristicName.STRIDE_LENGTH: False,  # optional
        CharacteristicName.PREFERRED_UNITS: False,  # optional
        CharacteristicName.LANGUAGE: False,  # optional
        CharacteristicName.HANDEDNESS: False,  # optional
        CharacteristicName.DEVICE_WEARING_POSITION: False,  # optional
        CharacteristicName.MIDDLE_NAME: False,  # optional
        CharacteristicName.HIGH_RESOLUTION_HEIGHT: False,  # optional
    }

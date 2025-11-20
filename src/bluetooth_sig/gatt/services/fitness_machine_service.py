"""Fitness Machine Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class FitnessMachineService(BaseGattService):
    """Fitness Machine Service implementation.

    Contains characteristics related to fitness machines:
    - Fitness Machine Feature - Mandatory
    - Treadmill Data - Optional
    - Cross Trainer Data - Optional
    - Step Climber Data - Optional
    - Stair Climber Data - Optional
    - Rower Data - Optional
    - Indoor Bike Data - Optional
    - Training Status - Optional
    - Supported Speed Range - Optional
    - Supported Inclination Range - Optional
    - Supported Resistance Level Range - Optional
    - Supported Heart Rate Range - Optional
    - Supported Power Range - Optional
    - Fitness Machine Control Point - Optional
    - Fitness Machine Status - Optional
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.FITNESS_MACHINE_FEATURE: True,  # mandatory
        CharacteristicName.TREADMILL_DATA: False,  # optional
        CharacteristicName.CROSS_TRAINER_DATA: False,  # optional
        CharacteristicName.STEP_CLIMBER_DATA: False,  # optional
        CharacteristicName.STAIR_CLIMBER_DATA: False,  # optional
        CharacteristicName.ROWER_DATA: False,  # optional
        CharacteristicName.INDOOR_BIKE_DATA: False,  # optional
        CharacteristicName.TRAINING_STATUS: False,  # optional
        CharacteristicName.SUPPORTED_SPEED_RANGE: False,  # optional
        CharacteristicName.SUPPORTED_INCLINATION_RANGE: False,  # optional
        CharacteristicName.SUPPORTED_RESISTANCE_LEVEL_RANGE: False,  # optional
        CharacteristicName.SUPPORTED_HEART_RATE_RANGE: False,  # optional
        CharacteristicName.SUPPORTED_POWER_RANGE: False,  # optional
        CharacteristicName.FITNESS_MACHINE_CONTROL_POINT: False,  # optional
        CharacteristicName.FITNESS_MACHINE_STATUS: False,  # optional
    }

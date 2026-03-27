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
        CharacteristicName.TREADMILL_DATA: False,
        CharacteristicName.CROSS_TRAINER_DATA: False,
        CharacteristicName.STEP_CLIMBER_DATA: False,
        CharacteristicName.STAIR_CLIMBER_DATA: False,
        CharacteristicName.ROWER_DATA: False,
        CharacteristicName.INDOOR_BIKE_DATA: False,
        CharacteristicName.TRAINING_STATUS: False,
        CharacteristicName.SUPPORTED_SPEED_RANGE: False,
        CharacteristicName.SUPPORTED_INCLINATION_RANGE: False,
        CharacteristicName.SUPPORTED_RESISTANCE_LEVEL_RANGE: False,
        CharacteristicName.SUPPORTED_HEART_RATE_RANGE: False,
        CharacteristicName.SUPPORTED_POWER_RANGE: False,
        CharacteristicName.FITNESS_MACHINE_CONTROL_POINT: False,
        CharacteristicName.FITNESS_MACHINE_STATUS: False,
    }

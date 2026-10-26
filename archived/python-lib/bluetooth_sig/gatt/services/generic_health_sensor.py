"""GenericHealthSensor Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class GenericHealthSensorService(BaseGattService):
    """Generic Health Sensor Service implementation (0x1840).

    A flexible health sensor framework supporting live and stored
    health observations with configurable observation schedules.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.HEALTH_SENSOR_FEATURES: False,
        CharacteristicName.LIVE_HEALTH_OBSERVATIONS: False,
        CharacteristicName.STORED_HEALTH_OBSERVATIONS: False,
        CharacteristicName.RECORD_ACCESS_CONTROL_POINT: False,
        CharacteristicName.GHS_CONTROL_POINT: False,
        CharacteristicName.OBSERVATION_SCHEDULE_CHANGED: False,
    }

"""IndustrialMeasurementDevice Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class IndustrialMeasurementDeviceService(BaseGattService):
    """Industrial Measurement Device Service implementation (0x185A).

    Used for industrial measurement instruments. Provides device
    status, historical measurement data, and control capabilities.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.IMD_STATUS: False,
        CharacteristicName.IMDS_DESCRIPTOR_VALUE_CHANGED: False,
        CharacteristicName.FIRST_USE_DATE: False,
        CharacteristicName.LIFE_CYCLE_DATA: False,
        CharacteristicName.WORK_CYCLE_DATA: False,
        CharacteristicName.SERVICE_CYCLE_DATA: False,
        CharacteristicName.IMD_CONTROL: False,
        CharacteristicName.IMD_HISTORICAL_DATA: False,
        CharacteristicName.RECORD_ACCESS_CONTROL_POINT: False,
        # IMD Measurement permitted characteristics (at least one required if service is present)
        CharacteristicName.ACCELERATION: False,
        CharacteristicName.FORCE: False,
        CharacteristicName.LINEAR_POSITION: False,
        CharacteristicName.ROTATIONAL_SPEED: False,
        CharacteristicName.LENGTH: False,
        CharacteristicName.TORQUE: False,
        CharacteristicName.TEMPERATURE: False,
    }

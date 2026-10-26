"""PhysicalActivityMonitor Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class PhysicalActivityMonitorService(BaseGattService):
    """Physical Activity Monitor Service implementation (0x183E).

    Used for physical activity monitoring devices. Provides general,
    cardiorespiratory, and sleep activity data along with step
    counting and session management.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.PHYSICAL_ACTIVITY_MONITOR_FEATURES: True,
        CharacteristicName.GENERAL_ACTIVITY_INSTANTANEOUS_DATA: True,
        CharacteristicName.GENERAL_ACTIVITY_SUMMARY_DATA: True,
        CharacteristicName.PHYSICAL_ACTIVITY_MONITOR_CONTROL_POINT: True,
        CharacteristicName.PHYSICAL_ACTIVITY_CURRENT_SESSION: True,
        CharacteristicName.PHYSICAL_ACTIVITY_SESSION_DESCRIPTOR: True,
        CharacteristicName.CARDIORESPIRATORY_ACTIVITY_INSTANTANEOUS_DATA: False,
        CharacteristicName.CARDIORESPIRATORY_ACTIVITY_SUMMARY_DATA: False,
        CharacteristicName.STEP_COUNTER_ACTIVITY_SUMMARY_DATA: False,
        CharacteristicName.SLEEP_ACTIVITY_INSTANTANEOUS_DATA: False,
        CharacteristicName.SLEEP_ACTIVITY_SUMMARY_DATA: False,
    }

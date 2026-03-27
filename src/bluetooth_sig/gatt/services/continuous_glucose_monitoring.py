"""ContinuousGlucoseMonitoring Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class ContinuousGlucoseMonitoringService(BaseGattService):
    """Continuous Glucose Monitoring Service implementation (0x181F).

    Used for continuous glucose monitoring devices. Provides real-time
    glucose concentration readings, session management, and device
    feature reporting.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.CGM_MEASUREMENT: True,
        CharacteristicName.CGM_FEATURE: True,
        CharacteristicName.CGM_STATUS: False,
        CharacteristicName.CGM_SESSION_START_TIME: False,
        CharacteristicName.CGM_SESSION_RUN_TIME: False,
        CharacteristicName.CGM_SPECIFIC_OPS_CONTROL_POINT: False,
        CharacteristicName.RECORD_ACCESS_CONTROL_POINT: False,
    }

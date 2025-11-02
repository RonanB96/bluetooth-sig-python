"""Registry of supported GATT services."""

from __future__ import annotations

# Import individual service classes for backward compatibility
from .automation_io import AutomationIOService
from .base import (
    CharacteristicStatus,
    ServiceCharacteristicInfo,
    ServiceCompletenessReport,
    ServiceHealthStatus,
    ServiceValidationResult,
)
from .battery_service import BatteryService
from .blood_pressure import BloodPressureService
from .body_composition import BodyCompositionService
from .cycling_power import CyclingPowerService
from .cycling_speed_and_cadence import CyclingSpeedAndCadenceService
from .device_information import DeviceInformationService
from .environmental_sensing import EnvironmentalSensingService
from .generic_access import GenericAccessService
from .generic_attribute import GenericAttributeService
from .glucose import GlucoseService
from .health_thermometer import HealthThermometerService
from .heart_rate import HeartRateService
from .location_and_navigation import LocationAndNavigationService
from .phone_alert_status import PhoneAlertStatusService
from .registry import (
    SERVICE_CLASS_MAP,
    GattServiceRegistry,
    ServiceName,
)
from .running_speed_and_cadence import RunningSpeedAndCadenceService
from .weight_scale import WeightScaleService

__all__ = [
    # Registry components
    "GattServiceRegistry",
    "SERVICE_CLASS_MAP",
    "ServiceName",
    # Service validation and status classes
    "ServiceHealthStatus",
    "CharacteristicStatus",
    "ServiceValidationResult",
    "ServiceCharacteristicInfo",
    "ServiceCompletenessReport",
    # Individual service classes for backward compatibility
    "AutomationIOService",
    "BatteryService",
    "BloodPressureService",
    "BodyCompositionService",
    "CyclingPowerService",
    "CyclingSpeedAndCadenceService",
    "DeviceInformationService",
    "EnvironmentalSensingService",
    "GenericAccessService",
    "GenericAttributeService",
    "GlucoseService",
    "HealthThermometerService",
    "HeartRateService",
    "LocationAndNavigationService",
    "PhoneAlertStatusService",
    "RunningSpeedAndCadenceService",
    "WeightScaleService",
]

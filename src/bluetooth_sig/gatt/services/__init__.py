"""Registry of supported GATT services."""

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
from .registry import (
    SERVICE_CLASS_MAP,
    SERVICE_CLASS_MAP_STR,
    GattServiceRegistry,
    ServiceName,
)
from .running_speed_and_cadence import RunningSpeedAndCadenceService
from .weight_scale import WeightScaleService

__all__ = [
    # Registry components
    "GattServiceRegistry",
    "SERVICE_CLASS_MAP",
    "SERVICE_CLASS_MAP_STR",
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
    "RunningSpeedAndCadenceService",
    "WeightScaleService",
]

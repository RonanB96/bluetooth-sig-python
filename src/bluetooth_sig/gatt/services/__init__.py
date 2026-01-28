"""Registry of supported GATT services."""

from __future__ import annotations

# Import individual service classes for backward compatibility
from .alert_notification import AlertNotificationService
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
from .bond_management import BondManagementService
from .current_time_service import CurrentTimeService
from .cycling_power import CyclingPowerService
from .cycling_speed_and_cadence import CyclingSpeedAndCadenceService
from .device_information import DeviceInformationService
from .environmental_sensing import EnvironmentalSensingService
from .generic_access import GenericAccessService
from .generic_attribute import GenericAttributeService
from .glucose import GlucoseService
from .health_thermometer import HealthThermometerService
from .heart_rate import HeartRateService
from .immediate_alert import ImmediateAlertService
from .indoor_positioning_service import IndoorPositioningService
from .link_loss import LinkLossService
from .location_and_navigation import LocationAndNavigationService
from .next_dst_change import NextDstChangeService
from .phone_alert_status import PhoneAlertStatusService
from .reference_time_update import ReferenceTimeUpdateService
from .registry import GattServiceRegistry, ServiceName, get_service_class_map
from .running_speed_and_cadence import RunningSpeedAndCadenceService
from .scan_parameters import ScanParametersService
from .tx_power import TxPowerService
from .weight_scale import WeightScaleService

__all__ = [
    # Individual service classes for backward compatibility
    "AlertNotificationService",
    "AutomationIOService",
    "BatteryService",
    "BloodPressureService",
    "BodyCompositionService",
    "BondManagementService",
    "CharacteristicStatus",
    "CurrentTimeService",
    "CyclingPowerService",
    "CyclingSpeedAndCadenceService",
    "DeviceInformationService",
    "EnvironmentalSensingService",
    # Registry components
    "GattServiceRegistry",
    "GenericAccessService",
    "GenericAttributeService",
    "GlucoseService",
    "HealthThermometerService",
    "HeartRateService",
    "ImmediateAlertService",
    "IndoorPositioningService",
    "LinkLossService",
    "LocationAndNavigationService",
    "NextDstChangeService",
    "PhoneAlertStatusService",
    "ReferenceTimeUpdateService",
    "RunningSpeedAndCadenceService",
    "ScanParametersService",
    "ServiceCharacteristicInfo",
    "ServiceCompletenessReport",
    # Service validation and status classes
    "ServiceHealthStatus",
    "ServiceName",
    "ServiceValidationResult",
    "TxPowerService",
    "WeightScaleService",
    "get_service_class_map",
]

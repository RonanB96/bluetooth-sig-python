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
from .link_loss import LinkLossService
from .location_and_navigation import LocationAndNavigationService
from .next_dst_change import NextDstChangeService
from .phone_alert_status import PhoneAlertStatusService
from .reference_time_update import ReferenceTimeUpdateService
from .registry import SERVICE_CLASS_MAP, GattServiceRegistry, ServiceName
from .running_speed_and_cadence import RunningSpeedAndCadenceService
from .scan_parameters import ScanParametersService
from .tx_power import TxPowerService
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
    "AlertNotificationService",
    "AutomationIOService",
    "BatteryService",
    "BloodPressureService",
    "BodyCompositionService",
    "BondManagementService",
    "CurrentTimeService",
    "CyclingPowerService",
    "CyclingSpeedAndCadenceService",
    "DeviceInformationService",
    "EnvironmentalSensingService",
    "GenericAccessService",
    "GenericAttributeService",
    "GlucoseService",
    "HealthThermometerService",
    "HeartRateService",
    "ImmediateAlertService",
    "LinkLossService",
    "LocationAndNavigationService",
    "NextDstChangeService",
    "PhoneAlertStatusService",
    "ReferenceTimeUpdateService",
    "RunningSpeedAndCadenceService",
    "ScanParametersService",
    "TxPowerService",
    "WeightScaleService",
]

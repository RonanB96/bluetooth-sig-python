"""Registry of supported GATT services."""

from __future__ import annotations

# Import individual service classes for backward compatibility
from .alert_notification import AlertNotificationService
from .audio_input_control import AudioInputControlService
from .audio_stream_control import AudioStreamControlService
from .authorization_control import AuthorizationControlService
from .automation_io import AutomationIOService
from .base import (
    CharacteristicStatus,
    ServiceCharacteristicInfo,
    ServiceCompletenessReport,
    ServiceHealthStatus,
    ServiceValidationResult,
)
from .basic_audio_announcement import BasicAudioAnnouncementService
from .battery_service import BatteryService
from .binary_sensor import BinarySensorService
from .blood_pressure import BloodPressureService
from .body_composition import BodyCompositionService
from .bond_management import BondManagementService
from .broadcast_audio_announcement import BroadcastAudioAnnouncementService
from .broadcast_audio_scan import BroadcastAudioScanService
from .common_audio import CommonAudioService
from .constant_tone_extension import ConstantToneExtensionService
from .continuous_glucose_monitoring import ContinuousGlucoseMonitoringService
from .coordinated_set_identification import CoordinatedSetIdentificationService
from .current_time_service import CurrentTimeService
from .cycling_power import CyclingPowerService
from .cycling_speed_and_cadence import CyclingSpeedAndCadenceService
from .device_information import DeviceInformationService
from .device_time import DeviceTimeService
from .elapsed_time import ElapsedTimeService
from .electronic_shelf_label import ElectronicShelfLabelService
from .emergency_configuration import EmergencyConfigurationService
from .environmental_sensing import EnvironmentalSensingService
from .gaming_audio import GamingAudioService
from .generic_access import GenericAccessService
from .generic_attribute import GenericAttributeService
from .generic_health_sensor import GenericHealthSensorService
from .generic_media_control import GenericMediaControlService
from .generic_telephone_bearer import GenericTelephoneBearerService
from .glucose import GlucoseService
from .health_thermometer import HealthThermometerService
from .hearing_access import HearingAccessService
from .heart_rate import HeartRateService
from .hid_iso import HidIsoService
from .http_proxy import HttpProxyService
from .immediate_alert import ImmediateAlertService
from .indoor_positioning_service import IndoorPositioningService
from .industrial_measurement_device import IndustrialMeasurementDeviceService
from .insulin_delivery import InsulinDeliveryService
from .internet_protocol_support import InternetProtocolSupportService
from .link_loss import LinkLossService
from .location_and_navigation import LocationAndNavigationService
from .media_control import MediaControlService
from .mesh_provisioning import MeshProvisioningService
from .mesh_proxy import MeshProxyService
from .mesh_proxy_solicitation import MeshProxySolicitationService
from .microphone_control import MicrophoneControlService
from .next_dst_change import NextDstChangeService
from .object_transfer import ObjectTransferService
from .phone_alert_status import PhoneAlertStatusService
from .physical_activity_monitor import PhysicalActivityMonitorService
from .public_broadcast_announcement import PublicBroadcastAnnouncementService
from .published_audio_capabilities import PublishedAudioCapabilitiesService
from .ranging import RangingService
from .reconnection_configuration import ReconnectionConfigurationService
from .reference_time_update import ReferenceTimeUpdateService
from .registry import GattServiceRegistry, ServiceName, get_service_class_map
from .running_speed_and_cadence import RunningSpeedAndCadenceService
from .scan_parameters import ScanParametersService
from .telephone_bearer import TelephoneBearerService
from .telephony_and_media_audio import TelephonyAndMediaAudioService
from .transport_discovery import TransportDiscoveryService
from .tx_power import TxPowerService
from .volume_control import VolumeControlService
from .volume_offset_control import VolumeOffsetControlService
from .weight_scale import WeightScaleService

__all__ = [
    "AlertNotificationService",
    "AudioInputControlService",
    "AudioStreamControlService",
    "AuthorizationControlService",
    "AutomationIOService",
    "BasicAudioAnnouncementService",
    "BatteryService",
    "BinarySensorService",
    "BloodPressureService",
    "BodyCompositionService",
    "BondManagementService",
    "BroadcastAudioAnnouncementService",
    "BroadcastAudioScanService",
    "CharacteristicStatus",
    "CommonAudioService",
    "ConstantToneExtensionService",
    "ContinuousGlucoseMonitoringService",
    "CoordinatedSetIdentificationService",
    "CurrentTimeService",
    "CyclingPowerService",
    "CyclingSpeedAndCadenceService",
    "DeviceInformationService",
    "DeviceTimeService",
    "ElapsedTimeService",
    "ElectronicShelfLabelService",
    "EmergencyConfigurationService",
    "EnvironmentalSensingService",
    "GamingAudioService",
    "GattServiceRegistry",
    "GenericAccessService",
    "GenericAttributeService",
    "GenericHealthSensorService",
    "GenericMediaControlService",
    "GenericTelephoneBearerService",
    "GlucoseService",
    "HealthThermometerService",
    "HearingAccessService",
    "HeartRateService",
    "HidIsoService",
    "HttpProxyService",
    "ImmediateAlertService",
    "IndoorPositioningService",
    "IndustrialMeasurementDeviceService",
    "InsulinDeliveryService",
    "InternetProtocolSupportService",
    "LinkLossService",
    "LocationAndNavigationService",
    "MediaControlService",
    "MeshProvisioningService",
    "MeshProxyService",
    "MeshProxySolicitationService",
    "MicrophoneControlService",
    "NextDstChangeService",
    "ObjectTransferService",
    "PhoneAlertStatusService",
    "PhysicalActivityMonitorService",
    "PublicBroadcastAnnouncementService",
    "PublishedAudioCapabilitiesService",
    "RangingService",
    "ReconnectionConfigurationService",
    "ReferenceTimeUpdateService",
    "RunningSpeedAndCadenceService",
    "ScanParametersService",
    "ServiceCharacteristicInfo",
    "ServiceCompletenessReport",
    "ServiceHealthStatus",
    "ServiceName",
    "ServiceValidationResult",
    "TelephoneBearerService",
    "TelephonyAndMediaAudioService",
    "TransportDiscoveryService",
    "TxPowerService",
    "VolumeControlService",
    "VolumeOffsetControlService",
    "WeightScaleService",
    "get_service_class_map",
]

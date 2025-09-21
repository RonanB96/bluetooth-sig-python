"""Registry of supported GATT services."""

from enum import Enum
from typing import Any, Optional

from .automation_io import AutomationIOService
from .base import BaseGattService
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
from .running_speed_and_cadence import RunningSpeedAndCadenceService
from .weight_scale import WeightScaleService


class ServiceName(Enum):
    """Enumeration of all supported GATT service names."""

    GENERIC_ACCESS = "Generic Access"
    GENERIC_ATTRIBUTE = "Generic Attribute"
    DEVICE_INFORMATION = "Device Information"
    BATTERY_SERVICE = "Battery Service"
    HEART_RATE = "Heart Rate"
    HEALTH_THERMOMETER = "Health Thermometer"
    GLUCOSE = "Glucose"
    CYCLING_SPEED_AND_CADENCE = "Cycling Speed and Cadence"
    CYCLING_POWER = "Cycling Power"
    RUNNING_SPEED_AND_CADENCE = "Running Speed and Cadence"
    AUTOMATION_IO = "Automation IO"
    ENVIRONMENTAL_SENSING = "Environmental Sensing"
    BODY_COMPOSITION = "Body Composition"
    WEIGHT_SCALE = "Weight Scale"


SERVICE_CLASS_MAP: dict[ServiceName, type[BaseGattService]] = {
    ServiceName.GENERIC_ACCESS: GenericAccessService,
    ServiceName.GENERIC_ATTRIBUTE: GenericAttributeService,
    ServiceName.DEVICE_INFORMATION: DeviceInformationService,
    ServiceName.BATTERY_SERVICE: BatteryService,
    ServiceName.HEART_RATE: HeartRateService,
    ServiceName.HEALTH_THERMOMETER: HealthThermometerService,
    ServiceName.GLUCOSE: GlucoseService,
    ServiceName.CYCLING_SPEED_AND_CADENCE: CyclingSpeedAndCadenceService,
    ServiceName.CYCLING_POWER: CyclingPowerService,
    ServiceName.RUNNING_SPEED_AND_CADENCE: RunningSpeedAndCadenceService,
    ServiceName.AUTOMATION_IO: AutomationIOService,
    ServiceName.ENVIRONMENTAL_SENSING: EnvironmentalSensingService,
    ServiceName.BODY_COMPOSITION: BodyCompositionService,
    ServiceName.WEIGHT_SCALE: WeightScaleService,
}

SERVICE_CLASS_MAP_STR: dict[str, type[BaseGattService]] = {
    e.value: c for e, c in SERVICE_CLASS_MAP.items()
}


class GattServiceRegistry:
    """Registry for all supported GATT services."""

    _services: list[type[BaseGattService]] = [
        AutomationIOService,
        BatteryService,
        BodyCompositionService,
        CyclingPowerService,
        DeviceInformationService,
        EnvironmentalSensingService,
        GenericAccessService,
        GenericAttributeService,
        GlucoseService,
        HealthThermometerService,
        HeartRateService,
        RunningSpeedAndCadenceService,
        CyclingSpeedAndCadenceService,
        WeightScaleService,
    ]

    __all__ = [
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
        "BaseGattService",
    ]

    @classmethod
    def get_service_class(cls, uuid: str) -> Optional[type[BaseGattService]]:
        """Get the service class for a given UUID."""
        uuid = uuid.replace("-", "").upper()
        for service_class in cls._services:
            if service_class.matches_uuid(uuid):
                return service_class
        return None

    @classmethod
    def get_service_class_by_name(
        cls, name: str | ServiceName
    ) -> Optional[type[BaseGattService]]:
        """Get the service class for a given name or enum."""
        if isinstance(name, ServiceName):
            return SERVICE_CLASS_MAP.get(name)
        return SERVICE_CLASS_MAP_STR.get(name)

    @classmethod
    def get_service_class_by_uuid(cls, uuid: str) -> Optional[type[BaseGattService]]:
        """Get the service class for a given UUID (alias for get_service_class)."""
        return cls.get_service_class(uuid)

    @classmethod
    def create_service(
        cls, uuid: str, characteristics: dict[str, dict[str, Any]]
    ) -> Optional[BaseGattService]:
        """Create a service instance for the given UUID and characteristics."""
        service_class = cls.get_service_class(uuid)
        if not service_class:
            return None

        service = service_class()
        service.process_characteristics(characteristics)
        return service

    @classmethod
    def create_service_by_name(
        cls, name: str | ServiceName, characteristics: dict[str, dict[str, Any]]
    ) -> Optional[BaseGattService]:
        """Create a service instance for the given name/enum and characteristics."""
        service_class = cls.get_service_class_by_name(name)
        if not service_class:
            return None

        service = service_class()
        service.process_characteristics(characteristics)
        return service

    @classmethod
    def get_all_services(cls) -> list[type[BaseGattService]]:
        """Get all registered service classes.

        Returns:
            List of all registered service classes
        """
        return cls._services.copy()

    @classmethod
    def supported_services(cls) -> list[str]:
        """Get a list of supported service UUIDs."""
        return [service().SERVICE_UUID for service in cls._services]

    @classmethod
    def supported_service_names(cls) -> list[str]:
        """Get a list of supported service names."""
        return [e.value for e in ServiceName]

    @classmethod
    def list_all_service_enums(cls) -> list[ServiceName]:
        """List all supported service names as enum values."""
        return list(ServiceName)

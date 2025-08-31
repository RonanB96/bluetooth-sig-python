"""Registry of supported GATT services."""

from typing import Dict, List, Optional, Type

from .automation_io import AutomationIOService
from .base import BaseGattService
from .battery_service import BatteryService
from .body_composition import BodyCompositionService
from .cycling_power import CyclingPowerService
from .cycling_speed_and_cadence import CyclingSpeedAndCadenceService
from .device_information import DeviceInformationService
from .environmental_sensing import EnvironmentalSensingService
from .generic_access import GenericAccessService
from .health_thermometer import HealthThermometerService
from .heart_rate import HeartRateService
from .running_speed_and_cadence import RunningSpeedAndCadenceService
from .weight_scale import WeightScaleService


class GattServiceRegistry:
    """Registry for all supported GATT services."""

    _services: List[Type[BaseGattService]] = [
        AutomationIOService,
        BatteryService,
        BodyCompositionService,
        CyclingPowerService,
        DeviceInformationService,
        EnvironmentalSensingService,
        GenericAccessService,
        HealthThermometerService,
        HeartRateService,
        RunningSpeedAndCadenceService,
        CyclingSpeedAndCadenceService,
        WeightScaleService,
    ]

    @classmethod
    def get_service_class(cls, uuid: str) -> Optional[Type[BaseGattService]]:
        """Get the service class for a given UUID."""
        uuid = uuid.replace("-", "").upper()
        for service_class in cls._services:
            if service_class.matches_uuid(uuid):
                return service_class
        return None

    @classmethod
    def create_service(
        cls, uuid: str, characteristics: Dict[str, Dict]
    ) -> Optional[BaseGattService]:
        """Create a service instance for the given UUID and characteristics."""
        service_class = cls.get_service_class(uuid)
        if not service_class:
            return None

        service = service_class()
        service.process_characteristics(characteristics)
        return service

    @classmethod
    def supported_services(cls) -> List[str]:
        """Get a list of supported service UUIDs."""
        return [service.SERVICE_UUID for service in cls._services]

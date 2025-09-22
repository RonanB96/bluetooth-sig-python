"""Bluetooth SIG GATT service registry.

This module contains the service registry implementation, including
the ServiceName enum, service class mappings, and the GattServiceRegistry class.
This was moved from __init__.py to follow Python best practices of keeping
__init__.py files lightweight.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .base import BaseGattService


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


# Lazy initialization of the class mappings to avoid circular imports
_service_class_map: dict[ServiceName, type[BaseGattService]] | None = None
_service_class_map_str: dict[str, type[BaseGattService]] | None = None


def _build_service_class_map() -> dict[ServiceName, type[BaseGattService]]:
    """Build the service class mapping.

    This function is called lazily to avoid circular imports.
    """
    # pylint: disable=import-outside-toplevel
    from .automation_io import AutomationIOService
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

    return {
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


def get_service_class_map() -> dict[ServiceName, type[BaseGattService]]:
    """Get the service class map, building it if necessary."""
    # pylint: disable=global-statement
    global _service_class_map
    if _service_class_map is None:
        _service_class_map = _build_service_class_map()
    return _service_class_map


def get_service_class_map_str() -> dict[str, type[BaseGattService]]:
    """Get the string-based service class map, building it if necessary."""
    # pylint: disable=global-statement
    global _service_class_map_str
    if _service_class_map_str is None:
        _service_class_map_str = {
            e.value: c for e, c in get_service_class_map().items()
        }
    return _service_class_map_str


# Public API - backward compatibility globals
SERVICE_CLASS_MAP = get_service_class_map()
SERVICE_CLASS_MAP_STR = get_service_class_map_str()


class GattServiceRegistry:
    """Registry for all supported GATT services."""

    @classmethod
    def _get_services(cls) -> list[type[BaseGattService]]:
        """Get the list of service classes."""
        return list(get_service_class_map().values())

    @classmethod
    def get_service_class(cls, uuid: str) -> type[BaseGattService] | None:
        """Get the service class for a given UUID."""
        uuid = uuid.replace("-", "").upper()
        for service_class in cls._get_services():
            if service_class.matches_uuid(uuid):
                return service_class
        return None

    @classmethod
    def get_service_class_by_name(
        cls, name: str | ServiceName
    ) -> type[BaseGattService] | None:
        """Get the service class for a given name or enum."""
        if isinstance(name, ServiceName):
            return get_service_class_map().get(name)
        return get_service_class_map_str().get(name)

    @classmethod
    def get_service_class_by_uuid(cls, uuid: str) -> type[BaseGattService] | None:
        """Get the service class for a given UUID (alias for get_service_class)."""
        return cls.get_service_class(uuid)

    @classmethod
    def create_service(
        cls, uuid: str, characteristics: dict[str, dict[str, Any]]
    ) -> BaseGattService | None:
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
    ) -> BaseGattService | None:
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
        return cls._get_services().copy()

    @classmethod
    def supported_services(cls) -> list[str]:
        """Get a list of supported service UUIDs."""
        return [service().SERVICE_UUID for service in cls._get_services()]

    @classmethod
    def supported_service_names(cls) -> list[str]:
        """Get a list of supported service names."""
        return [e.value for e in ServiceName]

    @classmethod
    def list_all_service_enums(cls) -> list[ServiceName]:
        """List all supported service names as enum values."""
        return list(ServiceName)

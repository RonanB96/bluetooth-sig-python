"""Bluetooth SIG GATT service registry.

This module contains the service registry implementation, including the
ServiceName enum, service class mappings, and the GattServiceRegistry
class. This was moved from __init__.py to follow Python best practices
of keeping __init__.py files lightweight.
"""

from __future__ import annotations

import threading
from enum import Enum
from typing import Any

from ...types.uuid import BluetoothUUID
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
        _service_class_map_str = {e.value: c for e, c in get_service_class_map().items()}
    return _service_class_map_str


# Public API - backward compatibility globals
SERVICE_CLASS_MAP = get_service_class_map()
SERVICE_CLASS_MAP_STR = get_service_class_map_str()


class GattServiceRegistry:
    """Registry for all supported GATT services."""

    _lock = threading.RLock()
    _custom_service_classes: dict[BluetoothUUID, type[BaseGattService]] = {}

    @classmethod
    def register_service_class(
        cls, uuid: str | BluetoothUUID, service_cls: type[BaseGattService], override: bool = False
    ) -> None:
        """Register a custom service class at runtime.

        Args:
            uuid: The service UUID
            service_cls: The service class to register
            override: Whether to override existing registrations

        Raises:
            TypeError: If service_cls does not inherit from BaseGattService
            ValueError: If UUID conflicts with existing registration and override=False
        """
        if not issubclass(service_cls, BaseGattService):
            raise TypeError(f"Class {service_cls.__name__} must inherit from BaseGattService")

        # Always normalize UUID to BluetoothUUID
        bt_uuid = BluetoothUUID(uuid) if not isinstance(uuid, BluetoothUUID) else uuid

        with cls._lock:
            # Check for conflicts
            if not override:
                if bt_uuid in cls._custom_service_classes:
                    raise ValueError(f"UUID {bt_uuid} already registered. Use override=True to replace.")

            cls._custom_service_classes[bt_uuid] = service_cls

    @classmethod
    def unregister_service_class(cls, uuid: str | BluetoothUUID) -> None:
        """Unregister a custom service class.

        Args:
            uuid: The service UUID to unregister
        """
        bt_uuid = BluetoothUUID(uuid) if not isinstance(uuid, BluetoothUUID) else uuid
        with cls._lock:
            cls._custom_service_classes.pop(bt_uuid, None)

    @classmethod
    def _get_services(cls) -> list[type[BaseGattService]]:
        """Get the list of service classes."""
        return list(get_service_class_map().values())

    @classmethod
    def get_service_class(cls, uuid: str | BluetoothUUID) -> type[BaseGattService] | None:
        """Get the service class for a given UUID."""
        try:
            if isinstance(uuid, str):
                bt_uuid = BluetoothUUID(uuid)
            else:
                bt_uuid = uuid
        except ValueError:
            return None
        # Check custom registry first
        with cls._lock:
            if custom_cls := cls._custom_service_classes.get(bt_uuid):
                return custom_cls

        for service_class in cls._get_services():
            if service_class.matches_uuid(bt_uuid):
                return service_class
        return None

    @classmethod
    def get_service_class_by_name(cls, name: str | ServiceName) -> type[BaseGattService] | None:
        """Get the service class for a given name or enum."""
        if isinstance(name, ServiceName):
            return get_service_class_map().get(name)
        return get_service_class_map_str().get(name)

    @classmethod
    def get_service_class_by_uuid(cls, uuid: BluetoothUUID) -> type[BaseGattService] | None:
        """Get the service class for a given UUID (alias for
        get_service_class)."""
        return cls.get_service_class(uuid)

    @classmethod
    def create_service(
        cls, uuid: BluetoothUUID, characteristics: dict[BluetoothUUID, dict[str, Any]]
    ) -> BaseGattService | None:
        """Create a service instance for the given UUID and characteristics."""
        service_class = cls.get_service_class(uuid)
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
        return [str(service().uuid) for service in cls._get_services()]

    @classmethod
    def supported_service_names(cls) -> list[str]:
        """Get a list of supported service names."""
        return [e.value for e in ServiceName]

    @classmethod
    def clear_custom_registrations(cls) -> None:
        """Clear all custom service registrations (for testing)."""
        cls._custom_service_classes.clear()

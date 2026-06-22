"""Opt-in GATT service compliance validation for discovered devices."""

from __future__ import annotations

import msgspec

from ..gatt.services.base import BaseGattService, ServiceValidationResult
from ..types.uuid import BluetoothUUID
from .connected import DeviceService


class DiscoveredServiceValidation(msgspec.Struct, kw_only=True, frozen=True):
    """Validation result for a single discovered GATT service."""

    service_uuid: BluetoothUUID
    service_name: str
    validation: ServiceValidationResult


def validate_device_services(
    services: dict[str, DeviceService],
    *,
    strict: bool = False,
) -> list[DiscoveredServiceValidation]:
    """Validate discovered services against SIG service definitions.

    Args:
        services: Discovered services keyed by UUID string (from ``DeviceConnected.services``).
        strict: When ``True``, missing optional characteristics produce warnings.

    Returns:
        Validation results for each discovered service with a known SIG implementation.
        Unknown vendor services (no registered service class) are skipped.
    """
    results: list[DiscoveredServiceValidation] = []
    for device_service in services.values():
        if device_service.service_class is None:
            continue

        service = _build_service_instance(device_service)
        validation = service.validate_service(strict=strict)
        results.append(
            DiscoveredServiceValidation(
                service_uuid=device_service.uuid,
                service_name=service.name,
                validation=validation,
            )
        )
    return results


def _build_service_instance(device_service: DeviceService) -> BaseGattService:
    """Instantiate a SIG service and attach discovered characteristics."""
    service_class = device_service.service_class
    assert service_class is not None
    service = service_class()
    for characteristic in device_service.characteristics.values():
        service.characteristics[characteristic.uuid] = characteristic
    return service

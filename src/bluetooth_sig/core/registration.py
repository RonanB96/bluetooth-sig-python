"""Custom characteristic and service registration manager.

Provides runtime registration of custom characteristic and service classes
into the SIG registries. Stateless — writes to global registries.
"""

from __future__ import annotations

from typing import Any

from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.characteristics.registry import CharacteristicRegistry
from ..gatt.services.base import BaseGattService
from ..gatt.services.registry import GattServiceRegistry
from ..gatt.uuid_registry import uuid_registry
from ..types import (
    CharacteristicInfo,
    ServiceInfo,
)


class RegistrationManager:
    """Handles runtime registration of custom characteristics and services.

    All registrations write to the global CharacteristicRegistry, GattServiceRegistry,
    and uuid_registry singletons.
    """

    @staticmethod
    def register_custom_characteristic_class(
        uuid_or_name: str,
        cls: type[BaseCharacteristic[Any]],
        info: CharacteristicInfo | None = None,
        override: bool = False,
    ) -> None:
        """Register a custom characteristic class at runtime.

        Args:
            uuid_or_name: The characteristic UUID or name
            cls: The characteristic class to register
            info: Optional CharacteristicInfo with metadata (name, unit, value_type)
            override: Whether to override existing registrations

        Raises:
            TypeError: If cls does not inherit from BaseCharacteristic
            ValueError: If UUID conflicts with existing registration and override=False

        """
        CharacteristicRegistry.register_characteristic_class(uuid_or_name, cls, override)

        if info:
            uuid_registry.register_characteristic(
                uuid=info.uuid,
                name=info.name or cls.__name__,
                identifier=info.id,
                unit=info.unit,
                value_type=info.value_type,
                override=override,
            )

    @staticmethod
    def register_custom_service_class(
        uuid_or_name: str,
        cls: type[BaseGattService],
        info: ServiceInfo | None = None,
        override: bool = False,
    ) -> None:
        """Register a custom service class at runtime.

        Args:
            uuid_or_name: The service UUID or name
            cls: The service class to register
            info: Optional ServiceInfo with metadata (name)
            override: Whether to override existing registrations

        Raises:
            TypeError: If cls does not inherit from BaseGattService
            ValueError: If UUID conflicts with existing registration and override=False

        """
        GattServiceRegistry.register_service_class(uuid_or_name, cls, override)

        if info:
            uuid_registry.register_service(
                uuid=info.uuid,
                name=info.name or cls.__name__,
                identifier=info.id,
                override=override,
            )

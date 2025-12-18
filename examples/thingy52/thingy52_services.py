"""Nordic Thingy:52 custom service implementations.

This module demonstrates how to create custom GATT services for vendor-specific
implementations using the bluetooth-sig-python library's service framework.

Services organize related characteristics into logical groups and provide
validation, discovery, and health checking capabilities.

References:
    - Nordic Thingy:52 Firmware Documentation:
      https://nordicsemiconductor.github.io/Nordic-Thingy52-FW/documentation
"""

from __future__ import annotations

from typing import ClassVar

from bluetooth_sig.gatt.services.base import BaseGattService
from bluetooth_sig.types import ServiceInfo
from bluetooth_sig.types.uuid import BluetoothUUID

# Import our custom characteristics (these would be the enum names if registered)
# For custom characteristics, we reference them by their class directly
from .thingy52_characteristics import (
    ThingyButtonCharacteristic,
    ThingyColorCharacteristic,
    ThingyGasCharacteristic,
    ThingyHeadingCharacteristic,
    ThingyHumidityCharacteristic,
    ThingyOrientationCharacteristic,
    ThingyPressureCharacteristic,
    ThingyTemperatureCharacteristic,
)

# Nordic UUID base for services
# Format: EF68XXYY-9B35-4933-9B10-52FFA9740042 where XX is service ID
NORDIC_SERVICE_UUID_BASE = "EF68%04X-9B35-4933-9B10-52FFA9740042"


class ThingyEnvironmentService(BaseGattService):
    """Nordic Thingy:52 Environment Sensing Service.

    Service UUID: EF680200-9B35-4933-9B10-52FFA9740042

    Contains environmental sensor characteristics:
    - Temperature (required)
    - Pressure (optional)
    - Humidity (optional)
    - Gas Sensor (optional)
    - Color Sensor (optional)

    This demonstrates how custom services can organize vendor-specific
    characteristics and provide service-level validation and health checking.

    Examples:
        >>> from bluetooth_sig.types.gatt_services import ServiceDiscoveryData, CharacteristicSpec
        >>> # Discovered service data with temperature characteristic
        >>> discovery_data = ServiceDiscoveryData(
        ...     service_uuid=BluetoothUUID("EF680200-9B35-4933-9B10-52FFA9740042"),
        ...     characteristics=[
        ...         CharacteristicSpec(
        ...             uuid=BluetoothUUID("EF680201-9B35-4933-9B10-52FFA9740042"), properties=["read", "notify"]
        ...         )
        ...     ],
        ... )
        >>> service = ThingyEnvironmentService(discovery_data=discovery_data)
        >>> service.service_info.name
        'Thingy Environment Service'
    """

    _info = ServiceInfo(
        uuid=BluetoothUUID(NORDIC_SERVICE_UUID_BASE % 0x0200),
        name="Thingy Environment Service",
    )

    # Define which characteristics belong to this service
    # For custom characteristics, we use the class type directly
    # In a real implementation with registry, these would be CharacteristicName enums
    _custom_characteristics: ClassVar[dict[type, bool]] = {
        ThingyTemperatureCharacteristic: True,
        ThingyPressureCharacteristic: False,
        ThingyHumidityCharacteristic: False,
        ThingyGasCharacteristic: False,
        ThingyColorCharacteristic: False,
    }


class ThingyUserInterfaceService(BaseGattService):
    """Nordic Thingy:52 User Interface Service.

    Service UUID: EF680300-9B35-4933-9B10-52FFA9740042

    Contains user interface characteristics:
    - Button (required) - Read/notify button state

    Examples:
        >>> from bluetooth_sig.types.gatt_services import ServiceDiscoveryData
        >>> discovery_data = ServiceDiscoveryData(
        ...     service_uuid=BluetoothUUID("EF680300-9B35-4933-9B10-52FFA9740042"), characteristics=[]
        ... )
        >>> service = ThingyUserInterfaceService(discovery_data=discovery_data)
        >>> service.service_info.uuid.short_uuid
        '0300'
    """

    _info = ServiceInfo(
        uuid=BluetoothUUID(NORDIC_SERVICE_UUID_BASE % 0x0300),
        name="Thingy User Interface Service",
    )

    _custom_characteristics: ClassVar[dict[type, bool]] = {
        ThingyButtonCharacteristic: True,
    }


class ThingyMotionService(BaseGattService):
    """Nordic Thingy:52 Motion Service.

    Service UUID: EF680400-9B35-4933-9B10-52FFA9740042

    Contains motion sensor characteristics:
    - Orientation (optional)
    - Heading (optional)
    - And others not yet implemented (accelerometer, gyroscope, etc.)

    Examples:
        >>> from bluetooth_sig.types.gatt_services import ServiceDiscoveryData
        >>> discovery_data = ServiceDiscoveryData(
        ...     service_uuid=BluetoothUUID("EF680400-9B35-4933-9B10-52FFA9740042"), characteristics=[]
        ... )
        >>> service = ThingyMotionService(discovery_data=discovery_data)
        >>> service.service_info.name
        'Thingy Motion Service'
    """

    _info = ServiceInfo(
        uuid=BluetoothUUID(NORDIC_SERVICE_UUID_BASE % 0x0400),
        name="Thingy Motion Service",
    )

    _custom_characteristics: ClassVar[dict[type, bool]] = {
        ThingyOrientationCharacteristic: False,
        ThingyHeadingCharacteristic: False,
    }

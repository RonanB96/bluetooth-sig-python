"""Nordic Thingy:52 example package.

This package demonstrates how to use the bluetooth-sig-python library to create
custom characteristics and services for vendor-specific BLE devices.

The Nordic Thingy:52 is an IoT sensor kit that uses custom GATT characteristics
and services. This example shows how to:

1. Define custom characteristics with proper encoding/decoding
2. Organize characteristics into services
3. Use msgspec.Struct for structured data returns
4. Leverage the library's template system to eliminate boilerplate
5. Provide identical API to SIG-standard characteristics

Exports:
    Characteristics: Temperature, Pressure, Humidity, Gas, Color, Button, Orientation, Heading
    Services: Environment, UserInterface, Motion
    Data Structures: ThingyGasData, ThingyColorData
"""

from __future__ import annotations

__all__ = [
    # UUID Base
    "NORDIC_UUID_BASE",
    # Data structures
    "ThingyGasData",
    "ThingyColorData",
    # Characteristics
    "ThingyButtonCharacteristic",
    "ThingyColorCharacteristic",
    "ThingyGasCharacteristic",
    "ThingyHeadingCharacteristic",
    "ThingyHumidityCharacteristic",
    "ThingyOrientationCharacteristic",
    "ThingyPressureCharacteristic",
    "ThingyTemperatureCharacteristic",
    # Services
    "ThingyEnvironmentService",
    "ThingyUserInterfaceService",
    "ThingyMotionService",
]

from .thingy52_characteristics import (
    NORDIC_UUID_BASE,
    ThingyButtonCharacteristic,
    ThingyColorCharacteristic,
    ThingyColorData,
    ThingyGasCharacteristic,
    ThingyGasData,
    ThingyHeadingCharacteristic,
    ThingyHumidityCharacteristic,
    ThingyOrientationCharacteristic,
    ThingyPressureCharacteristic,
    ThingyTemperatureCharacteristic,
)
from .thingy52_services import (
    ThingyEnvironmentService,
    ThingyMotionService,
    ThingyUserInterfaceService,
)

# Registry API Reference

The registry system provides UUID resolution based on official Bluetooth SIG specifications.

## Overview

The registry system automatically loads UUID mappings from the official Bluetooth SIG assigned numbers repository. It provides bidirectional resolution between UUIDs, names, and enums.

## Using the Registry

The recommended way to use the registry is through the [Core API](core.md):

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# UUID to name
char_info = translator.resolve_by_uuid("2A19")
print(char_info.name)  # "Battery Level"

# Name to UUID
char_info = translator.resolve_by_name("Battery Level")
print(char_info.uuid)  # "2A19"
```

## Direct Registry Access

For advanced use cases, you can access the UUID registry directly:

```python
from bluetooth_sig.gatt.uuid_registry import uuid_registry
from bluetooth_sig.types.gatt_enums import CharacteristicName, ServiceName

# Get characteristic info
char_info = uuid_registry.get_characteristic_info(
    CharacteristicName.BATTERY_LEVEL
)
print(char_info.uuid)  # "2A19"
print(char_info.name)  # "Battery Level"

# Get service info
service_info = uuid_registry.get_service_info(ServiceName.BATTERY_SERVICE)
print(service_info.uuid)  # "180F"
print(service_info.name)  # "Battery Service"
```

## Enumerations

Use type-safe enums instead of string literals:

```python
from bluetooth_sig.types.gatt_enums import CharacteristicName, ServiceName

# Characteristics
CharacteristicName.BATTERY_LEVEL     # "Battery Level"
CharacteristicName.TEMPERATURE       # "Temperature"
CharacteristicName.HUMIDITY          # "Humidity"

# Services
ServiceName.BATTERY_SERVICE          # "Battery Service"
ServiceName.ENVIRONMENTAL_SENSING    # "Environmental Sensing"
ServiceName.DEVICE_INFORMATION       # "Device Information"
```

See [CharacteristicData][bluetooth_sig.types.CharacteristicData], [CharacteristicInfo][bluetooth_sig.types.CharacteristicInfo], and [ServiceInfo][bluetooth_sig.types.ServiceInfo] in the [Core API](core.md) for type definitions.

## Custom Registration

Register custom characteristics and services:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Register custom characteristic
translator.register_custom_characteristic(
    uuid="ACME0001",
    characteristic_class=MyCustomCharacteristic
)

# Register custom service
translator.register_custom_service(
    uuid="ACME1000",
    service_class=MyCustomService
)
```

See [Adding Characteristics](../guides/adding-characteristics.md) for implementation details.

## See Also

- [Core API](core.md) - Main API with type definitions
- [Adding Characteristics](../guides/adding-characteristics.md) - Custom implementation guide

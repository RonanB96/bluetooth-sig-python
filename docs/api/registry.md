# Registry API Reference

The registry system provides UUID resolution based on official Bluetooth SIG specifications.

## UUID Registry

The UUID registry is automatically loaded from official Bluetooth SIG YAML files.

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

## Name Resolution

Resolve names to UUIDs:

```python
from bluetooth_sig.core import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Service name to UUID
service = translator.resolve_by_name("Battery Service")
print(service.uuid)  # "180F"

# Characteristic name to UUID
char = translator.resolve_by_name("Battery Level")
print(char.uuid)  # "2A19"
```

## See Also

- [Core API](core.md) - Main API
- [Types & Enums](types.md) - Type definitions

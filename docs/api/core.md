# Core API Reference

The core API provides the main entry point for using the Bluetooth SIG Standards
Library.

## BluetoothSIGTranslator

::: bluetooth_sig.core.BluetoothSIGTranslator
options:
show_root_heading: true
heading_level: 3

## Quick Reference

### UUID Resolution

```python
from bluetooth_sig.core import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Resolve UUID to get information
service_info = translator.resolve_by_uuid("180F")
print(service_info.name)  # "Battery Service"

# Resolve characteristic
char_info = translator.resolve_by_uuid("2A19")
print(char_info.name)  # "Battery Level"
```

### Name Resolution

```python
# Resolve name to UUID
battery_service = translator.resolve_by_name("Battery Service")
print(battery_service.uuid)  # "180F"

battery_level = translator.resolve_by_name("Battery Level")
print(battery_level.uuid)  # "2A19"
```

### Characteristic Parsing

```python
# Parse characteristic data
battery_data = translator.parse_characteristic("2A19", bytearray([85]))
print(f"Battery: {battery_data.value}%")  # Battery: 85%

# Parse temperature
temp_data = translator.parse_characteristic("2A6E", bytearray([0x64, 0x09]))
print(f"Temperature: {temp_data.value}°C")  # Temperature: 24.36°C
```

## Error Handling

The core API can raise several exceptions:

```python
from bluetooth_sig.gatt.exceptions import (
    UUIDResolutionError,
    InsufficientDataError,
    ValueRangeError,
)

try:
    result = translator.parse_characteristic("2A19", data)
except UUIDResolutionError:
    print("Unknown UUID")
except InsufficientDataError:
    print("Data too short")
except ValueRangeError:
    print("Value out of range")
```

## See Also

- [GATT Layer API](gatt.md) - Lower-level GATT APIs
- [Registry API](registry.md) - UUID registry system
- [Usage Guide](../usage.md) - Practical examples

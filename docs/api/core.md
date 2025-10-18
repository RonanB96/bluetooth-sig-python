# Core API Reference

The core API provides the main entry point for using the Bluetooth SIG Standards Library.

::: bluetooth_sig.BluetoothSIGTranslator
    options:
      show_root_heading: false
      heading_level: 2
      show_source: true

## Quick Examples

### Parse Characteristic Data

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Parse battery level - returns CharacteristicData
result = translator.parse_characteristic("2A19", bytearray([85]))
print(f"Battery: {result.value}%")  # Battery: 85%
print(f"Unit: {result.info.unit}")  # Unit: %
```

The [parse_characteristic][bluetooth_sig.BluetoothSIGTranslator.parse_characteristic] method returns a [CharacteristicData][bluetooth_sig.types.CharacteristicData] object.

### UUID Resolution

```python
# Resolve UUID to get information
service_info = translator.get_sig_info_by_uuid("180F")
print(service_info.name)  # "Battery Service"

# Resolve characteristic
char_info = translator.get_sig_info_by_uuid("2A19")
print(char_info.name)  # "Battery Level"
```

See [get_sig_info_by_uuid][bluetooth_sig.BluetoothSIGTranslator.get_sig_info_by_uuid] for full details.

battery_level = translator.get_sig_info("Battery Level")

## Name Resolution

```python
# Resolve name to UUID
battery_service = translator.get_sig_info_by_name("Battery Service")
print(battery_service.uuid)  # "180F"

battery_level = translator.get_sig_info_by_name("Battery Level")
print(battery_level.uuid)  # "2A19"
```

## Error Handling

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

- [GATT Layer](gatt.md) - Lower-level GATT APIs
- [Registry System](registry.md) - UUID registry details
- [Usage Guide](../usage.md) - Practical examples

## Type Definitions

These types are returned by the core API methods:

::: bluetooth_sig.types.CharacteristicData
    options:
      show_root_heading: true
      heading_level: 3
      show_source: false
      members: true

::: bluetooth_sig.types.CharacteristicInfo
    options:
      show_root_heading: true
      heading_level: 3
      show_source: false
      members: true

::: bluetooth_sig.types.ServiceInfo
    options:
      show_root_heading: true
      heading_level: 3
      show_source: false
      members: true

::: bluetooth_sig.types.ValidationResult
    options:
      show_root_heading: true
      heading_level: 3
      show_source: false
      members: true

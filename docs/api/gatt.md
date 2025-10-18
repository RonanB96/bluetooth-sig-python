# GATT Layer API Reference

The GATT layer provides the fundamental building blocks for Bluetooth characteristic
parsing.

## Overview

The GATT layer consists of:

- **Characteristic parsers** - 70+ implementations for standard characteristics
- **Service definitions** - Organize characteristics into services
- **Validation logic** - Ensure data integrity
- **Exception types** - Clear error reporting

## Base Classes

### BaseCharacteristic

::: bluetooth_sig.BaseCharacteristic
    options:
      show_root_heading: false
      heading_level: 4
      members:
        - decode_value
        - encode_value
        - validate

All characteristic implementations inherit from [BaseCharacteristic][].

### BaseService

::: bluetooth_sig.gatt.services.base.BaseGattService
    options:
      show_root_heading: false
      heading_level: 4

All service definitions inherit from BaseGattService.

## Registries

### CharacteristicRegistry

::: bluetooth_sig.gatt.characteristics.registry.CharacteristicRegistry
    options:
      show_root_heading: false
      heading_level: 4
      members:
        - register
        - get

Use [CharacteristicRegistry][] to register custom characteristics.

### GattServiceRegistry

::: bluetooth_sig.gatt.services.registry.GattServiceRegistry
    options:
      show_root_heading: false
      heading_level: 4
      members:
        - register
        - get

Use [GattServiceRegistry][] to register custom services.

## Common Characteristic Examples

### Battery Level

```python
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

char = BatteryLevelCharacteristic()
value = char.decode_value(bytearray([85]))
print(f"Battery: {value}%")  # Battery: 85%
```

### Temperature

```python
from bluetooth_sig.gatt.characteristics import TemperatureCharacteristic

char = TemperatureCharacteristic()
value = char.decode_value(bytearray([0x64, 0x09]))
print(f"Temperature: {value}°C")  # Temperature: 24.36°C
```

### Humidity

```python
from bluetooth_sig.gatt.characteristics import HumidityCharacteristic

char = HumidityCharacteristic()
value = char.decode_value(bytearray([0x3A, 0x13]))
print(f"Humidity: {value}%")  # Humidity: 49.42%
```

## Exceptions

### InsufficientDataError

Raised when data is too short for the characteristic.

```python
from bluetooth_sig.gatt.exceptions import InsufficientDataError

try:
    char.decode_value(bytearray([]))  # Empty
except InsufficientDataError as e:
    print(f"Error: {e}")
```

### ValueRangeError

Raised when value is outside valid range.

```python
from bluetooth_sig.gatt.exceptions import ValueRangeError

try:
    char.decode_value(bytearray([150]))  # > 100%
except ValueRangeError as e:
    print(f"Error: {e}")
```

## See Also

- [Core API](core.md) - High-level `BluetoothSIGTranslator` API
- [Supported Characteristics](../supported-characteristics.md) - Full list
- [Architecture](../architecture.md) - Design details
- [Adding Characteristics](../guides/adding-characteristics.md) - Custom implementations

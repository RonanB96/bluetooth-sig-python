# GATT Layer API Reference

The GATT layer provides the fundamental building blocks for Bluetooth characteristic
parsing.

## Overview

The GATT layer consists of:

- **Characteristic parsers** - 70+ implementations for standard characteristics
- **Service definitions** - Organize characteristics into services
- **Validation logic** - Ensure data integrity
- **Exception types** - Clear error reporting

## Common Characteristics

### Battery Level (0x2A19)

Parse battery percentage (0-100%).

```python
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

char = BatteryLevelCharacteristic()
value = char.decode_value(bytearray([85]))
print(f"Battery: {value}%")  # Battery: 85%
```

### Temperature (0x2A6E)

Parse temperature in °C with 0.01°C resolution.

```python
from bluetooth_sig.gatt.characteristics import TemperatureCharacteristic

char = TemperatureCharacteristic()
value = char.decode_value(bytearray([0x64, 0x09]))
print(f"Temperature: {value}°C")  # Temperature: 24.36°C
```

### Humidity (0x2A6F)

Parse humidity percentage with 0.01% resolution.

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

- [Core API](core.md) - High-level API
- [Architecture](../architecture.md) - Design details

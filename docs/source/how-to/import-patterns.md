# Import Patterns

This guide shows you how to import the parts of `bluetooth-sig` you need for different tasks.

## Quick Reference

Import the primary API for most tasks:

```python
from bluetooth_sig import BluetoothSIGTranslator, Device
```

For Device usage, you also need a connection manager:

```python
from examples.connection_managers.bleak_retry import (
    BleakRetryConnectionManager,
)
```

Import from submodules when you need specific features:

```python
from bluetooth_sig.advertising import AdvertisingPDUParser
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
```

## How to Import for Common Tasks

### Task: Parse characteristic data (type-safe)

Import the characteristic class directly for full type inference:

```python
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

battery = BatteryLevelCharacteristic()
level = battery.parse_value(bytearray([85]))  # IDE knows: int
encoded = battery.build_value(85)  # Encode back to bytes
```

### Task: Parse unknown characteristics (dynamic)

Use the Translator when scanning unknown devices:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# UUID and data from device discovery (replace with actual BLE reads)
uuid = "2A19"  # Battery Level
raw_data = bytearray([75])

value = translator.parse_characteristic(uuid, raw_data)
info = translator.get_characteristic_info_by_uuid(uuid)
print(f"{info.name}: {value}")  # Battery Level: 75
```

### Task: Parse advertising packets

Import from the advertising module:

```python
from bluetooth_sig.advertising import AdvertisingPDUParser

parser = AdvertisingPDUParser()
raw_adv_bytes = bytearray([0x02, 0x01, 0x06])  # Example advertising data
adv_data = parser.parse_advertising_data(raw_adv_bytes)
```

### Task: Work with multiple characteristics (type-safe)

Import characteristic classes for full IDE support:

```python
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    BodySensorLocationCharacteristic,
    HeartRateMeasurementCharacteristic,
)

# Example data (replace with actual BLE reads)
hr_bytes = bytearray([0x00, 75])  # Heart rate 75 bpm
loc_bytes = bytearray([0x01])  # Chest location
bat_bytes = bytearray([85])  # 85% battery

hr_char = HeartRateMeasurementCharacteristic()
sensor_char = BodySensorLocationCharacteristic()
battery_char = BatteryLevelCharacteristic()

# All have full type inference
hr_data = hr_char.parse_value(hr_bytes)  # HeartRateData
location = sensor_char.parse_value(loc_bytes)  # int
level = battery_char.parse_value(bat_bytes)  # int
```

### Task: Add type hints to your code

Import the data types you need. The library returns parsed values directly,
so type hints use the actual value types:

```python
from bluetooth_sig.gatt.characteristics import (
    HeartRateMeasurementCharacteristic,
)

# Example data (replace with actual BLE reads)
raw_bytes = bytearray([0x00, 72])  # Heart rate 72 bpm

# Type annotations use the characteristic's return type
hr_char = HeartRateMeasurementCharacteristic()
hr_data = hr_char.parse_value(raw_bytes)  # IDE knows: HeartRateData

# For dynamic parsing, return type is Any
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
uuid = "2A37"
data = bytearray([0x00, 72])
value = translator.parse_characteristic(uuid, data)  # Returns Any
```

### Task: Use the Device abstraction (type-safe)

Import Device with characteristic classes:

```python
# SKIP: Requires async context and BLE hardware
from bluetooth_sig import Device
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
from examples.connection_managers.bleak_retry import (
    BleakRetryConnectionManager,
)

connection_manager = BleakRetryConnectionManager("AA:BB:CC:DD:EE:FF")
device = Device(connection_manager)

# Type-safe read - IDE knows level is int
battery = BatteryLevelCharacteristic()
level = await device.read_characteristic(battery)
```

### Task: Use the Device abstraction (dynamic)

Import Device with Translator for unknown devices:

```python
# SKIP: Requires async context and BLE hardware
from bluetooth_sig import BluetoothSIGTranslator, Device
from examples.connection_managers.bleak_retry import (
    BleakRetryConnectionManager,
)

translator = BluetoothSIGTranslator()
connection_manager = BleakRetryConnectionManager("AA:BB:CC:DD:EE:FF")
device = Device(connection_manager, translator)

# Dynamic read - returns CharacteristicData with Any value
uuid_from_discovery = "2A19"  # Example: Battery Level from service discovery
result = await device.read_characteristic_by_uuid(uuid_from_discovery)
```

### Task: Work with registries programmatically

Import from the registry module:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
char_uuid = translator.get_characteristic_uuid_by_name("Battery Level")
```

### Task: Create a custom characteristic

Import base classes:

```python
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.types.data_types import CharacteristicInfo


class MyCustomCharacteristic(BaseCharacteristic):
    _info = CharacteristicInfo(
        uuid="12345678-1234-5678-1234-56789abcdef0",
        name="My Custom Characteristic",
    )
```

## What's Available at Each Level

### Top level (`from bluetooth_sig import X`)

Only the primary API and essential types:

- `BluetoothSIGTranslator` - Main parsing API
- `AsyncParsingSession` - Async context manager
- `Device` - High-level device abstraction
- `CharacteristicData` - Return type for parsed data
- `CharacteristicInfo` - Characteristic metadata
- `ServiceInfo` - Service metadata
- `ValidationResult` - Validation results
- `SIGInfo` - SIG standard info
- `__version__` - Package version

### Submodules (explicit imports)

Import from specific modules as needed:

**Advertising**: `bluetooth_sig.advertising`

- `AdvertisingPDUParser`
- `AdvertisingDataInterpreter`
- `AdvertisingInterpreterRegistry`

**Characteristics**: `bluetooth_sig.gatt.characteristics`

- All characteristic classes (e.g., `BatteryLevelCharacteristic`)

**Services**: `bluetooth_sig.gatt.services`

- All service classes (e.g., `BatteryService`)

**Registries**: `bluetooth_sig.registry`

- UUID resolution utilities
- YAML cross-reference system

**Base classes** (for extending): `bluetooth_sig.gatt.characteristics.base`

- `BaseCharacteristic`
- `BaseGattService`

**Connection managers** (from examples): `examples.connection_managers`

- `BleakRetryConnectionManager` - Bleak-based async manager with retry logic
- `SimplePyBLEConnectionManager` - SimplePyBLE synchronous adapter
- `BluePyConnectionManager` - BluePy adapter

These implement `ConnectionManagerProtocol` and are required for Device usage.

## Troubleshooting Imports

**Problem**: `ImportError: cannot import name 'AdvertisingPDUParser'`

**Solution**: Use explicit submodule import:

```python
from bluetooth_sig.advertising import AdvertisingPDUParser
```

**Problem**: Need to find where a class lives

**Solution**: Check the module structure:

- Advertising → `bluetooth_sig.advertising`
- Characteristics → `bluetooth_sig.gatt.characteristics`
- Services → `bluetooth_sig.gatt.services`
- Device → `bluetooth_sig.device`
- Registries → `bluetooth_sig.registry`

## Best Practices

1. **Start simple**: Begin with `BluetoothSIGTranslator` from the top level
2. **Import what you need**: Only import from submodules when necessary
3. **No wildcards**: Avoid `from bluetooth_sig import *`
4. **Group logically**: Keep standard library, third-party, and bluetooth-sig imports separated
5. **Be explicit**: Clear imports make code easier to understand and maintain

## Related Documentation

1. **Clearer intent**: `from bluetooth_sig.gatt.characteristics import X` clearly indicates you're working with GATT characteristics
2. **Easier maintenance**: Changes to characteristics don't require updating top-level `__init__.py`
3. **Better documentation**: Users can navigate to the specific module they need rather than wondering where features come from

## Best Practices

1. **Start with the primary API**: Always begin with `BluetoothSIGTranslator` at the top level
2. **Import what you use**: Only import from submodules when you need specific features
3. **Use type hints**: Import data types (`CharacteristicInfo`, etc.) for better type checking
4. **Avoid wildcards**: Never use `from bluetooth_sig import *` - be explicit about what you're importing
5. **Group imports logically**:

```python
# Standard library
import asyncio

# Third-party
from bleak import BleakClient

# bluetooth-sig primary API
from bluetooth_sig import BluetoothSIGTranslator, CharacteristicInfo

# bluetooth-sig submodules
from bluetooth_sig.advertising import AdvertisingPDUParser
from bluetooth_sig.gatt.characteristics import (
    HeartRateMeasurementCharacteristic,
)
```

## Related Documentation

- [Usage Guide](usage.md) - Complete usage examples
- [Migration Guide](migration.md) - Upgrading from earlier versions
- [API Reference](../api/index.md) - Complete API documentation
- [Architecture Overview](../explanation/architecture/overview.md) - Understanding the design (for context on why imports are structured this way)

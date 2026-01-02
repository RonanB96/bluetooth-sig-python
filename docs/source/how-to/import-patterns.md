# Import Patterns

This guide shows you how to import the parts of `bluetooth-sig` you need for different tasks.

## Quick Reference

Import the primary API for most tasks:

```python
from bluetooth_sig import BluetoothSIGTranslator, Device
```

For Device usage, you also need a connection manager:

```python
from examples.connection_managers.bleak_retry import BleakRetryConnectionManager
```

Import from submodules when you need specific features:

```python
from bluetooth_sig.advertising import AdvertisingPDUParser
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
```

## How to Import for Common Tasks

### Task: Parse characteristic data

Use the primary API:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
result = translator.parse_characteristic("2A19", bytes([85]))
```

### Task: Parse advertising packets

Import from the advertising module:

```python
from bluetooth_sig.advertising import AdvertisingPDUParser

parser = AdvertisingPDUParser()
raw_adv_bytes = bytearray([0x02, 0x01, 0x06])  # Example advertising data
adv_data = parser.parse_advertising_data(raw_adv_bytes)
```

### Task: Work with a specific characteristic

Import the characteristic class directly:

```python
from bluetooth_sig.gatt.characteristics import HeartRateMeasurementCharacteristic

hr_char = HeartRateMeasurementCharacteristic()
hr_bytes = bytearray([0x00, 0x3C])  # Example: 60 BPM
hr_data = hr_char.parse_value(hr_bytes)
```

### Task: Add type hints to your code

Import the data types you need:

```python
from bluetooth_sig import CharacteristicData, CharacteristicInfo

def process_characteristic(data: CharacteristicData) -> None:
    if data.parse_success:
        print(f"{data.info.name}: {data.value}")
```

### Task: Use the Device abstraction

Import Device and a connection manager:

```python
from bluetooth_sig import BluetoothSIGTranslator, Device
from examples.connection_managers.bleak_retry import BleakRetryConnectionManager

translator = BluetoothSIGTranslator()
connection_manager = BleakRetryConnectionManager("AA:BB:CC:DD:EE:FF")
device = Device(connection_manager, translator)
```

**Note**: Device requires a connection manager for BLE operations (connect, read, write, notifications). The address is provided to the connection manager, eliminating redundancy. Example implementations for Bleak, SimpleBLE, and BluePy are in `examples/connection_managers/`.

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
3. **Use type hints**: Import data types (`CharacteristicData`, `CharacteristicInfo`, etc.) for better type checking
4. **Avoid wildcards**: Never use `from bluetooth_sig import *` - be explicit about what you're importing
5. **Group imports logically**:

```python
# Standard library
import asyncio

# Third-party
from bleak import BleakClient

# bluetooth-sig primary API
from bluetooth_sig import BluetoothSIGTranslator, CharacteristicData

# bluetooth-sig submodules
from bluetooth_sig.advertising import AdvertisingPDUParser
from bluetooth_sig.gatt.characteristics import HeartRateMeasurementCharacteristic
```

## Related Documentation

- [Usage Guide](usage.md) - Complete usage examples
- [Migration Guide](migration.md) - Upgrading from earlier versions
- [API Reference](../api/index.md) - Complete API documentation
- [Architecture Overview](../explanation/architecture/overview.md) - Understanding the design (for context on why imports are structured this way)

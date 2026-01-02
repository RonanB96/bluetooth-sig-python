# Bluetooth SIG Standards Library

[![Coverage Status](https://img.shields.io/endpoint?url=https://ronanb96.github.io/bluetooth-sig-python/coverage/coverage-badge.json)](https://ronanb96.github.io/bluetooth-sig-python/coverage/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/bluetooth-sig.svg)](https://pypi.org/project/bluetooth-sig/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://ronanb96.github.io/bluetooth-sig-python/)

A pure Python library for Bluetooth SIG standards interpretation, providing comprehensive GATT characteristic, service, and advertisement parsing with automatic UUID resolution.

**[📚 Full Documentation](https://ronanb96.github.io/bluetooth-sig-python/)** | **[🚀 Quick Start](https://ronanb96.github.io/bluetooth-sig-python/quickstart/)** | **[📖 API Reference](https://ronanb96.github.io/bluetooth-sig-python/api/core/)**

## Features

- ✅ **Standards-Based**: Official Bluetooth SIG YAML registry with automatic UUID resolution
- ✅ **Type-Safe**: Convert raw Bluetooth data to meaningful values with comprehensive typing
- ✅ **Modern Python**: msgspec-based design with Python 3.9+ compatibility
- ✅ **Comprehensive**: Support for 200+ GATT characteristics across multiple service categories
- ✅ **Production Ready**: Extensive validation and comprehensive testing
- ✅ **Flexible Validation**: Enable/disable validation per-characteristic for testing or debugging
- ✅ **Framework Agnostic**: Works with any BLE library (bleak, simplepyble, etc.)

## Installation

```bash
pip install bluetooth-sig
```

## Quick Start

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import ServiceName, CharacteristicName

translator = BluetoothSIGTranslator()

# Type-safe service discovery
service_info = translator.get_service_info_by_name(ServiceName.BATTERY.value)
print(f"Service: {service_info.name}")  # Service: Battery
print(f"UUID: {service_info.uuid}")  # UUID: 0000180F-0000-1000-8000-00805F9B34FB

# Type-safe characteristic info access
char_info = translator.get_characteristic_info_by_name(CharacteristicName.BATTERY_LEVEL)
print(f"Characteristic: {char_info.name}")  # Characteristic: Battery Level
print(f"UUID: {char_info.uuid}")  # UUID: 00002A19-0000-1000-8000-00805F9B34FB
```

## Usage Approaches

**Choose the approach that fits your use case** - all patterns are fully supported:

### Type-Safe Characteristic Classes

Direct access when you know the characteristic type:

```python
from bluetooth_sig.gatt.characteristics.battery_level import BatteryLevelCharacteristic
from bluetooth_sig.gatt.characteristics.acceleration_3d import Acceleration3DCharacteristic

# Simple characteristic
battery_char = BatteryLevelCharacteristic()
raw_data = bytearray([85])  # Example data: 85%
level = battery_char.parse_value(raw_data).value  # Returns: int (0-100)
encoded = battery_char.build_value(85)  # Returns: bytearray([85])

# Complex characteristic with typed results
accel_char = Acceleration3DCharacteristic()
accel_raw_data = bytearray([0x96, 0xCE, 0xD4])  # Example 3D acceleration data (3 bytes)
parsed = accel_char.parse_value(accel_raw_data)
data = parsed.value  # VectorData(x_axis=..., y_axis=..., z_axis=...)
encoded = accel_char.build_value(data)  # Type-safe encoding and returns bytearray to writing
```

### Translator with Enums

UUID resolution with characteristic name enums:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()

# Get UUID from characteristic name
char_uuid = translator.get_characteristic_uuid_by_name(CharacteristicName.BATTERY_LEVEL)
raw_data = await client.read_gatt_char(str(char_uuid))

# Parse with automatic type resolution
result = translator.parse_characteristic(str(char_uuid), raw_data)
print(f"{result.info.name}: {result.value}%")

# Encode with type safety
data = translator.encode_characteristic(str(char_uuid), 85)
await client.write_gatt_char(str(char_uuid), data)  # SKIP: async write operation
```

### Device Class with Connection Management

High-level device abstraction (requires connection manager implementation):

```python
# SKIP: Requires connection manager implementation
from bluetooth_sig.device import Device
from bluetooth_sig.types.gatt_enums import CharacteristicName

device = Device(connection_manager, translator)
await device.connect()

# Type-safe reads with automatic parsing
battery = await device.read(CharacteristicName.BATTERY_LEVEL)
print(f"Battery: {battery.value}%")

# Type-safe writes
data = translator.encode_characteristic_by_name(CharacteristicName.BATTERY_LEVEL, 85)
await device.write(CharacteristicName.BATTERY_LEVEL, data)
```

### Parsing Unknown Characteristics

Discover and parse characteristics from unknown devices:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Loop through discovered characteristic UUIDs
for char in client.services.characteristics:
    uuid_str = str(char.uuid)
    if translator.supports(uuid_str):
        raw_data = await client.read_gatt_char(uuid_str)
        result = translator.parse_characteristic(uuid_str, raw_data)
        print(f"{result.info.name}: {result.value}")
    else:
        print(f"Unknown characteristic UUID: {uuid_str}")
```

**[→ See comprehensive usage guide](https://ronanb96.github.io/bluetooth-sig-python/usage/)** for validation control, context parameters, and advanced patterns

## What This Library Does

Enables high-level Bluetooth applications without low-level expertise:

- ✅ **UUID abstraction** - Resolves unknown UUIDs to characteristic types; provides enum/class access for known characteristics
- ✅ **Automatic encoding/decoding** - Converts between raw bytes and typed Python objects using standards-compliant parsing
- ✅ **Type-safe data structures** - Returns structured data objects instead of raw byte arrays (e.g., `VectorData`, `TemperatureMeasurement`)
- ✅ **Framework-agnostic design** - Works with any BLE library (bleak, simplepyble, etc.) using a common connection manager interface
- ✅ **Standards-based parsing** - 200+ GATT characteristics according to official Bluetooth SIG specifications
- ✅ **Extensible** - Supports custom characteristics and services with the same type-safe patterns

## What This Library Does NOT Do

- ❌ **BLE transport layer** - Requires a BLE library (bleak, simplepyble, etc.); but this lib provides Device class abstraction over these libraries
- ❌ **Firmware implementation** - Client-side parsing and encoding only

**[Learn more about what problems this solves →](https://ronanb96.github.io/bluetooth-sig-python/what-it-solves/)**

## Integration with BLE Libraries

Quick integration with any BLE library using the translator directly:

```python
# SKIP: Requires BLE hardware and connection setup
from bleak import BleakClient
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()

# Get UUID from characteristic name (do once, reuse)
battery_uuid = translator.get_characteristic_uuid_by_name(CharacteristicName.BATTERY_LEVEL)

async with BleakClient(address) as client:
    # Read: bleak handles connection, bluetooth-sig handles parsing
    raw_data = await client.read_gatt_char(str(battery_uuid))
    result = translator.parse_characteristic(str(battery_uuid), raw_data)
    print(f"Battery: {result.value}%")

    # Write: bluetooth-sig handles encoding, bleak handles transmission
    data = translator.encode_characteristic(str(battery_uuid), 85)
    await client.write_gatt_char(str(battery_uuid), data)
```

**Recommended:** Implement the connection manager interface to use the Device class for BLE-library-agnostic design.

**[→ See BLE integration guide](https://ronanb96.github.io/bluetooth-sig-python/guides/ble-integration/)** for connection manager implementation examples with bleak, bleak-retry-connector, and simplepyble.

## Supported Characteristics

200+ GATT characteristics across multiple categories:

- **Battery Service**: Level, Power State
- **Environmental Sensing**: Temperature, Humidity, Pressure, Air Quality
- **Health Monitoring**: Heart Rate, Blood Pressure, Glucose
- **Fitness Tracking**: Running/Cycling Speed, Cadence, Power
- **Device Information**: Manufacturer, Model, Firmware Version
- And many more...

**[View full list of supported services →](https://ronanb96.github.io/bluetooth-sig-python/usage/)**

## Documentation

- **[Full Documentation](https://ronanb96.github.io/bluetooth-sig-python/)** - Complete guides and API reference
- **[Quick Start Guide](https://ronanb96.github.io/bluetooth-sig-python/quickstart/)** - Get started in 5 minutes
- **[API Reference](https://ronanb96.github.io/bluetooth-sig-python/api/core/)** - Detailed API documentation
- **[Examples](https://github.com/ronanb96/bluetooth-sig-python/tree/main/examples)** - Integration examples with various BLE libraries

## Contributing

Contributions are welcome! Please see the **[Contributing Guide](https://ronanb96.github.io/bluetooth-sig-python/contributing/)** for details.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/ronanb96/bluetooth-sig-python/blob/main/LICENSE) file for details.

## Links

- **PyPI**: <https://pypi.org/project/bluetooth-sig/>
- **Documentation**: <https://ronanb96.github.io/bluetooth-sig-python/>
- **Source Code**: <https://github.com/ronanb96/bluetooth-sig-python>
- **Issue Tracker**: <https://github.com/ronanb96/bluetooth-sig-python/issues>

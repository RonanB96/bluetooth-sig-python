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
- ✅ **Type-Safe**: Characteristic classes provide compile-time type checking; UUID strings return dynamic types
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

**Recommended**: Use characteristic classes for type-safe parsing when you know the characteristic type.

```python
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

# Type-safe: return type is automatically inferred as int
char = BatteryLevelCharacteristic()
level = char.parse_value(bytearray([85]))  # IDE knows this is int
print(f"Battery: {level}%")  # Battery: 85%

encoded = char.build_value(85)
```

For unknown characteristics discovered at runtime, use UUID strings:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import ServiceName, CharacteristicName

translator = BluetoothSIGTranslator()

# Service discovery: identify services by UUID or name
service_info = translator.get_service_info_by_name(ServiceName.BATTERY.value)
print(f"Service: {service_info.name}")  # Service: Battery
print(f"UUID: {service_info.uuid}")  # UUID: 0000180F-0000-1000-8000-00805F9B34FB

# Characteristic parsing: returns Any (type determined at runtime)
result = translator.parse_characteristic("2A19", bytearray([85]))
print(f"{result.info.name}: {result.value}%")  # Battery Level: 85%
```

## Usage Approaches

**Choose the approach that fits your use case:**

### Direct Characteristic Classes

When you know the characteristic type, use the class directly for full type inference:

```python
from bluetooth_sig.gatt.characteristics import HeartRateMeasurementCharacteristic

# Complex: structured dataclass with autocompletion
heart_rate = HeartRateMeasurementCharacteristic()
hr_data = heart_rate.parse_value(bytearray([0x00, 72]))  # IDE infers HeartRateData
print(f"{hr_data.heart_rate} bpm")
encoded = heart_rate.build_value(hr_data)
```

### Translator API

For scanning unknown devices or working with UUID strings:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Discover and parse any characteristic by UUID
for char in client.services.characteristics:
    uuid_str = str(char.uuid)
    if translator.supports(uuid_str):
        raw_data = await client.read_gatt_char(uuid_str)  # SKIP: async
        result = translator.parse_characteristic(uuid_str, raw_data)
        print(f"{result.info.name}: {result.value}")  # Returns Any
    else:
        print(f"Unknown characteristic UUID: {uuid_str}")
```

Pass a characteristic class to the translator for type-safe parsing:

```python
from bluetooth_sig.gatt.characteristics import TemperatureMeasurementCharacteristic

# Type-safe via translator: IDE infers TemperatureMeasurementData
temp = translator.parse_characteristic(TemperatureMeasurementCharacteristic, raw_data)
print(f"{temp.temperature}°C")
```

### Device Abstraction

Combines connection management with type-safe operations:

```python
# SKIP: Requires connection manager implementation
from bluetooth_sig.device import Device
from bluetooth_sig.gatt.characteristics import HumidityCharacteristic

device = Device(connection_manager, translator)
await device.connect()

# Type-safe: IDE infers float from characteristic class
humidity = await device.read(HumidityCharacteristic)
print(f"Humidity: {humidity}%")

# Dynamic: returns Any when using enum/string
from bluetooth_sig.types.gatt_enums import CharacteristicName
result = await device.read(CharacteristicName.TEMPERATURE)
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

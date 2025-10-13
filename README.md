# Bluetooth SIG Standards Library

[![Coverage Status](https://img.shields.io/endpoint?url=https://ronanb96.github.io/bluetooth-sig-python/coverage/coverage-badge.json)](https://ronanb96.github.io/bluetooth-sig-python/coverage/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/bluetooth-sig.svg)](https://pypi.org/project/bluetooth-sig/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://ronanb96.github.io/bluetooth-sig-python/)

A pure Python library for Bluetooth SIG standards interpretation, providing comprehensive GATT characteristic and service parsing with automatic UUID resolution.

**[📚 Full Documentation](https://ronanb96.github.io/bluetooth-sig-python/)** | **[🚀 Quick Start](https://ronanb96.github.io/bluetooth-sig-python/quickstart/)** | **[📖 API Reference](https://ronanb96.github.io/bluetooth-sig-python/api/core/)**

## Features

- ✅ **Standards-Based**: Official Bluetooth SIG YAML registry with automatic UUID resolution
- ✅ **Type-Safe**: Convert raw Bluetooth data to meaningful values with comprehensive typing
- ✅ **Modern Python**: Dataclass-based design with Python 3.9+ compatibility
- ✅ **Comprehensive**: Support for 70+ GATT characteristics across multiple service categories
- ✅ **Production Ready**: Extensive validation and comprehensive testing
- ✅ **Framework Agnostic**: Works with any BLE library (bleak, simplepyble, etc.)

## Installation

```bash
pip install bluetooth-sig
```

## Quick Start

```python
from bluetooth_sig.core import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Resolve UUIDs
service_info = translator.resolve_uuid("180F")
print(f"Service: {service_info.name}")  # "Battery Service"

# Parse characteristic data
battery_data = translator.parse_characteristic_data("2A19", bytearray([85]))
print(f"Battery: {battery_data.value}%")  # "Battery: 85%"
```

## What This Library Does

- ✅ **Parse Bluetooth GATT characteristics** according to official specifications
- ✅ **Resolve UUIDs** to human-readable service and characteristic names
- ✅ **Provide type-safe data structures** for all parsed values
- ✅ **Work with any BLE library** (bleak, simplepyble, etc.)

## What This Library Does NOT Do

- ❌ **BLE device connections** - Use bleak, simplepyble, or similar libraries
- ❌ **Custom/proprietary protocols** - Only official Bluetooth SIG standards
- ❌ **Firmware implementation** - This is a client-side library

**[Learn more about what problems this solves →](https://ronanb96.github.io/bluetooth-sig-python/what-it-solves/)**

## Integration with BLE Libraries

Works seamlessly with any BLE connection library:

```python
from bleak import BleakClient
from bluetooth_sig.core import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

async with BleakClient(address) as client:
    # bleak handles connection
    raw_data = await client.read_gatt_char("2A19")
    
    # bluetooth-sig handles parsing
    result = translator.parse_characteristic_data("2A19", raw_data)
    print(f"Battery: {result.value}%")
```

See the **[BLE Integration Guide](https://ronanb96.github.io/bluetooth-sig-python/guides/ble-integration/)** for examples with bleak, bleak-retry-connector, and simplepyble.

## Supported Characteristics

70+ GATT characteristics across multiple categories:

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
- **[Examples](examples/)** - Integration examples with various BLE libraries

## Contributing

Contributions are welcome! Please see the **[Contributing Guide](https://ronanb96.github.io/bluetooth-sig-python/contributing/)** for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- **PyPI**: https://pypi.org/project/bluetooth-sig/
- **Documentation**: https://ronanb96.github.io/bluetooth-sig-python/
- **Source Code**: https://github.com/RonanB96/bluetooth-sig-python
- **Issue Tracker**: https://github.com/RonanB96/bluetooth-sig-python/issues
- **Changelog**: https://github.com/RonanB96/bluetooth-sig-python/blob/main/HISTORY.md

# Bluetooth SIG Standards Library

A pure Python library for Bluetooth SIG standards interpretation

![Coverage Status](https://img.shields.io/endpoint?url=https://ronanb96.github.io/bluetooth-sig-python/coverage/coverage-badge.json)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/bluetooth-sig.svg)](https://pypi.org/project/bluetooth-sig/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Welcome

The **Bluetooth SIG Standards Library** provides comprehensive GATT characteristic and service parsing with automatic UUID resolution. Built on the official Bluetooth SIG specifications, it offers a robust, standards-compliant architecture for Bluetooth device communication with type-safe data parsing and clean API design.

## Key Features

- ✅ **Standards-Based**: Official Bluetooth SIG YAML registry with automatic UUID resolution
- ✅ **Type-Safe**: Characteristic classes provide compile-time type checking and IDE autocomplete
- ✅ **Modern Python**: msgspec-based design with Python 3.9+ compatibility
- ✅ **Comprehensive**: Support for 200+ GATT characteristics across multiple service categories
- ✅ **Framework Agnostic**: Works with any BLE connection library (bleak, simplepyble, etc.)

## Quick Example

**Device abstraction** (recommended for backend abstraction):

```python
# SKIP: Requires actual BLE device connection
from bluetooth_sig import BluetoothSIGTranslator, Device
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

# Connection manager for your BLE backend
from examples.connection_managers.bleak_retry import (
    BleakRetryClientManager,
)


async def main():
    translator = BluetoothSIGTranslator()
    device = Device(
        BleakRetryClientManager("AA:BB:CC:DD:EE:FF"), translator
    )

    await device.connect()
    battery = await device.read(BatteryLevelCharacteristic)  # IDE knows: int
    print(f"Battery: {battery}%")
    await device.disconnect()
```

**Type-safe parsing** (direct characteristic access):

```python
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

battery = BatteryLevelCharacteristic()
level = battery.parse_value(bytearray([85]))  # IDE infers int
print(f"Battery: {level}%")  # Battery: 85%
```

**Dynamic parsing** (for scanning unknown devices):

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
result = translator.parse_characteristic("2A19", bytearray([85]))
print(f"Battery Level: {result}%")  # Battery Level: 85%
```

## Getting Started

::::{grid} 2
:gutter: 3

:::{grid-item-card} ⚡ Quick Start
:link: tutorials/quickstart
:link-type: doc

Get up and running in minutes
:::

:::{grid-item-card} 📦 Installation
:link: tutorials/installation
:link-type: doc

Install via pip or from source
:::

:::{grid-item-card} 📖 Usage Guide
:link: how-to/usage
:link-type: doc

Real-world usage patterns
:::

:::{grid-item-card} 📚 API Reference
:link: api/index
:link-type: doc

Detailed API documentation
:::

::::

## Which Guide Should I Read?

| I want to...                                | Read this                                             |
| ------------------------------------------- | ----------------------------------------------------- |
| Get started quickly                         | [Quick Start](tutorials/quickstart.md)                |
| Choose the right API approach               | [Choosing the Right API](explanation/api-overview.md) |
| Integrate with bleak or other BLE libraries | [BLE Integration Guide](how-to/ble-integration.md)    |
| See real-world usage patterns               | [Usage Guide](how-to/usage.md)                        |
| Use async patterns                          | [Async Usage](how-to/async-usage.md)                  |
| Understand the library's purpose            | [Why Use This Library](explanation/why-use.md)        |

## Why Choose This Library?

Unlike other Bluetooth libraries that focus on device connectivity, this library specializes in **standards interpretation**. It bridges the gap between raw BLE data and meaningful application-level information.

[Learn more about what this library solves →](explanation/why-use.md)

## Support

- **Issues**: [GitHub Issues](https://github.com/ronanb96/bluetooth-sig-python/issues)
- **Source Code**: [GitHub Repository](https://github.com/ronanb96/bluetooth-sig-python)
- **Documentation**: You're here! 🎉
- **Test Coverage**: Available in CI artifacts

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/RonanB96/bluetooth-sig-python/blob/main/LICENSE) file for details.

```{toctree}
:maxdepth: 2
:hidden:

tutorials/index
how-to/index
api/index
explanation/index
community/index
performance/index
```

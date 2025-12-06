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
- ✅ **Type-Safe**: Convert raw Bluetooth data to meaningful sensor values with comprehensive typing
- ✅ **Modern Python**: msgspec-based design with Python 3.9+ compatibility
- ✅ **Comprehensive**: Support for 70+ GATT characteristics across multiple service categories
- ✅ **Production Ready**: Extensive validation, perfect code quality scores, and comprehensive testing
- ✅ **Framework Agnostic**: Works with any BLE connection library (bleak, simplepyble, etc.)

## Quick Example

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
service_info = translator.get_sig_info_by_uuid("180F")  # Battery
char_info = translator.get_sig_info_by_uuid("2A19")  # Battery Level
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

Learn how to use the library
:::

:::{grid-item-card} 📚 API Reference
:link: api/index
:link-type: doc

Detailed API documentation
:::

::::

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

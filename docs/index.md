# Bluetooth SIG Standards Library

A pure Python library for Bluetooth SIG standards interpretation

[![Coverage Status](https://img.shields.io/endpoint?url=https://ronanb96.github.io/bluetooth-sig-python/coverage/coverage-badge.json)](coverage/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/bluetooth-sig.svg)](https://pypi.org/project/bluetooth-sig/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Welcome

The **Bluetooth SIG Standards Library** provides comprehensive GATT characteristic and service parsing with automatic UUID resolution. Built on the official Bluetooth SIG specifications, it offers a robust, standards-compliant architecture for Bluetooth device communication with type-safe data parsing and clean API design.

## Key Features

- ✅ **Standards-Based**: Official Bluetooth SIG YAML registry with automatic UUID resolution
- ✅ **Type-Safe**: Convert raw Bluetooth data to meaningful sensor values with comprehensive typing
- ✅ **Modern Python**: Dataclass-based design with Python 3.9+ compatibility
- ✅ **Comprehensive**: Support for 70+ GATT characteristics across multiple service categories
- ✅ **Production Ready**: Extensive validation, perfect code quality scores, and comprehensive testing
- ✅ **Framework Agnostic**: Works with any BLE connection library (bleak, simplepyble, etc.)

## Quick Example

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
service_info = translator.get_sig_info_by_uuid("180F")  # Battery
char_info = translator.get_sig_info_by_uuid("2A19")    # Battery Level
```

## Getting Started

<div class="grid cards" markdown>

- :material-clock-fast:{ .lg .middle } __Quick Start__

    ---

    Get up and running in minutes

    [:octicons-arrow-right-24: Quick Start](quickstart.md)

- :material-book-open-variant:{ .lg .middle } __Installation__

    ---

    Install via pip or from source

    [:octicons-arrow-right-24: Installation](installation.md)

- :material-code-braces:{ .lg .middle } __Usage Guide__

    ---

    Learn how to use the library

    [:octicons-arrow-right-24: Usage Guide](usage.md)

- :material-api:{ .lg .middle } __API Reference__

    ---

    Detailed API documentation

    [:octicons-arrow-right-24: API Reference](api/core.md)

</div>

## Why Choose This Library?

Unlike other Bluetooth libraries that focus on device connectivity, this library specializes in **standards interpretation**. It bridges the gap between raw BLE data and meaningful application-level information.

[Learn more about what this library solves →](why-use.md)

## Support

- **Issues**: [GitHub Issues](https://github.com/RonanB96/bluetooth-sig-python/issues)
- **Source Code**: [GitHub Repository](https://github.com/RonanB96/bluetooth-sig-python)
- **Documentation**: You're here! 🎉
- **Coverage Report**: [Test Coverage](coverage/) (Generated from CI)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/RonanB96/bluetooth-sig-python/blob/main/LICENSE) file for details.

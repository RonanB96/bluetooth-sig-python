# How-to Guides

Practical guides to solve specific problems and accomplish goals with the Bluetooth SIG Standards Library.

## Getting Started

- **[Import Patterns](import-patterns.md)** — Understanding the library's import structure and best practices
- **[Basic Usage](usage.md)** — Core workflows and common patterns
- **[BLE Integration](ble-integration.md)** — Integrate with bleak, simplepyble, and other BLE libraries
- **[Async Usage](async-usage.md)** — Use the library in asynchronous applications

## Core Features

- **[Characteristics](characteristics.md)** — Parse, encode, and work with GATT characteristics
- **[Services](services.md)** — Work with services, validation, health checking, and compliance
- **[Advertising Parsing](advertising-parsing.md)** — Parse BLE advertising packets and custom protocols

## Extending the Library

- **[Adding Characteristics](adding-characteristics.md)** — Add new SIG-defined characteristics
- **[Testing](testing.md)** — Test your BLE applications without hardware
- **[Contributing](contributing.md)** — Contribute code, docs, or bug reports

## Optimization

- **[Performance Tuning](performance-tuning.md)** — Profile and optimize parsing performance

## Migration

- **[Migration Guide](migration.md)** — Upgrade from older versions

## Related Sections

- **[Tutorials](../tutorials/index.md)** — Step-by-step learning for beginners
- **[API Reference](../api/index.md)** — Detailed API documentation
- **[Explanation](../explanation/index.md)** — Understand concepts and architecture

## Reference

- **[Supported Characteristics](../reference/characteristics.md)** — Complete list of implemented GATT characteristics
- **[Registry Coverage](../reference/registry-coverage.md)** — Bluetooth SIG registry implementation status

```{toctree}
:maxdepth: 1
:hidden:

import-patterns
usage
ble-integration
async-usage
characteristics
services
advertising-parsing
adding-characteristics
performance-tuning
testing
migration
contributing
../reference/characteristics
../reference/registry-coverage
```

# API Reference

Complete API documentation for the Bluetooth SIG Standards Library.

## Main Modules

::::{grid} 2
:gutter: 3

:::{grid-item-card} 🔄 Core
:link: reference/api/bluetooth_sig/core/index
:link-type: doc

Main translator and async context for parsing Bluetooth data
:::

:::{grid-item-card} 📡 GATT
:link: reference/api/bluetooth_sig/gatt/index
:link-type: doc

GATT services, characteristics, and descriptors
:::

:::{grid-item-card} 📱 Device
:link: reference/api/bluetooth_sig/device/index
:link-type: doc

Device representation and advertising data parsing
:::

:::{grid-item-card} 🗄️ Registry
:link: reference/api/bluetooth_sig/registry/index
:link-type: doc

UUID registries and SIG standards database
:::

:::{grid-item-card} 🏷️ Types
:link: reference/api/bluetooth_sig/types/index
:link-type: doc

Type definitions and data structures
:::

::::

## Quick Navigation

- **BluetoothSIGTranslator** - Main entry point for parsing
- **CharacteristicRegistry** - Characteristic lookup
- **BaseCharacteristic** - Base class for all characteristics
- **CharacteristicData** - Parsed characteristic data

## Core Modules

- [bluetooth_sig](reference/api/bluetooth_sig/index) - Package root with main exports
- [bluetooth_sig.core](reference/api/bluetooth_sig/core/index) - Core translator and async parsing
- [bluetooth_sig.gatt](reference/api/bluetooth_sig/gatt/index) - GATT layer (services, characteristics, descriptors)
- [bluetooth_sig.device](reference/api/bluetooth_sig/device/index) - Device representation and advertising
- [bluetooth_sig.registry](reference/api/bluetooth_sig/registry/index) - UUID registries from Bluetooth SIG specs
- [bluetooth_sig.types](reference/api/bluetooth_sig/types/index) - Type definitions and data structures

### Key Submodules

- [bluetooth_sig.gatt.characteristics](reference/api/bluetooth_sig/gatt/characteristics/index) - SIG characteristic implementations
- [bluetooth_sig.gatt.services](reference/api/bluetooth_sig/gatt/services/index) - GATT service definitions

```{toctree}
:maxdepth: 1
:hidden:

characteristics
performance-data
benchmarks
```

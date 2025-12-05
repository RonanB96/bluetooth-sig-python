# API Reference

Complete API documentation for the Bluetooth SIG Standards Library.

## Main Modules

<div class="grid cards" markdown>

-   :material-translate: **Core**

    ---

    Main translator and async context for parsing Bluetooth data

    [:octicons-arrow-right-24: Explore Core](bluetooth_sig/core/index.md)

-   :material-bluetooth: **GATT**

    ---

    GATT services, characteristics, and descriptors

    [:octicons-arrow-right-24: Explore GATT](bluetooth_sig/gatt/index.md)

-   :material-devices: **Device**

    ---

    Device representation and advertising data parsing

    [:octicons-arrow-right-24: Explore Device](bluetooth_sig/device/index.md)

-   :material-database: **Registry**

    ---

    UUID registries and SIG standards database

    [:octicons-arrow-right-24: Explore Registry](bluetooth_sig/registry/index.md)

-   :material-code-braces: **Types**

    ---

    Type definitions and data structures

    [:octicons-arrow-right-24: Explore Types](bluetooth_sig/types/index.md)

</div>

## Quick Navigation

- [BluetoothSIGTranslator][bluetooth_sig.core.translator.BluetoothSIGTranslator] - Main entry point for parsing
- [CharacteristicRegistry][bluetooth_sig.gatt.characteristics.registry.CharacteristicRegistry] - Characteristic lookup
- [BaseCharacteristic][bluetooth_sig.gatt.characteristics.base.BaseCharacteristic] - Base class for all characteristics
- [CharacteristicData][bluetooth_sig.gatt.characteristics.base.CharacteristicData] - Parsed characteristic data

## Click any module below to see its complete API documentation:

Click any module below to see its complete API documentation:

### Core Modules

- [bluetooth_sig](bluetooth_sig/index.md) - Package root with main exports
- [bluetooth_sig.core](bluetooth_sig/core/index.md) - Core translator and async parsing
- [bluetooth_sig.gatt](bluetooth_sig/gatt/index.md) - GATT layer (services, characteristics, descriptors)
- [bluetooth_sig.device](bluetooth_sig/device/index.md) - Device representation and advertising
- [bluetooth_sig.registry](bluetooth_sig/registry/index.md) - UUID registries from Bluetooth SIG specs
- [bluetooth_sig.types](bluetooth_sig/types/index.md) - Type definitions and data structures

### Key Submodules

- [bluetooth_sig.gatt.characteristics](bluetooth_sig/gatt/characteristics/index.md) - SIG characteristic implementations
- [bluetooth_sig.gatt.services](bluetooth_sig/gatt/services/index.md) - GATT service definitions
- [bluetooth_sig.registry.uuids](bluetooth_sig/registry/uuids/index.md) - UUID registries (services, characteristics, etc.)

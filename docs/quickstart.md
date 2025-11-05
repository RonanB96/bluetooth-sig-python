# Quick Start

Get started with the Bluetooth SIG Standards Library in 5 minutes.

## Prerequisites

Before using the library, make sure it's installed:

```bash
pip install bluetooth-sig
```

For detailed installation instructions, see the [Installation Guide](installation.md).

## Basic Usage

### 1. Import the Library

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
```

### 2. Resolve UUIDs

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Get service information
service_info = translator.get_sig_info_by_uuid("180F")
print(f"Service: {service_info.name}")  # "Battery Service"

# Get characteristic information
char_info = translator.get_sig_info_by_uuid("2A19")
print(f"Characteristic: {char_info.name}")  # "Battery Level"
print(f"Unit: {char_info.unit}")  # "percentage"
```

### 3. Parse Characteristic Data

The [parse_characteristic][bluetooth_sig.BluetoothSIGTranslator.parse_characteristic] method returns a [CharacteristicData][bluetooth_sig.types.CharacteristicData] object with parsed values:

```python
# Parse battery level (0-100%)
battery_data = translator.parse_characteristic("2A19", bytearray([85]))
print(f"Battery: {battery_data.value}%")  # Battery: 85%

# Parse temperature (°C)
temp_data = translator.parse_characteristic("2A6E", bytearray([0x64, 0x09]))
print(f"Temperature: {temp_data.value}°C")  # Temperature: 24.36°C

# Parse humidity (%)
humidity_data = translator.parse_characteristic("2A6F", bytearray([0x3A, 0x13]))
print(f"Humidity: {humidity_data.value}%")  # Humidity: 49.42%
```

The [parse_characteristic][bluetooth_sig.BluetoothSIGTranslator.parse_characteristic] method returns a [CharacteristicData][bluetooth_sig.types.CharacteristicData] object containing:

- `value` - The parsed, human-readable value
- `info` - [CharacteristicInfo][bluetooth_sig.types.CharacteristicInfo] with UUID, name, unit, and properties
- `raw_data` - Original bytearray
- `parse_success` - Boolean indicating successful parsing
- `error_message` - Error details if parsing failed

## Working with Types

### CharacteristicData Result Object

Every call to [parse_characteristic][bluetooth_sig.BluetoothSIGTranslator.parse_characteristic] returns a [CharacteristicData][bluetooth_sig.types.CharacteristicData] object:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
result = translator.parse_characteristic("2A19", bytearray([85]))

# Access parsed value
print(result.value)          # 85

# Access metadata via CharacteristicInfo
print(result.info.name)      # "Battery Level"
print(result.info.unit)      # "%"
print(result.info.uuid)      # "00002a19-0000-1000-8000-00805f9b34fb"

# Access raw data and status
print(result.raw_data)       # bytearray([85])
print(result.parse_success)  # True
print(result.error_message)  # None
```

See the [CharacteristicData][bluetooth_sig.types.CharacteristicData] API reference for complete details.

### Using Enums for Type Safety

For type-safe UUID references, use the built-in enums:

```python
from bluetooth_sig.types.gatt_enums import CharacteristicName, ServiceName

# Characteristic enums
CharacteristicName.BATTERY_LEVEL  # "Battery Level"
CharacteristicName.TEMPERATURE    # "Temperature"
CharacteristicName.HUMIDITY       # "Humidity"

# Service enums
ServiceName.BATTERY_SERVICE           # "Battery Service"
ServiceName.ENVIRONMENTAL_SENSING     # "Environmental Sensing"
ServiceName.DEVICE_INFORMATION        # "Device Information"
```

These enums provide autocomplete and prevent typos when resolving by name.

### Error Handling with ValidationResult

When validation fails, check the [ValidationResult][bluetooth_sig.types.ValidationResult]:

```python
result = translator.parse_characteristic("2A19", bytearray([200]))  # Invalid: >100%

if not result.parse_success:
    print(f"Error: {result.error_message}")
    # Error: Value 200 exceeds maximum 100 for Battery Level
```

See the [ValidationResult][bluetooth_sig.types.ValidationResult] API reference for all validation fields.

## Complete Example

Here's a complete working example:

```python
from bluetooth_sig import BluetoothSIGTranslator

def main():
    # Create translator
    translator = BluetoothSIGTranslator()

    # UUID Resolution
    print("=== UUID Resolution ===")
    service_info = translator.get_sig_info_by_uuid("180F")
    print(f"UUID 180F: {service_info.name}")

    # Name Resolution
    print("\n=== Name Resolution ===")
    battery_level = translator.get_sig_info_by_name("Battery Level")
    print(f"Battery Level: {battery_level.uuid}")

    # Data Parsing
    print("\n=== Data Parsing ===")


    # Battery level
    battery_data = translator.parse_characteristic("2A19", bytearray([75]))
    print(f"Battery: {battery_data.value}%")

    # Temperature
    temp_data = translator.parse_characteristic("2A6E", bytearray([0x64, 0x09]))
    print(f"Temperature: {temp_data.value}°C")

    # Humidity
    humidity_data = translator.parse_characteristic("2A6F", bytearray([0x3A, 0x13]))
    print(f"Humidity: {humidity_data.value}%")


if __name__ == '__main__':
    main()

```

**Output:**

```text
=== UUID Resolution ===
UUID 180F: Battery Service (service)

=== Name Resolution ===
Battery Level: 2A19

=== Data Parsing ===
Battery: 75%
Temperature: 24.36°C
Humidity: 49.42%
```

## Integration with BLE Libraries

The library is designed to work with any BLE connection library. See the [BLE Integration Guide](guides/ble-integration.md) for detailed examples with bleak, simplepyble, and other libraries.

For step-by-step adoption from existing code (before/after examples), see the [Migration Guide](guides/migration.md). It also references example connection managers and adapters you can copy and update as needed.

## Common Use Cases

For examples of reading multiple sensors and advanced usage patterns, see the [Usage Guide](usage.md).

### Error Handling

For comprehensive error handling examples and troubleshooting, see the [Usage Guide](usage.md) and [Testing Guide](testing.md).

## Supported Characteristics

The library supports 70+ GATT characteristics across multiple categories:

- **Battery Service**: Battery Level, Battery Power State
- **Environmental Sensing**: Temperature, Humidity, Pressure, Air Quality
- **Health Monitoring**: Heart Rate, Blood Pressure, Glucose
- **Fitness Tracking**: Running/Cycling Speed, Cadence, Power
- **Device Information**: Manufacturer, Model, Firmware Version
- And many more...

See the [Usage Guide](usage.md) for a complete list.

## Next Steps

- [Usage Guide](usage.md) - Comprehensive usage examples
- [BLE Integration Guide](guides/ble-integration.md) - Integrate with your BLE library
- [API Reference](api/core.md) - Complete API documentation
- [What Problems It Solves](what-it-solves.md) - Understand the benefits

## Getting Help

- **Documentation**: You're reading it! 📚
- **Examples**: Check the [examples/](https://github.com/RonanB96/bluetooth-sig-python/tree/main/examples) directory
- **Issues**: [GitHub Issues](https://github.com/RonanB96/bluetooth-sig-python/issues)
- **Source**: [GitHub Repository](https://github.com/RonanB96/bluetooth-sig-python)

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

### 2. Look Up SIG Standards by Name

**You don't need to memorize UUIDs!** Use human-readable names to look up official Bluetooth SIG standards:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Look up by name (recommended - no UUIDs to remember!)
service_info = translator.get_sig_info_by_name("Battery Service")
print(f"Service: {service_info.name}")  # "Battery Service"
print(f"UUID: {service_info.uuid}")  # "180F"

char_info = translator.get_sig_info_by_name("Battery Level")
print(f"Characteristic: {char_info.name}")  # "Battery Level"
print(f"UUID: {char_info.uuid}")  # "2A19"
print(f"Unit: {char_info.unit}")  # "%"

# Or look up by UUID (if you already have it from your BLE library)
char_from_uuid = translator.get_sig_info_by_uuid("2A19")
print(f"Name: {char_from_uuid.name}")  # "Battery Level"
```

### 3. Parse Characteristic Data Automatically

**The library automatically recognizes and parses standard Bluetooth SIG characteristics** - just pass the UUID and raw data:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
# These are example values for demonstration purposes.
# In a real application, you would get these from your BLE library (bleak, simplepyble, etc.)
SIMULATED_BATTERY_DATA = bytearray([85])  # Simulates 85% battery level
SIMULATED_TEMP_DATA = bytearray([0x64, 0x09])  # Simulates 24.04°C temperature
SIMULATED_HUMIDITY_DATA = bytearray([0x3A, 0x13])  # Simulates 49.22% humidity

# Get UUID from your BLE library (bleak, simplepyble, etc.)
# The translator automatically recognizes standard SIG UUIDs and parses accordingly
# If you know what you're looking for, you can use CharacteristicName enum

# Parse battery level using UUID from BLE library
battery_data = translator.parse_characteristic("2A19", SIMULATED_BATTERY_DATA)
print(
    f"What is this? {battery_data.info.name}"
)  # "Battery Level" - auto-recognized!
print(f"Battery: {battery_data.value}%")  # Battery: 85%

# Parse temperature - library knows the encoding (sint16, 0.01°C)
temp_data = translator.parse_characteristic("2A6E", SIMULATED_TEMP_DATA)
print(
    f"What is this? {temp_data.info.name}"
)  # "Temperature" - auto-recognized!
print(f"Temperature: {temp_data.value}°C")  # Temperature: 24.04°C

# Parse humidity - library knows the format (uint16, 0.01%)
humidity_data = translator.parse_characteristic(
    "2A6F", SIMULATED_HUMIDITY_DATA
)
print(
    f"What is this? {humidity_data.info.name}"
)  # "Humidity" - auto-recognized!
print(f"Humidity: {humidity_data.value}%")  # Humidity: 49.22%

# Alternative: If you know the characteristic name, convert enum to UUID first
from bluetooth_sig.types.gatt_enums import CharacteristicName

battery_uuid = translator.get_characteristic_uuid_by_name(
    CharacteristicName.BATTERY_LEVEL
)
if battery_uuid:
    result = translator.parse_characteristic(
        str(battery_uuid), SIMULATED_BATTERY_DATA
    )
    print(f"Using enum: {result.value}%")  # Using enum: 85%
```

**Key point**: You get UUIDs from your BLE connection library, then this library automatically identifies what they are and parses the data correctly.

The {py:meth}`~bluetooth_sig.BluetoothSIGTranslator.parse_characteristic` method returns a {py:class}`~bluetooth_sig.gatt.characteristics.base.CharacteristicData` object containing:

- `value` - The parsed, human-readable value
- `info` - {py:class}`~bluetooth_sig.types.CharacteristicInfo` with UUID, name, unit, and properties
- `raw_data` - Original bytearray
- `parse_success` - Boolean indicating successful parsing
- `error_message` - Error details if parsing failed (empty string if successful)

## Working with Types

### CharacteristicData Result Object

Every call to {py:class}`~bluetooth_sig.BluetoothSIGTranslator.parse_characteristic` returns a {py:class}`~bluetooth_sig.gatt.characteristics.base.CharacteristicData` object:

```python
from bluetooth_sig import BluetoothSIGTranslator

# ============================================
# SIMULATED DATA - Replace with actual BLE read
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])  # Simulates 85% battery level

translator = BluetoothSIGTranslator()
# Use UUID string from your BLE library
result = translator.parse_characteristic("2A19", SIMULATED_BATTERY_DATA)

# Access parsed value
print(result.value)  # 85

# Access metadata via CharacteristicInfo
print(result.info.name)  # "Battery Level"
print(result.info.unit)  # "%"
print(result.info.uuid)  # "00002a19-0000-1000-8000-00805f9b34fb"

# Access raw data and status
print(result.raw_data)  # bytearray([85])
print(result.parse_success)  # True
print(result.error_message)  # "" (empty string when successful)
```

See the {py:class}`~bluetooth_sig.gatt.characteristics.base.CharacteristicData` API reference for complete details.

### Using Enums for Type Safety

For type-safe UUID references, use the built-in enums:

```python
from bluetooth_sig.types.gatt_enums import CharacteristicName, ServiceName

# Characteristic enums
CharacteristicName.BATTERY_LEVEL  # "Battery Level"
CharacteristicName.TEMPERATURE  # "Temperature"
CharacteristicName.HUMIDITY  # "Humidity"

# Service enums
ServiceName.BATTERY  # "Battery"
ServiceName.ENVIRONMENTAL_SENSING  # "Environmental Sensing"
ServiceName.DEVICE_INFORMATION  # "Device Information"
```

These enums provide autocomplete and prevent typos when resolving by name.

### Error Handling with ValidationResult

When validation fails, check the {py:class}`~bluetooth_sig.types.ValidationResult`:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
result = translator.parse_characteristic(
    "2A19", bytearray([200])
)  # Invalid: >100%

if not result.parse_success:
    print(f"Error: {result.error_message}")
    # Error: Value 200 exceeds maximum 100 for Battery Level
```

See the {py:class}`~bluetooth_sig.types.ValidationResult` API reference for all validation fields.

## Integration with BLE Libraries

The library is designed to work with any BLE connection library. See the [BLE Integration Guide](../how-to/ble-integration.md) for detailed examples with bleak, simplepyble, and other libraries.

For step-by-step adoption from existing code (before/after examples), see the [Migration Guide](../how-to/migration.md). It also references example connection managers and adapters you can copy and update as needed.

## Common Use Cases

For examples of reading multiple sensors and advanced usage patterns, see the [Usage Guide](../how-to/usage.md).

### Error Handling

For comprehensive error handling examples and troubleshooting, see the [Usage Guide](../how-to/usage.md) and [Testing Guide](../how-to/testing.md).

## Supported Characteristics

The library supports 70+ GATT characteristics across multiple categories:

- **Battery Service**: Battery Level, Battery Power State
- **Environmental Sensing**: Temperature, Humidity, Pressure, Air Quality
- **Health Monitoring**: Heart Rate, Blood Pressure, Glucose
- **Fitness Tracking**: Running/Cycling Speed, Cadence, Power
- **Device Information**: Manufacturer, Model, Firmware Version
- And many more...

See the [Usage Guide](../how-to/usage.md) for a complete list.

## Next Steps

- [Usage Guide](../how-to/usage.md) - Comprehensive usage examples
- [BLE Integration Guide](../how-to/ble-integration.md) - Integrate with your BLE library
- [API Reference](../api/index.md) - Complete API documentation
- [What Problems It Solves](../explanation/what-it-solves.md) - Understand the benefits

## Getting Help

- **Documentation**: You're reading it! 📚
- **Examples**: Check the [examples/](https://github.com/RonanB96/bluetooth-sig-python/tree/main/examples) directory
- **Issues**: [GitHub Issues](https://github.com/RonanB96/bluetooth-sig-python/issues)
- **Source**: [GitHub Repository](https://github.com/RonanB96/bluetooth-sig-python)

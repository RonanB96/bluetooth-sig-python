# Quick Start

Get started with the Bluetooth SIG Standards Library in 5 minutes.

## Prerequisites

Before using the library, make sure it's installed:

```bash
pip install bluetooth-sig
```

For detailed installation instructions, see the [Installation Guide](installation.md).

## Choose Your Approach

See [API Overview](../explanation/api-overview.md) for guidance on choosing between the APIs like characteristic classes, the translator, and the Device abstraction etc.

## Type-Safe Parsing

When you know the characteristic type, use the class directly for full type inference:

```python
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HeartRateMeasurementCharacteristic,
    TemperatureCharacteristic,
)

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])  # 85% battery
SIMULATED_HR_DATA = bytearray([0x00, 72])  # 72 bpm
SIMULATED_TEMP_DATA = bytearray([0x64, 0x09])  # 24.04°C

# Simple: IDE infers return type as int
battery = BatteryLevelCharacteristic()
level = battery.parse_value(SIMULATED_BATTERY_DATA)
print(f"Battery: {level}%")  # Battery: 85%

# Encode value back to bytes
encoded = battery.build_value(85)
print(f"Encoded: {encoded.hex()}")  # Encoded: 55

# Complex: IDE infers HeartRateData with full autocomplete
heart_rate = HeartRateMeasurementCharacteristic()
hr_data = heart_rate.parse_value(SIMULATED_HR_DATA)
print(f"Heart rate: {hr_data.heart_rate} bpm")  # Heart rate: 72 bpm
print(f"Sensor contact: {hr_data.sensor_contact}")  # Autocompletion works!

# Temperature: returns float with proper scaling
temp = TemperatureCharacteristic()
temp_value = temp.parse_value(SIMULATED_TEMP_DATA)
print(f"Temperature: {temp_value}°C")  # Temperature: 24.04°C
```

**Why use characteristic classes?**

- IDE automatically infers return types—no manual type hints needed
- Autocompletion shows available fields on parsed data
- Type errors caught at compile time
- Direct access to values without wrapper objects

## Dynamic Parsing (Device Scanning)

For unknown characteristics discovered at runtime, use the :class:`~bluetooth_sig.BluetoothSIGTranslator` with UUID strings:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])

# Parse using UUID string - returns the parsed value directly
result = translator.parse_characteristic("2A19", SIMULATED_BATTERY_DATA)
info = translator.get_characteristic_info_by_uuid("2A19")
print(f"Identified as: {info.name}")  # Battery Level
print(f"Value: {result}%")  # 85%

# Check which discovered UUIDs are supported SIG characteristics
discovered_uuids = ["2A19", "2A6E", "2A37"]  # From your BLE library
for uuid in discovered_uuids:
    if translator.supports(uuid):
        char_info = translator.get_characteristic_info_by_uuid(uuid)
        print(f"Found: {char_info.name} ({uuid})")
```

**Note:** The `parse_characteristic` method returns the parsed value directly (not a wrapper object). Use `get_characteristic_info_by_uuid()` to get metadata like characteristic name and unit.

## Look Up SIG Standards by Name

Use human-readable names or enums to look up official Bluetooth SIG standards:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName, ServiceName

translator = BluetoothSIGTranslator()

# Look up by enum (recommended - autocomplete and typo prevention)
char_info = translator.get_sig_info_by_name(
    CharacteristicName.BATTERY_LEVEL.value
)
print(f"Characteristic: {char_info.name}")  # "Battery Level"
print(f"UUID: {char_info.uuid}")  # "00002A19-0000-1000-8000-00805F9B34FB"

service_info = translator.get_sig_info_by_name(ServiceName.BATTERY.value)
print(f"Service: {service_info.name}")  # "Battery"
print(f"UUID: {service_info.uuid}")  # "0000180F-0000-1000-8000-00805F9B34FB"
```

## Using Enums for Type Safety

The library provides enums for all SIG-defined characteristics and services:

```python
from bluetooth_sig.types.gatt_enums import CharacteristicName, ServiceName

# Characteristic enums
CharacteristicName.BATTERY_LEVEL  # "Battery Level"
CharacteristicName.TEMPERATURE  # "Temperature"
CharacteristicName.HEART_RATE_MEASUREMENT  # "Heart Rate Measurement"

# Service enums
ServiceName.BATTERY  # "Battery"
ServiceName.ENVIRONMENTAL_SENSING  # "Environmental Sensing"
ServiceName.DEVICE_INFORMATION  # "Device Information"
```

## Error Handling

When validation fails, check the :class:`~bluetooth_sig.types.ValidationResult`:

```python
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
from bluetooth_sig.gatt.exceptions import CharacteristicParseError

battery = BatteryLevelCharacteristic()

# Invalid data: battery level cannot exceed 100%
try:
    level = battery.parse_value(bytearray([200]))
except CharacteristicParseError as e:
    print(f"Validation error: {e}")
    # Validation error: Invalid percentage: 200 (expected range [0, 100])
```

For permissive parsing (e.g., debugging non-compliant devices), disable validation:

```python
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

battery = BatteryLevelCharacteristic()
level = battery.parse_value(bytearray([200]), validate=False)  # Returns 200
```

## BLE Library Integration

The library works with any BLE connection library. See the [BLE Integration Guide](../how-to/ble-integration.md) for detailed examples with bleak, simplepyble, and other libraries.

## Supported Characteristics

The library supports 200+ GATT characteristics across multiple categories:

- **Battery Service**: Battery Level, Battery Power State
- **Environmental Sensing**: Temperature, Humidity, Pressure, Air Quality
- **Health Monitoring**: Heart Rate, Blood Pressure, Glucose
- **Fitness Tracking**: Running/Cycling Speed, Cadence, Power
- **Device Information**: Manufacturer, Model, Firmware Version
- And many more...

See the [Supported Characteristics](../reference/characteristics.md) for a complete list.

## Next Steps

- [Usage Guide](../how-to/usage.md) - Real-world usage patterns and batch parsing
- [BLE Integration Guide](../how-to/ble-integration.md) - Integrate with your BLE library
- [API Reference](../api/index.md) - Complete API documentation

## Getting Help

- **Documentation**: You're reading it! 📚
- **Examples**: Check the [examples/](https://github.com/RonanB96/bluetooth-sig-python/tree/main/examples) directory
- **Issues**: [GitHub Issues](https://github.com/RonanB96/bluetooth-sig-python/issues)
- **Source**: [GitHub Repository](https://github.com/RonanB96/bluetooth-sig-python)

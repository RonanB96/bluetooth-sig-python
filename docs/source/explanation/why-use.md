# Why Use This Library?

## The Problem with Raw BLE Data

When working with Bluetooth Low Energy (BLE) devices, you typically encounter raw binary data that needs to be interpreted according to Bluetooth SIG specifications. This creates several challenges:

### Challenge 1: Complex Data Formats

```python
# ============================================
# SIMULATED DATA - Example raw bytes
# ============================================
raw_data = bytearray([0x64, 0x09])  # What does this mean? 🤔
```

Without proper interpretation, this is just bytes. According to Bluetooth SIG specifications for the Temperature characteristic (0x2A6E), this represents **24.04°C** (2404 * 0.01).

### Challenge 2: UUID Management

```python
# UUIDs are cryptic
uuid = "0000180f-0000-1000-8000-00805f9b34fb"  # What service is this?
```

These 128-bit UUIDs need to be mapped to human-readable names like "Battery Service" based on the official Bluetooth SIG registry.

### Challenge 3: Standards Compliance

Each characteristic has specific parsing rules:

- Different byte orders (little-endian vs big-endian)
- Varying data types (uint8, sint16, SFLOAT, etc.)
- Special sentinel values (0xFFFF meaning "unknown")
- Conditional fields based on flags
- Unit conversions and scaling factors

## The Solution: bluetooth-sig

This library handles all the complexity for you:

### ✅ UUID Resolution

```python
# ============================================
# EXAMPLE UUIDs - From your BLE library
# ============================================
BATTERY_SERVICE_UUID = "180F"  # UUID from BLE device discovery

# Resolve UUIDs to names
service_info = translator.get_sig_info_by_uuid(BATTERY_SERVICE_UUID)
print(service_info.name)  # "Battery Service"

# Reverse lookup
battery_service = translator.get_sig_info_by_name("Battery Service")
print(battery_service.uuid)  # "180F"
```

### ✅ Type-Safe Data Structures

```python
# ============================================
# SIMULATED DATA - Replace with actual BLE read
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])  # Simulates 85% battery
BATTERY_LEVEL_UUID = "2A19"  # UUID from your BLE library

# Get structured data, not raw bytes
battery_data = translator.parse_characteristic(
    BATTERY_LEVEL_UUID, SIMULATED_BATTERY_DATA
)

# battery_data is a typed msgspec struct with validation
assert battery_data.value == 85
assert 0 <= battery_data.value <= 100  # Automatically validated
```

### ✅ Complete Parsing Example

```python
# ============================================
# COMPLETE EXAMPLE - From BLE device to parsed data
# ============================================
from bluetooth_sig import BluetoothSIGTranslator

# Initialize the translator (loads all SIG definitions)
translator = BluetoothSIGTranslator()

# Example: Reading temperature from a BLE environmental sensor
TEMPERATURE_UUID = "2A6E"  # Official SIG UUID for Temperature
SERVICE_UUID = "181A"  # Environmental Sensing Service

# Step 1: Connect to device (using your BLE library)
# raw_bytes = await your_ble_client.read_gatt_char(TEMPERATURE_UUID)

# Step 2: Simulate real BLE data for this example
raw_temperature_bytes = bytearray(
    [0x0A, 0x01]
)  # 266 = 0x010A in little-endian

# Step 3: Parse with bluetooth-sig (handles all complexity)
temperature_data = translator.parse_characteristic(
    TEMPERATURE_UUID, raw_temperature_bytes
)

# Result: Fully typed, validated data structure
print(f"Temperature: {temperature_data.value}°C")  # "Temperature: 26.6°C"
print(f"Units: {temperature_data.unit}")  # "Units: celsius"
```

## When Should You Use This Library?

### ✅ Perfect For

- **Application Developers**: Building apps that need to display BLE sensor data
- **IoT Projects**: Reading data from Bluetooth sensors and devices
- **Testing & Validation**: Verifying BLE device implementations
- **Protocol Implementation**: Building BLE client applications
- **Research & Analysis**: Analysing BLE device behaviour
- **Custom Protocols**: Supports custom GATT characteristics via extension API

### ❌ Not Designed For

- **BLE Connection Management**: Use `bleak`, `simplepyble`, or similar libraries for actual device connections
- **Firmware Development**: This is a client-side library, not for embedded devices
- **Real-time Streaming**: Optimized for parsing, not high-frequency streaming

## Key Differentiators

### 1. Standards-First Approach

Built directly from official Bluetooth SIG specifications. Every characteristic parser is validated against the official documentation.

### 2. Framework Agnostic

Works with **any** BLE connection library:

```python
# SKIP: Example requires BLE hardware access and external libraries
# ============================================
# EXAMPLE UUIDs - From your BLE library
# ============================================
CHAR_UUID = "2A19"  # Characteristic UUID from device discovery
SERVICE_UUID = "180F"  # Service UUID from device discovery

# Works with bleak
from bleak import BleakClient

raw_data = await client.read_gatt_char(CHAR_UUID)
parsed = translator.parse_characteristic(CHAR_UUID, raw_data)

# Works with simplepyble
from simplepyble import Peripheral

raw_data = peripheral.read(SERVICE_UUID, CHAR_UUID)
parsed = translator.parse_characteristic(CHAR_UUID, raw_data)

# Works with ANY BLE library
```

### 3. Type Safety & Validation

```python
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

char = BatteryLevelCharacteristic()

# Automatic validation
try:
    char.decode_value(bytearray([150]))  # Invalid: > 100
except Exception as e:
    print(e)  # "Invalid percentage: 150 (expected range [0, 100])"
```

### 4. Comprehensive Coverage

Support for 70+ characteristics across multiple service categories:

- Battery Service
- Environmental Sensing (temperature, humidity, pressure, air quality)
- Health Monitoring (heart rate, blood pressure, glucose)
- Fitness Tracking (running, cycling speed/cadence/power)
- Device Information
- And many more...

## Comparison with DIY Parsing

| Feature | bluetooth-sig | DIY Manual Parsing |
|---------|--------------|---------------------|
| Standards Compliance | ✅ Official specs | ❌ Manual implementation |
| Type Safety | ✅ Full typing | ❌ Raw bytes |
| UUID Resolution | ✅ Automatic | ❌ Manual mapping |
| BLE Library Support | ✅ Any library | ✅ Any library |
| Validation | ✅ Built-in | ❌ Manual |
| Maintenance | ✅ SIG registry updates | ❌ You maintain |
| Custom Characteristics | ✅ Extension API | ✅ You implement everything |

## Real-World Example

### Without bluetooth-sig

```python
# Manual parsing (error-prone)
def parse_battery_level(data: bytes) -> int:
    if len(data) != 1:
        raise ValueError("Invalid length")
    value = data[0]
    if value > 100:
        raise ValueError("Invalid range")
    return value


# Manual UUID mapping
UUID_MAP = {
    "2A19": "Battery Level",
    "180F": "Battery Service",
    # ... hundreds more
}
```

### With bluetooth-sig

```python
from bluetooth_sig import BluetoothSIGTranslator

# ============================================
# SIMULATED DATA - Replace with actual BLE read
# ============================================
BATTERY_LEVEL_UUID = "2A19"  # UUID from your BLE library
data = bytearray([85])  # Simulated battery data

translator = BluetoothSIGTranslator()

# One line, standards-compliant, type-safe
result = translator.parse_characteristic(BATTERY_LEVEL_UUID, data)
```

## Next Steps

- [Quick Start Guide](../tutorials/quickstart.md) - Get started in 5 minutes
- [What Problems It Solves](what-it-solves.md) - Detailed problem/solution analysis
- [Limitations](limitations.md) - Understand the boundaries
- [Usage Guide](../how-to/usage.md) - Comprehensive usage examples

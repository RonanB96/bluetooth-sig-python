# Usage

This guide covers real-world usage patterns for the Bluetooth SIG Standards Library.

**Key Principle**: You don't need to memorize Bluetooth UUIDs! When scanning unknown devices, this library automatically recognizes standard SIG characteristics and tells you what they are. When working with known devices, use characteristic classes directly for full type safety.

## Which API Should I Use?

See [API Overview](../explanation/api-overview.md) for guidance on choosing between the APIs like characteristic classes, the translator, and the Device abstraction etc.

## Device Abstraction

The `Device` class provides the highest-level API with automatic dependency resolution and caching. It requires a connection manager that implements `ConnectionManagerProtocol`.

```python
# SKIP: Requires BLE hardware and ConnectionManagerProtocol implementation
from bluetooth_sig import BluetoothSIGTranslator, Device
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HeartRateMeasurementCharacteristic,
)

# connection_manager implements ConnectionManagerProtocol
# See BLE Integration Guide for backend-specific examples
device = Device(connection_manager, BluetoothSIGTranslator())

await device.connect()

# Type-safe: IDE knows battery is int
battery = await device.read(BatteryLevelCharacteristic)
print(f"Battery: {battery}%")

# Complex type: IDE knows hr_data is HeartRateData
hr_data = await device.read(HeartRateMeasurementCharacteristic)
print(f"Heart Rate: {hr_data.heart_rate} bpm")

# Dynamic: returns Any (for scanning/discovery)
unknown_value = await device.read("2A6E")  # Temperature UUID
```

For connection manager setup, see the [BLE Integration Guide](ble-integration.md).

## Type-Safe Parsing (Direct Classes)

When you know the characteristic type, use classes directly for full IDE inference:

```python
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HeartRateMeasurementCharacteristic,
    TemperatureCharacteristic,
)

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])
SIMULATED_HR_DATA = bytearray([0x00, 72])

# Simple characteristic: IDE infers int
battery = BatteryLevelCharacteristic()
level = battery.parse_value(SIMULATED_BATTERY_DATA)  # level: int
print(f"Battery: {level}%")  # Battery: 85%

# Encode back to bytes
encoded = battery.build_value(85)
print(f"Encoded: {encoded.hex()}")  # Encoded: 55

# Complex characteristic: IDE infers HeartRateData
heart_rate = HeartRateMeasurementCharacteristic()
hr_data = heart_rate.parse_value(SIMULATED_HR_DATA)  # hr_data: HeartRateData
print(f"Heart rate: {hr_data.heart_rate} bpm")
print(f"Sensor contact: {hr_data.sensor_contact}")

# Encode structured data
encoded_hr = heart_rate.build_value(hr_data)
```

**Benefits:**

- IDE autocomplete on all parsed fields
- Type errors caught at compile time
- No wrapper objects—direct access to values

## Dynamic Parsing (Device Scanning)

For scanning unknown devices, use UUID strings. The return type is `Any`:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
SIMULATED_HEART_RATE_DATA = bytearray([72])
UNKNOWN_UUID = "2A37"  # UUID from device discovery

# Parse: translator identifies and parses automatically
value = translator.parse_characteristic(
    UNKNOWN_UUID, SIMULATED_HEART_RATE_DATA
)

# value is the parsed result directly (type is Any at runtime)
info = translator.get_characteristic_info_by_uuid(UNKNOWN_UUID)
print(f"Identified as: {info.name}")  # "Heart Rate Measurement"
print(f"Value: {value}")  # HeartRateData(heart_rate=72, ...)

# Useful pattern: loop through discovered characteristics
# In real usage, each UUID would have its own data from BLE reads
discovered_uuids = ["2A19", "2A6E", "2A37"]
simulated_data = {
    "2A19": bytearray([85]),  # Battery Level: 85%
    "2A6E": bytearray([0xDC, 0x09]),  # Temperature: 25.24°C
    "2A37": bytearray([0x00, 72]),  # Heart Rate: 72 bpm
}
for uuid in discovered_uuids:
    if translator.supports(uuid):
        raw_data = simulated_data[uuid]
        parsed_value = translator.parse_characteristic(uuid, raw_data)
        char_info = translator.get_characteristic_info_by_uuid(uuid)
        print(f"{char_info.name}: {parsed_value}")
```

## UUID Format Handling

BLE libraries output UUIDs in different formats, but bluetooth-sig handles them all:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

# ============================================
# SIMULATED DATA - Replace with actual BLE read
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])  # Simulates 85% battery level

translator = BluetoothSIGTranslator()

found_uuid = translator.get_characteristic_uuid_by_name(
    CharacteristicName.BATTERY_LEVEL
)
# These all work - the library normalizes them internally
formats = [
    str(found_uuid),  # uuid found from Enum name
    "0x2A19",  # Hex prefix
    "00002a19-0000-1000-8000-00805f9b34fb",  # Full 128-bit (what bleak gives you)
    "00002A19-0000-1000-8000-00805F9B34FB",  # Uppercase variant
]

for uuid_format in formats:
    result = translator.parse_characteristic(
        str(uuid_format), SIMULATED_BATTERY_DATA
    )
    info = translator.get_characteristic_info_by_uuid(uuid_format)
    print(f"{uuid_format:45} → {info.name}")

# Output:
# 00002A19-0000-1000-8000-00805F9B34FB         → Battery Level
# 0x2A19                                       → Battery Level
# 00002a19-0000-1000-8000-00805f9b34fb         → Battery Level
# 00002A19-0000-1000-8000-00805F9B34FB         → Battery Level
```

For more basic usage examples, see the [Quick Start Guide](../tutorials/quickstart.md).

For async parsing patterns, see the [Async Usage Guide](async-usage.md).

## Real-World Usage Patterns

For complete examples with BLE connection code, see the [BLE Integration Guide](ble-integration.md).

### Parsing Notifications

Parse incoming notification data with type safety:

```python
from bluetooth_sig.gatt.characteristics import (
    HeartRateMeasurementCharacteristic,
)

heart_rate = HeartRateMeasurementCharacteristic()


def on_heart_rate(sender, data: bytearray):
    """Notification callback - parse with full type safety."""
    hr_data = heart_rate.parse_value(data)
    print(f"Heart Rate: {hr_data.heart_rate} bpm")
    if hr_data.rr_intervals:
        print(f"RR intervals: {hr_data.rr_intervals}")


# Register callback with your BLE library's notification API
# await client.start_notify(str(heart_rate.uuid), on_heart_rate)
```

### Pairing Multiple Characteristics

Use `DependencyPairingBuffer` when you need to wait for multiple characteristics before processing:

```python
from typing import Any

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HeartRateMeasurementCharacteristic,
)
from bluetooth_sig.stream.pairing import DependencyPairingBuffer

hr = HeartRateMeasurementCharacteristic()
battery = BatteryLevelCharacteristic()


def on_complete_reading(paired_data: dict[str, Any]):
    """Called when both heart rate and battery level arrive."""
    hr_data = paired_data[str(hr.uuid)]
    battery_level = paired_data[str(battery.uuid)]
    print(f"Heart Rate: {hr_data.heart_rate} bpm, Battery: {battery_level}%")


buffer = DependencyPairingBuffer(
    translator=BluetoothSIGTranslator(),
    required_uuids={str(hr.uuid), str(battery.uuid)},
    group_key=lambda uuid, parsed: 0,  # All notifications go to same group
    on_pair=on_complete_reading,
)

# Feed notification/read data into buffer
hr_bytes = bytearray([0x00, 75])  # Heart rate: 75 bpm
battery_bytes = bytearray([85])  # Battery: 85%

buffer.ingest(str(hr.uuid), hr_bytes)
buffer.ingest(str(battery.uuid), battery_bytes)  # Triggers on_complete_reading
```

## Dependency-Aware Batch Parsing (Recommended)

When multiple characteristics are related (e.g., Blood Pressure Measurement `0x2A35` and Intermediate Cuff Pressure `0x2A36`), parse them together so the translator can handle them correctly.

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

bpm_uuid = "2A35"
icp_uuid = "2A36"

# Example data (replace with actual BLE reads)
blood_pressure_measurement_bytes = bytearray(
    [0x00, 0x78, 0x00, 0x50, 0x00, 0x46, 0x00]
)
intermediate_cuff_pressure_bytes = bytearray(
    [0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00]
)

char_data = {
    bpm_uuid: blood_pressure_measurement_bytes,
    icp_uuid: intermediate_cuff_pressure_bytes,
}

results = translator.parse_characteristics(char_data)

bpm_value = results[bpm_uuid]
icp_value = results[icp_uuid]

print(
    f"Blood Pressure: {bpm_value.systolic}/{bpm_value.diastolic} {bpm_value.unit.value}"
)
print(
    f"Cuff Pressure: {icp_value.current_cuff_pressure} {icp_value.unit.value}"
)
```

This batch API is the most user-friendly path: you provide UUIDs and raw bytes; the library parses each characteristic according to its specification.

## Strongly-Typed Raw Input Containers

If you prefer typed containers before calling the translator, use these types:

- `bluetooth_sig.types.io.RawCharacteristicRead` — holds a single read (`uuid`, `raw_data`, optional `descriptors`, optional `properties`).
- `bluetooth_sig.types.io.RawCharacteristicBatch` — a batch of reads.
- `bluetooth_sig.types.io.to_parse_inputs(batch)` — converts a batch to the exact `(char_data, descriptor_data)` shapes accepted by `parse_characteristics`.

Example:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName
from bluetooth_sig.types.io import (
    RawCharacteristicBatch,
    RawCharacteristicRead,
    to_parse_inputs,
)

# Blood pressure measurement requires at least 7 bytes
blood_pressure_measurement_bytes = bytearray(
    [0x00, 0x78, 0x00, 0x50, 0x00, 0x46, 0x00]
)
# Intermediate cuff pressure also requires at least 7 bytes
intermediate_cuff_pressure_bytes = bytearray(
    [0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00]
)

bpm_uuid = "2A35"
icp_uuid = "2A36"

batch = RawCharacteristicBatch(
    items=[
        RawCharacteristicRead(
            uuid=bpm_uuid, raw_data=blood_pressure_measurement_bytes
        ),
        RawCharacteristicRead(
            uuid=icp_uuid, raw_data=intermediate_cuff_pressure_bytes
        ),
    ]
)

char_data, descriptor_data = to_parse_inputs(batch)
results = BluetoothSIGTranslator().parse_characteristics(char_data)
```

For BLE library integration patterns (bleak, simplepyble, etc.), see the [BLE Integration Guide](ble-integration.md) and [Migration Guide](migration.md).

______________________________________________________________________

## Troubleshooting

If you encounter errors when parsing characteristic data (e.g., unknown UUID, insufficient data, or value out of range), check:

- The UUID and data format match the official specification
- Your data is a bytearray of the correct length

See the [Testing Guide](testing.md) for more on validating your setup and troubleshooting parsing issues.

## Device Class

The `Device` class provides high-level device abstraction with service discovery, caching, and encryption tracking:

```python
# SKIP: Requires BLE hardware and ConnectionManagerProtocol implementation
from bluetooth_sig import BluetoothSIGTranslator, Device
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

# connection_manager implements ConnectionManagerProtocol
device = Device(connection_manager, BluetoothSIGTranslator())

await device.connect()
await device.discover_services()

# Type-safe read
battery = await device.read(BatteryLevelCharacteristic)
print(f"Battery: {battery}%")

# Check encryption requirements
print(f"Requires encryption: {device.encryption.requires_encryption}")
```

**Device data structures:**

- `DeviceService` — Groups a service with its parsed characteristics
- `DeviceEncryption` — Tracks encryption and authentication requirements
- `DeviceAdvertiserData` — Parsed advertisement data

For connection manager setup, see the [BLE Integration Guide](ble-integration.md).

## Controlling Validation

By default, characteristics validate all data against Bluetooth SIG specifications. Disable validation for testing or debugging non-compliant devices:

```python
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

# Create characteristic instance
char = BatteryLevelCharacteristic()

# Default: validation enabled (raises on out-of-range)
# Disable for permissive parsing using validate=False on parse_value
result = char.parse_value(
    bytearray([50])  # Valid battery level
)
print(f"Battery: {result}%")  # Battery: 50%
```

Use `validate=False` for testing with synthetic data or debugging firmware. Keep validation enabled (default) for production code.

## Next Steps

- [Quick Start Guide](../tutorials/quickstart.md) - Basic getting started
- [BLE Integration Guide](ble-integration.md) - Connect with bleak, simplepyble, etc.
- [Supported Characteristics](../reference/characteristics.md) - Complete list of supported GATT characteristics
- [API Reference](../api/index.md) - Detailed API documentation
- [Testing Guide](testing.md) - How to test your BLE integration

# Working with Characteristics

GATT characteristics are the primary data containers in Bluetooth Low Energy. This guide covers parsing, encoding, registry lookup, and creating custom characteristics.

## When to Use Characteristic Classes

- **Type-safe parsing** — Get full IDE inference on parsed values
- **Known devices** — When you know what characteristics the device has
- **Encoding data** — Build bytes from structured values
- **Notifications** — Parse incoming notification data

## Parsing Characteristic Data

### Direct Class Usage (Type-Safe)

When you know the characteristic type, instantiate the class directly:

```python
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HeartRateMeasurementCharacteristic,
    TemperatureCharacteristic,
)

# Simple characteristic: returns int
battery = BatteryLevelCharacteristic()
level = battery.parse_value(bytearray([85]))  # IDE knows: int
print(f"Battery: {level}%")

# Complex characteristic: returns structured data
heart_rate = HeartRateMeasurementCharacteristic()
hr_data = heart_rate.parse_value(
    bytearray([0x00, 72])
)  # IDE knows: HeartRateData
print(f"Heart rate: {hr_data.heart_rate} bpm")
print(f"Sensor contact: {hr_data.sensor_contact}")  # Full autocomplete
```

### Dynamic Parsing (UUID Strings)

When discovering unknown devices, use the translator:

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Parse by UUID - returns Any
value = translator.parse_characteristic("2A19", bytearray([85]))

# Get characteristic info separately
info = translator.get_characteristic_info_by_uuid("2A19")
print(f"{info.name}: {value}")  # "Battery Level: 85"
```

## Encoding Data

Convert values back to bytes for writing to devices:

```python
from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    HeartRateMeasurementCharacteristic,
)
from bluetooth_sig.gatt.characteristics.heart_rate_measurement import (
    HeartRateData,
)

# Simple encoding
battery = BatteryLevelCharacteristic()
encoded = battery.build_value(85)
print(f"Bytes: {encoded.hex()}")  # "55"

# Complex encoding
heart_rate = HeartRateMeasurementCharacteristic()
data = HeartRateData(
    heart_rate=72,
    sensor_contact=True,
    energy_expended=None,
    rr_intervals=[],
)
encoded_hr = heart_rate.build_value(data)
print(f"Bytes: {encoded_hr.hex()}")
```

## Characteristic Registry

The `CharacteristicRegistry` provides dynamic lookup:

```python
from bluetooth_sig.gatt.characteristics import CharacteristicRegistry

# Check if UUID is a known characteristic
char_class = CharacteristicRegistry.get_characteristic_class_by_uuid("2A19")
if char_class:
    print(f"Found: {char_class.__name__}")  # BatteryLevelCharacteristic

# Get instance from UUID
instance = CharacteristicRegistry.get_characteristic(uuid="2A19")
if instance:
    value = instance.parse_value(bytearray([85]))
    print(f"Parsed: {value}")

# Get by name
from bluetooth_sig.gatt.characteristics.registry import CharacteristicName

char_class = CharacteristicRegistry.get_characteristic_class(
    CharacteristicName.BATTERY_LEVEL
)
```

## Custom Characteristics

For vendor-specific characteristics not defined by the Bluetooth SIG.

### Runtime Registration

Register a custom characteristic class at runtime. This example shows a sensor
characteristic with multiple fields and validation:

```python
import msgspec

from bluetooth_sig.gatt.characteristics import CharacteristicRegistry
from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID


class SensorReading(msgspec.Struct, frozen=True, kw_only=True):
    """Structured data from vendor sensor."""

    temperature: float  # Celsius
    humidity: float  # Percentage
    battery: int  # 0-100


class VendorSensorCharacteristic(CustomBaseCharacteristic):
    """Custom characteristic for vendor environmental sensor.

    Data format (6 bytes):
      Bytes 0-1: Temperature (sint16, 0.01°C resolution)
      Bytes 2-3: Humidity (uint16, 0.01% resolution)
      Byte 4: Battery level (uint8, 0-100%)
      Byte 5: Reserved
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("12345678-1234-1234-1234-123456789ABC"),
        name="Vendor Environmental Sensor",
    )

    min_length = 6
    expected_type = SensorReading

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SensorReading:
        # Parse temperature (signed 16-bit, 0.01°C resolution)
        temp_raw = int.from_bytes(data[0:2], "little", signed=True)
        temperature = temp_raw * 0.01

        # Parse humidity (unsigned 16-bit, 0.01% resolution)
        humidity_raw = int.from_bytes(data[2:4], "little", signed=False)
        humidity = humidity_raw * 0.01

        # Parse battery (0-100%)
        battery = data[4]

        return SensorReading(
            temperature=temperature,
            humidity=humidity,
            battery=battery,
        )

    def _encode_value(self, value: SensorReading) -> bytearray:
        result = bytearray(6)

        # Encode temperature
        temp_raw = int(value.temperature / 0.01)
        result[0:2] = temp_raw.to_bytes(2, "little", signed=True)

        # Encode humidity
        humidity_raw = int(value.humidity / 0.01)
        result[2:4] = humidity_raw.to_bytes(2, "little", signed=False)

        # Encode battery
        result[4] = value.battery

        # Reserved byte
        result[5] = 0x00

        return result


# Register with the registry
CharacteristicRegistry.register_characteristic_class(
    uuid="12345678-1234-1234-1234-123456789ABC",
    char_cls=VendorSensorCharacteristic,
)

# Use it
sensor = VendorSensorCharacteristic()

# Decode: raw bytes → structured data
raw_data = bytearray([0xC4, 0x09, 0xDC, 0x0D, 0x5A, 0x00])  # 25°C, 35.5%, 90%
reading = sensor.parse_value(raw_data)
print(
    f"Temp: {reading.temperature}°C, Humidity: {reading.humidity}%, Battery: {reading.battery}%"
)

# Encode: structured data → raw bytes
new_reading = SensorReading(temperature=22.5, humidity=45.0, battery=85)
encoded = sensor.build_value(new_reading)
print(f"Encoded: {encoded.hex()}")
```

### Cleanup Custom Registrations

```python
from bluetooth_sig.gatt.characteristics import CharacteristicRegistry

# Remove specific registration (if it was registered)
CharacteristicRegistry.unregister_characteristic_class(
    "12345678-1234-1234-1234-123456789ABC"
)

# Clear all custom registrations (useful for testing)
CharacteristicRegistry.clear_custom_registrations()
```

## Handling Notifications

Parse characteristic data from BLE notifications:

```python
# SKIP: Requires BLE hardware and async context for start_notify
from bluetooth_sig.gatt.characteristics import (
    HeartRateMeasurementCharacteristic,
)

heart_rate = HeartRateMeasurementCharacteristic()


def on_notification(sender, data: bytearray):
    """Handle incoming heart rate notification."""
    hr_data = heart_rate.parse_value(data)
    print(f"Heart Rate: {hr_data.heart_rate} bpm")

    if hr_data.rr_intervals:
        avg_rr = sum(hr_data.rr_intervals) / len(hr_data.rr_intervals)
        print(f"Avg RR interval: {avg_rr:.0f} ms")


# With bleak
await client.start_notify(str(heart_rate.uuid), on_notification)
```

## Context-Dependent Parsing

Some characteristics require context from other characteristics. When using
`translator.process_services()`, dependencies are resolved automatically. For
manual parsing, you can provide context explicitly:

```python
from bluetooth_sig.gatt.characteristics import (
    BodySensorLocationCharacteristic,
    HeartRateMeasurementCharacteristic,
)
from bluetooth_sig.gatt.context import CharacteristicContext

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
location_bytes = bytearray([0x01])  # Chest sensor location
measurement_bytes = bytearray([0x00, 72])  # 72 bpm heart rate

# Read feature characteristic first
location = BodySensorLocationCharacteristic()
location_value = location.parse_value(location_bytes)
print(f"Sensor location: {location_value}")

# Create context with feature data for dependent characteristics
ctx = CharacteristicContext(
    other_characteristics={"body_sensor_location": location_value},
)

# Parse measurement with context
hr = HeartRateMeasurementCharacteristic()
hr_data = hr.parse_value(measurement_bytes, ctx=ctx)
print(f"Heart rate: {hr_data.heart_rate} bpm")
```

> **Tip:** For automatic dependency resolution, use `translator.process_services()`
> which builds context from all discovered characteristics. See
> [Working with Services](services.md) for details.

## Error Handling

Handle parsing errors gracefully:

```python
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
from bluetooth_sig.gatt.exceptions import (
    CharacteristicEncodeError,
    CharacteristicParseError,
)

battery = BatteryLevelCharacteristic()

try:
    # Invalid data (wrong length)
    value = battery.parse_value(bytearray([]))
except CharacteristicParseError as e:
    print(f"Parse error: {e}")

try:
    # Invalid value (out of range)
    encoded = battery.build_value(150)  # Battery max is 100
except CharacteristicEncodeError as e:
    print(f"Encode error: {e}")
```

## See Also

- [API Overview](../explanation/api-overview.md) — When to use each parsing approach
- [Adding Characteristics](adding-characteristics.md) — Extend the library with new SIG characteristics
- [Supported Characteristics](../reference/characteristics.md) — Complete list of implemented characteristics
- [BLE Integration](ble-integration.md) — Full integration patterns with BLE libraries

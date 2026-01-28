# Migration Guide: Adopt the Bluetooth SIG Standards Library

This guide shows how to migrate existing BLE code to use the library's parsing. Examples are based on **real-world applications** like heart rate monitors, environmental sensors, and smart home devices.

The library stays backend-agnostic: **you keep your connection code** (Bleak, SimplePyBLE, etc.) and drop the parser into your reads/notifications.

## Who is this for?

- You already read GATT characteristics via a BLE client (Bleak, SimplePyBLE, Home Assistant, etc.)
- You manually parse bytes today and want robust, spec-aligned parsing with validation and types
- You're building health monitors, environmental sensors, or smart home devices

## Real-World Example 1: Heart Rate Monitor

**Based on**: Polar H10, Fitbit, Apple Watch integrations

**Before** (manual parsing - typical fitness app pattern):

```python
# SKIP: Migration "before" example (anti-pattern)
# Common pattern from real fitness app integrations
async with BleakClient(device_address) as client:

    def heart_rate_handler(sender, data: bytearray):
        # Manual bit manipulation from BLE Heart Rate spec
        flags = data[0]
        hr_format = flags & 0x01
        if hr_format == 0:
            heart_rate = data[1]
            offset = 2
        else:
            heart_rate = int.from_bytes(data[1:3], "little")
            offset = 3

        # Energy expended (if present)
        energy = None
        if flags & 0x08:
            energy = int.from_bytes(data[offset : offset + 2], "little")
            offset += 2

        # RR intervals (if present)
        rr_intervals = []
        if flags & 0x10:
            while offset < len(data):
                rr = int.from_bytes(data[offset : offset + 2], "little")
                rr_intervals.append(rr / 1024.0)  # Convert to seconds
                offset += 2

        print(f"HR: {heart_rate} bpm, Energy: {energy} kJ, RR: {rr_intervals}")

    await client.start_notify("2A37", heart_rate_handler)
```

**After** (with bluetooth-sig-python):

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator


async def main():
    translator = BluetoothSIGTranslator()

    # Note: This is a simplified example - in production, use actual BleakClient
    def heart_rate_handler(sender, data: bytearray):
        # Returns HeartRateData directly - type-safe dataclass
        hr_data = translator.parse_characteristic("2A37", data)
        print(f"HR: {hr_data.heart_rate} bpm")
        if hr_data.energy_expended:
            print(f"Energy: {hr_data.energy_expended} kJ")
        if hr_data.rr_intervals:
            print(f"RR intervals: {hr_data.rr_intervals} seconds")

    # Test with sample data
    heart_rate_handler(None, bytearray([0x00, 0x55]))


asyncio.run(main())
```

**What improved**:

- ✅ No manual bit manipulation or offset tracking
- ✅ Automatic unit conversions (RR intervals to seconds)
- ✅ Type-safe access to all fields with autocomplete
- ✅ Validates against spec (catches malformed data)

## Real-World Example 2: Environmental Sensor Dashboard

**Based on**: Xiaomi LYWSD03MMC, SwitchBot Meter, Govee sensors

**Before** (manual parsing - typical home automation pattern):

```python
# SKIP: Migration "before" example (anti-pattern)
# Common pattern from home automation projects (Home Assistant, openHAB)
async with BleakClient(device_address) as client:
    # Read battery level
    battery_bytes = await client.read_gatt_char("2A19")
    battery = battery_bytes[0]

    # Read temperature
    temp_bytes = await client.read_gatt_char("2A6E")
    temp_raw = int.from_bytes(temp_bytes[0:2], "little", signed=True)
    temperature = temp_raw / 100.0  # Convert to °C

    # Read humidity
    humidity_bytes = await client.read_gatt_char("2A6F")
    humidity = int.from_bytes(humidity_bytes[0:2], "little") / 100.0

    print(f"Battery: {battery}%, Temp: {temperature}°C, Humidity: {humidity}%")
```

**After** (with bluetooth-sig-python):

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator


async def main():
    translator = BluetoothSIGTranslator()

    # ============================================
    # SIMULATED DATA - Replace with actual BLE reads
    # ============================================
    SIMULATED_BATTERY_DATA = bytearray([85])  # Simulates 85% battery
    SIMULATED_TEMP_DATA = bytearray([0x64, 0x09])  # Simulates 24.04°C
    SIMULATED_HUMIDITY_DATA = bytearray([0x3A, 0x13])  # Simulates 49.22%

    # Parse each characteristic - returns values directly
    battery = translator.parse_characteristic(
        "2A19", SIMULATED_BATTERY_DATA
    )  # int
    temp = translator.parse_characteristic(
        "2A6E", SIMULATED_TEMP_DATA
    )  # float
    humidity = translator.parse_characteristic(
        "2A6F", SIMULATED_HUMIDITY_DATA
    )  # float

    print(f"Battery: {battery}%")
    print(f"Temp: {temp}°C")
    print(f"Humidity: {humidity}%")


asyncio.run(main())
```

**What improved**:

- ✅ Single parse call for multiple characteristics
- ✅ Automatic unit handling (no hardcoded divisors)
- ✅ Cleaner, more maintainable code
- ✅ Consistent error handling across all values

## Real-World Example 3: Glucose Meter with Context

**Based on**: OneTouch Verio, AccuChek Guide, Abbott FreeStyle

**Before** (manual pairing logic):

```python
# SKIP: Migration "before" example (anti-pattern)
# Typical medical device integration pattern
async with BleakClient(device_address) as client:
    measurements = {}
    contexts = {}

    def measurement_handler(sender, data: bytearray):
        seq = int.from_bytes(data[1:3], "little")
        # Complex flag parsing...
        glucose = int.from_bytes(data[3:5], "little")
        measurements[seq] = glucose / 100000.0  # mg/dL conversion

    def context_handler(sender, data: bytearray):
        seq = int.from_bytes(data[1:3], "little")
        # More flag parsing...
        carbs = data[3]
        contexts[seq] = carbs

    await client.start_notify(
        "2A18", measurement_handler
    )  # Glucose Measurement
    await client.start_notify("2A34", context_handler)  # Glucose Context

    # Manual pairing logic
    await asyncio.sleep(5)
    for seq in measurements:
        if seq in contexts:
            print(
                f"Seq {seq}: {measurements[seq]} mg/dL, Carbs: {contexts[seq]}g"
            )
```

**After** (with automatic dependency resolution):

```python
# SKIP: Requires BLE hardware and bleak client connection
import asyncio

from bluetooth_sig import BluetoothSIGTranslator


async def main():
    translator = BluetoothSIGTranslator()
    gm_uuid = "2A18"
    gmc_uuid = "2A34"

    measurements_cache = {}
    contexts_cache = {}

    # Example of handling paired characteristics
    def combined_handler(char_uuid: str, data: bytearray):
        # Parse immediately to get the sequence number
        # Returns the parsed value directly (GlucoseMeasurement or GlucoseMeasurementContext)
        parsed = translator.parse_characteristic(char_uuid, data)

        # Cache using the parsed sequence number
        if char_uuid == gm_uuid:
            seq = parsed.sequence_number
            measurements_cache[seq] = data
        elif char_uuid == gmc_uuid:
            seq = parsed.sequence_number
            contexts_cache[seq] = data

        # Parse pairs when we have matching sequence numbers
        matching_seqs = set(measurements_cache.keys()) & set(
            contexts_cache.keys()
        )
        for seq in matching_seqs:
            results = translator.parse_characteristics(
                {
                    gm_uuid: measurements_cache[seq],
                    gmc_uuid: contexts_cache[seq],
                }
            )

            gm = results[gm_uuid]  # GlucoseMeasurementData directly
            gmc = results[gmc_uuid]  # GlucoseMeasurementContextData directly
            print(f"Seq {seq}: Glucose {gm.glucose_concentration} {gm.unit}")
            print(f"Seq {seq}: Carbs {gmc.carbohydrate} g")

            # Remove processed entries
            del measurements_cache[seq]
            del contexts_cache[seq]

    await client.start_notify(
        gm_uuid, lambda s, d: combined_handler(gm_uuid, d)
    )
    await client.start_notify(
        gmc_uuid, lambda s, d: combined_handler(gmc_uuid, d)
    )
```

**What improved**:

- ✅ Automatic validation of sequence number pairing
- ✅ Type-safe access to complex nested structures
- ✅ Proper unit handling (mol/L vs mg/dL)
- ✅ No manual offset calculations

## Real-World Example 4: Device Service Discovery

**Based on**: Bleak's `service_explorer.py` pattern

**Before** (reading and manually parsing all characteristics):

```python
# SKIP: Migration "before" example (anti-pattern)
# Common pattern from BLE exploration tools
async with BleakClient(device_address) as client:
    for service in client.services:
        print(f"[Service] {service.uuid}")
        for char in service.characteristics:
            if "read" in char.properties:
                try:
                    value = await client.read_gatt_char(char)
                    # Manual parsing depends on UUID
                    if char.uuid == "2A19":
                        print(f"  Battery: {value[0]}%")
                    elif char.uuid == "2A37":
                        hr = value[1]
                        print(f"  Heart Rate: {hr} bpm")
                    else:
                        print(f"  Raw: {value.hex()}")
                except Exception as e:
                    print(f"  Error: {e}")
```

**After** (with automatic parsing):

```python
import asyncio

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.exceptions import CharacteristicParseError

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])  # Simulates 85% battery
SIMULATED_HR_DATA = bytearray([0x00, 0x55])  # Simulates heart rate measurement


async def main():
    translator = BluetoothSIGTranslator()

    # Example: parse known characteristics using UUIDs
    characteristics = {
        "2A19": SIMULATED_BATTERY_DATA,  # Battery
        "2A37": SIMULATED_HR_DATA,  # Heart Rate
    }

    for uuid, raw_bytes in characteristics.items():
        try:
            result = translator.parse_characteristic(uuid, raw_bytes)
            info = translator.get_characteristic_info_by_uuid(uuid)
            # For simple types (int/float), result is the value directly
            # For complex types, result is a dataclass with fields
            if hasattr(result, "heart_rate"):
                print(f"  {info.name}: {result.heart_rate} bpm")
            else:
                print(f"  {info.name}: {result}")
        except CharacteristicParseError:
            print(f"  {uuid}: {raw_bytes.hex()} (parse failed)")


asyncio.run(main())
```

**What improved**:

- ✅ Automatic characteristic identification by UUID
- ✅ No UUID-specific parsing logic needed
- ✅ Graceful fallback for unknown characteristics
- ✅ Human-readable characteristic names

## Batch Parsing (Dependencies)

If characteristics depend on each other (e.g., Glucose Measurement + Context), parse them together.

### Minimal path (no adapters)

```python
from bluetooth_sig import BluetoothSIGTranslator

# Example data (replace with actual BLE reads)
bpm_bytes = bytearray(
    [0x00, 0x78, 0x00, 0x50, 0x00, 0x46, 0x00]
)  # Blood Pressure
battery_bytes = bytearray([85])  # Battery Level

translator = BluetoothSIGTranslator()

bpm_uuid = "2A35"
battery_uuid = "2A19"

values = {
    bpm_uuid: bpm_bytes,
    battery_uuid: battery_bytes,
}
results = translator.parse_characteristics(values)

print(f"Blood Pressure: {results[bpm_uuid]}")
print(f"Battery: {results[battery_uuid]}%")
```

### With Connection Managers

Example adapters are provided in `examples/connection_managers/` as references.

```python
from bluetooth_sig import BluetoothSIGTranslator

# Example data (replace with actual BLE reads)
heart_rate_bytes = bytearray([0x00, 75])  # Heart Rate 75 bpm
battery_bytes = bytearray([92])  # Battery 92%

translator = BluetoothSIGTranslator()

# Simple batch parsing
char_data = {
    "2A37": heart_rate_bytes,
    "2A19": battery_bytes,
}

results = translator.parse_characteristics(char_data)
print(f"Heart Rate: {results['2A37']}")
print(f"Battery: {results['2A19']}%")
```

### With descriptors/services (adapters in examples)

- Bleak: `examples/connection_managers/bleak_utils.py`
- SimplePyBLE: `examples/connection_managers/simpleble.py`

```python
# SKIP: Requires BLE connection (client.services from bleak)
from bluetooth_sig import CharacteristicName
from bluetooth_sig.types.io import to_parse_inputs
from examples.connection_managers.bleak_utils import bleak_services_to_batch

gm_uuid = "2A18"
gmc_uuid = "2A34"

services = client.services
values = {gm_uuid: gm_bytes, gmc_uuid: gmc_bytes}

batch = bleak_services_to_batch(services, values_by_uuid=values)
char_data, desc_data = to_parse_inputs(batch)
results = translator.parse_characteristics(
    char_data, descriptor_data=desc_data
)
```

**Note**: Example adapters are provided as references; update them as needed for your project/backend versions.

## Device + Connection Manager (larger apps)

For applications managing multiple devices or complex workflows, use the Device pattern:

```python
# SKIP: Needs real BLE device
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()
device = Device(address, translator)

# Your manager implements ConnectionManagerProtocol (connect/read/write/notify/etc.)
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
from examples.connection_managers.bleak_retry import (
    BleakRetryConnectionManager,
)

battery = BatteryLevelCharacteristic()
manager = BleakRetryConnectionManager(address)
device.attach_connection_manager(manager)
await device.connect()

# Type-safe read with characteristic class
parsed = await device.read(BatteryLevelCharacteristic)
await device.disconnect()
```

## Migration Checklist

- ✅ Keep your BLE client code (Bleak/SimplePyBLE) unchanged
- ✅ After each read or in notification callbacks, call `parse_characteristic(uuid, bytes)`
- ✅ For multiple related characteristics, call `parse_characteristics({uuid: bytes})`
- ✅ Include descriptors when needed (via adapters or `descriptor_data` mapping)
- ✅ For larger apps, adopt a `ConnectionManagerProtocol` + `Device` pattern

## Where are the example adapters?

- `examples/connection_managers/bleak_utils.py` → `bleak_services_to_batch(...)`
- `examples/connection_managers/simpleble.py` → `simpleble_services_to_batch(...)`

These adapters are intentionally kept in examples to avoid hard dependencies. Copy or adapt them for your project; they may require updates to match your specific library versions and object shapes.

## Adoption in Real Projects

### Home Assistant Integration Pattern

```python
# SKIP: Requires Home Assistant
from homeassistant.components import bluetooth

from bluetooth_sig.gatt.characteristics import TemperatureCharacteristic


class MySensorEntity(SensorEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._temp = TemperatureCharacteristic()

    def _async_handle_bluetooth_event(
        self, service_info: BluetoothServiceInfoBleak, change: BluetoothChange
    ) -> None:
        """Handle bluetooth callback."""
        # Your existing connection/read logic
        char_data = self._read_characteristic(str(self._temp.uuid))

        # Type-safe parsing - IDE knows value is float
        value = self._temp.parse_value(bytearray(char_data))
        self._attr_native_value = value
        self._attr_native_unit_of_measurement = self._temp.unit
```

### SimplePyBLE Pattern

```python
# SKIP: Requires SimplePyBLE
import simplepyble

from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic

battery = BatteryLevelCharacteristic()

peripheral = simplepyble.Peripheral()
peripheral.connect_to_address(device_address)

for service in peripheral.services():
    for characteristic in service.characteristics():
        try:
            data = peripheral.read(service.uuid(), characteristic.uuid())
            value = translator.parse_characteristic(
                characteristic.uuid(), data
            )
            info = translator.get_characteristic_info_by_uuid(
                characteristic.uuid()
            )
            if info:
                print(f"{info.name}: {value} {info.unit or ''}")
        except Exception as e:
            print(f"Error reading {characteristic.uuid()}: {e}")
```

## Troubleshooting

- **Unknown UUID**: Ensure you're using the correct SIG UUID (short or full).
- **Parse failed**: Check spec constraints (length, range); `result.error_message` explains the issue.
- **Descriptor-dependent parsing**: Pass descriptor bytes via `descriptor_data` or use the example adapters.
- **Advertising data**: Use `AdvertisingPDUParser` for parsing advertising packets—see [Advertising Parsing Guide](advertising-parsing.md).
- **Type hints not working**: Ensure you're using Python 3.10+ for best type checking support.

## Next Steps

- See [Usage Guide](usage.md) for detailed API documentation
- Check [examples/](https://github.com/RonanB96/bluetooth-sig-python/tree/main/examples) for complete working applications
- Review [supported characteristics](../reference/characteristics.md) to see what's available

## Pairing Dependent Characteristics (Blood Pressure Example)

Some BLE profiles send related data in separate notifications that must be paired. For example, during a Blood Pressure measurement, the device sends **Intermediate Cuff Pressure** notifications repeatedly as the cuff inflates, then a final **Blood Pressure Measurement**. If multiple measurement sessions overlap (or you have multiple devices), you need to pair notifications correctly.

The `DependencyPairingBuffer` helper buffers notifications and groups them using a caller-defined key (timestamp, sequence number, session ID, etc.).

### Real-World Scenario: Blood Pressure Monitor

```python
# SKIP: Requires BLE hardware connection
from datetime import datetime

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.stream import DependencyPairingBuffer
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()

bpm_uuid = "2A35"
icp_uuid = "2A36"


def group_by_timestamp(uuid: str, parsed) -> datetime:
    """Group notifications by their timestamp - same session = same timestamp.

    Args:
        uuid: The characteristic UUID (for reference)
        parsed: The parsed value directly (BloodPressureMeasurement or IntermediateCuffPressure)
    """
    # Both characteristics have optional timestamp fields
    if hasattr(parsed, "optional_fields") and parsed.optional_fields.timestamp:
        return parsed.optional_fields.timestamp

    # Fallback: use current time or synthetic session tracking
    raise ValueError("Timestamp required for grouping")


def on_measurement_complete(results):
    """Called when both BPM and ICP arrive for the same timestamp.

    Results is dict[str, Any] where values are parsed dataclasses directly.
    """
    bpm = results[bpm_uuid]  # BloodPressureMeasurement directly
    icp = results[icp_uuid]  # IntermediateCuffPressure directly

    print(f"Blood Pressure: {bpm.systolic}/{bpm.diastolic} mmHg")
    print(f"Max Cuff Pressure: {icp.current_cuff_pressure} mmHg")

    # Store to database, update UI, etc.


buffer = DependencyPairingBuffer(
    translator=translator,
    required_uuids={bpm_uuid, icp_uuid},
    group_key=group_by_timestamp,
    on_pair=on_measurement_complete,
)

# In your notification handlers (notifications arrive in any order)
async with BleakClient(device_address) as client:
    await client.start_notify(
        bpm_uuid, lambda s, d: buffer.ingest(bpm_uuid, d)
    )
    await client.start_notify(
        icp_uuid, lambda s, d: buffer.ingest(icp_uuid, d)
    )

    # Buffer automatically pairs when both arrive with matching timestamps
    await asyncio.sleep(30)  # Wait for measurements
```

### Why This is Useful

**Without the buffer**: You'd manually track which ICP belongs to which BPM, especially when:

- Multiple measurement sessions overlap (nurse takes measurements from multiple patients)
- Notifications arrive out of order (common with BLE)
- Network delays cause interleaving

**With the buffer**: Automatically groups by timestamp, handles out-of-order arrival, and triggers your callback only when complete pairs arrive.

### Paired Characteristics Example

Group characteristics by a key (e.g., timestamp, sequence number) and trigger a callback when all required characteristics arrive:

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.stream import DependencyPairingBuffer

translator = BluetoothSIGTranslator()

hr_uuid = "2A37"  # Heart Rate Measurement
bat_uuid = "2A19"  # Battery Level

received_pairs = []


def on_pair(results):
    """Handle complete pair of characteristics."""
    hr = results[hr_uuid]  # HeartRateData
    bat = results[bat_uuid]  # int
    received_pairs.append(results)
    print(f"Heart Rate: {hr.heart_rate} bpm, Battery: {bat}%")


buffer = DependencyPairingBuffer(
    translator=translator,
    required_uuids={hr_uuid, bat_uuid},
    group_key=lambda uuid, parsed: 0,  # All go to same group
    on_pair=on_pair,
)

# Example data (in real use, comes from BLE notifications)
hr_bytes = bytearray([0x00, 75])  # Heart rate 75 bpm
bat_bytes = bytearray([85])  # Battery 85%

# Ingest data (order-independent)
buffer.ingest(hr_uuid, hr_bytes)
buffer.ingest(bat_uuid, bat_bytes)  # Triggers on_pair callback

print(f"Total received: {len(received_pairs)}")
```

### Notes

- **Generic**: Works with any paired characteristics - you define the grouping key
- **Validation**: Implement profile-specific validation (sequence matching, etc.) in your `on_pair` callback
- **Backend-agnostic**: Buffer only handles UUID strings and bytes; keep subscription management in your BLE client
- **Order-independent**: Notifications can arrive in any order; buffer waits for both before calling your callback

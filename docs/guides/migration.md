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
            heart_rate = int.from_bytes(data[1:3], 'little')
            offset = 3

        # Energy expended (if present)
        energy = None
        if flags & 0x08:
            energy = int.from_bytes(data[offset:offset+2], 'little')
            offset += 2

        # RR intervals (if present)
        rr_intervals = []
        if flags & 0x10:
            while offset < len(data):
                rr = int.from_bytes(data[offset:offset+2], 'little')
                rr_intervals.append(rr / 1024.0)  # Convert to seconds
                offset += 2

        print(f"HR: {heart_rate} bpm, Energy: {energy} kJ, RR: {rr_intervals}")

    await client.start_notify("2A37", heart_rate_handler)
```

**After** (with bluetooth-sig-python):

```python
import asyncio
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

# ============================================
# SIMULATED DATA - Replace with actual device
# ============================================
SIMULATED_DEVICE_ADDRESS = "AA:BB:CC:DD:EE:FF"

async def main():
    translator = BluetoothSIGTranslator()

    # Note: This is a simplified example - in production, use actual BleakClient
    def heart_rate_handler(sender, data: bytearray):
        parsed = translator.parse_characteristic("2A37", data)
        if parsed.parse_success:
            hr_data = parsed.value  # HeartRateMeasurementData
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
    temp_raw = int.from_bytes(temp_bytes[0:2], 'little', signed=True)
    temperature = temp_raw / 100.0  # Convert to °C

    # Read humidity
    humidity_bytes = await client.read_gatt_char("2A6F")
    humidity = int.from_bytes(humidity_bytes[0:2], 'little') / 100.0

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
    SIMULATED_BATTERY_DATA = bytearray([85])           # Simulates 85% battery
    SIMULATED_TEMP_DATA = bytearray([0x64, 0x09])     # Simulates 24.04°C
    SIMULATED_HUMIDITY_DATA = bytearray([0x3A, 0x13]) # Simulates 49.22%

    # Example with mock data - you can use UUIDs or CharacteristicName string names
    from bluetooth_sig.types.gatt_enums import CharacteristicName

    # Using UUIDs from your BLE library
    battery_uuid = "2A19"
    temp_uuid = "2A6E"
    humidity_uuid = "2A6F"

    # Or using CharacteristicName enum for string names (both work!)
    # battery_name = CharacteristicName.BATTERY_LEVEL  # Resolves to "Battery Level"

    # Parse all at once
    results = translator.parse_characteristics({
        battery_uuid: SIMULATED_BATTERY_DATA,
        temp_uuid: SIMULATED_TEMP_DATA,
        humidity_uuid: SIMULATED_HUMIDITY_DATA,
    })

    print(f"Battery: {results[battery_uuid].value}{results[battery_uuid].info.unit or ''}")
    print(f"Temp: {results[temp_uuid].value}{results[temp_uuid].info.unit or ''}")
    print(f"Humidity: {results[humidity_uuid].value}{results[humidity_uuid].info.unit or ''}")

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
        seq = int.from_bytes(data[1:3], 'little')
        # Complex flag parsing...
        glucose = int.from_bytes(data[3:5], 'little')
        measurements[seq] = glucose / 100000.0  # mg/dL conversion

    def context_handler(sender, data: bytearray):
        seq = int.from_bytes(data[1:3], 'little')
        # More flag parsing...
        carbs = data[3]
        contexts[seq] = carbs

    await client.start_notify("2A18", measurement_handler)  # Glucose Measurement
    await client.start_notify("2A34", context_handler)      # Glucose Context

    # Manual pairing logic
    await asyncio.sleep(5)
    for seq in measurements:
        if seq in contexts:
            print(f"Seq {seq}: {measurements[seq]} mg/dL, Carbs: {contexts[seq]}g")
```

**After** (with automatic dependency resolution):

```python
# SKIP: Async function needs completion
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
        parsed = translator.parse_characteristic(char_uuid, data)

        if not parsed.parse_success:
            return

        # Cache using the parsed sequence number
        if char_uuid == gm_uuid:
            seq = parsed.value.sequence_number
            measurements_cache[seq] = data
        elif char_uuid == gmc_uuid:
            seq = parsed.value.sequence_number
            contexts_cache[seq] = data

        # Parse pairs when we have matching sequence numbers
        matching_seqs = set(measurements_cache.keys()) & set(contexts_cache.keys())
        for seq in matching_seqs:
            results = translator.parse_characteristics({
                gm_uuid: measurements_cache[seq],
                gmc_uuid: contexts_cache[seq],
            })

            gm = results[gm_uuid].value  # GlucoseMeasurementData
            gmc = results[gmc_uuid].value  # GlucoseMeasurementContextData
            print(f"Seq {seq}: Glucose {gm.concentration} {results[gm_uuid].unit}")
            print(f"Seq {seq}: Carbs {gmc.carbohydrate} g")

            # Remove processed entries
            del measurements_cache[seq]
            del contexts_cache[seq]

    await client.start_notify(gm_uuid, lambda s, d: combined_handler(gm_uuid, d))
    await client.start_notify(gmc_uuid, lambda s, d: combined_handler(gmc_uuid, d))
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

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])         # Simulates 85% battery
SIMULATED_HR_DATA = bytearray([0x00, 0x55])     # Simulates heart rate measurement

async def main():
    translator = BluetoothSIGTranslator()

    # Example: parse known characteristics using UUIDs
    characteristics = {
        "2A19": SIMULATED_BATTERY_DATA,     # Battery
        "2A37": SIMULATED_HR_DATA,          # Heart Rate
    }

    for uuid, value in characteristics.items():
        parsed = translator.parse_characteristic(uuid, value)
        if parsed.parse_success:
            print(f"  {parsed.info.name}: {parsed.value} {parsed.info.unit or ''}")
        else:
            print(f"  {uuid}: {value.hex()} (unknown)")

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
from bluetooth_sig.types.gatt_enums import CharacteristicName

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
gm_bytes = bytearray([0x00, 0x01, 0x02])  # Simulated glucose measurement
gmc_bytes = bytearray([0x03, 0x04])       # Simulated glucose context

translator = BluetoothSIGTranslator()

gm_uuid = "2A18"
gmc_uuid = "2A34"

values = {
    gm_uuid: gm_bytes,
    gmc_uuid: gmc_bytes,
}
results = translator.parse_characteristics(values)
```

### With Connection Managers

Example adapters are provided in `examples/connection_managers/` as references.

```python
from bluetooth_sig import BluetoothSIGTranslator

# ============================================
# SIMULATED DATA - Replace with actual BLE reads
# ============================================
glucose_measurement_bytes = bytearray([0x00, 0x01, 0x02])  # Simulated glucose measurement
glucose_context_bytes = bytearray([0x03, 0x04])            # Simulated glucose context

translator = BluetoothSIGTranslator()

# Simple batch parsing
char_data = {
    "2A18": glucose_measurement_bytes,
    "2A34": glucose_context_bytes,
}

results = translator.parse_characteristics(char_data)
```

### With descriptors/services (adapters in examples)

- Bleak: `examples/connection_managers/bleak_utils.py`
- SimplePyBLE: `examples/connection_managers/simpleble.py`

```python
# SKIP: Requires external modules
from bluetooth_sig import CharacteristicName
from bluetooth_sig.types.io import to_parse_inputs
from examples.connection_managers.bleak_utils import bleak_services_to_batch

gm_uuid = "2A18"
gmc_uuid = "2A34"

services = client.services
values = {gm_uuid: gm_bytes, gmc_uuid: gmc_bytes}

batch = bleak_services_to_batch(services, values_by_uuid=values)
char_data, desc_data = to_parse_inputs(batch)
results = translator.parse_characteristics(char_data, descriptor_data=desc_data)
```

**Note**: Example adapters are provided as references; update them as needed for your project/backend versions.

## Device + Connection Manager (larger apps)

For applications managing multiple devices or complex workflows, use the Device pattern:

```python
# SKIP: Needs real BLE device
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName
from bluetooth_sig.device import Device

translator = BluetoothSIGTranslator()
device = Device(address, translator)

# Your manager implements ConnectionManagerProtocol (connect/read/write/notify/etc.)
from examples.connection_managers.bleak_retry import BleakRetryConnectionManager

manager = BleakRetryConnectionManager(address)
device.attach_connection_manager(manager)
await device.connect()

battery_uuid = "2A19"
parsed = await device.read(battery_uuid)
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
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()

class MySensorEntity(SensorEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._temp_uuid = "2A6E"

    def _async_handle_bluetooth_event(
        self, service_info: BluetoothServiceInfoBleak, change: BluetoothChange
    ) -> None:
        """Handle bluetooth callback."""
        # Your existing connection/read logic
        char_data = self._read_characteristic(self._temp_uuid)

        # Parse with library
        result = translator.parse_characteristic(self._temp_uuid, char_data)
        if result.parse_success:
            self._attr_native_value = result.value
            self._attr_native_unit_of_measurement = result.unit
```

### SimplePyBLE Pattern

```python
# SKIP: Requires SimplePyBLE
import simplepyble
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

peripheral = simplepyble.Peripheral()
peripheral.connect_to_address(device_address)

for service in peripheral.services():
    for characteristic in service.characteristics():
        try:
            data = peripheral.read(service.uuid(), characteristic.uuid())
            result = translator.parse_characteristic(characteristic.uuid(), data)
            if result.parse_success:
                print(f"{result.name}: {result.value} {result.unit}")
        except Exception as e:
            print(f"Error reading {characteristic.uuid()}: {e}")
```

## Troubleshooting

- **Unknown UUID**: Ensure you're using the correct SIG UUID (short or full).
- **Parse failed**: Check spec constraints (length, range); `result.error_message` explains the issue.
- **Descriptor-dependent parsing**: Pass descriptor bytes via `descriptor_data` or use the example adapters.
- **Home Assistant-style (advertising)**: This library focuses on GATT characteristic parsing; advertising parsers are out of scope.
- **Type hints not working**: Ensure you're using Python 3.10+ for best type checking support.

## Next Steps

- See [Usage Guide](../usage.md) for detailed API documentation
- Check [examples/](https://github.com/RonanB96/bluetooth-sig-python/tree/main/examples) for complete working applications
- Review [supported characteristics](../supported-characteristics.md) to see what's available

## Pairing Dependent Characteristics (Blood Pressure Example)

Some BLE profiles send related data in separate notifications that must be paired. For example, during a Blood Pressure measurement, the device sends **Intermediate Cuff Pressure** notifications repeatedly as the cuff inflates, then a final **Blood Pressure Measurement**. If multiple measurement sessions overlap (or you have multiple devices), you need to pair notifications correctly.

The `DependencyPairingBuffer` helper buffers notifications and groups them using a caller-defined key (timestamp, sequence number, session ID, etc.).

### Real-World Scenario: Blood Pressure Monitor

```python
from datetime import datetime
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.stream import DependencyPairingBuffer
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()

bpm_uuid = "2A35"
icp_uuid = "2A36"

def group_by_timestamp(uuid: str, parsed) -> datetime:
    """Group notifications by their timestamp - same session = same timestamp."""
    if not parsed.parse_success or parsed.value is None:
        raise ValueError("Unable to derive grouping key: parse failed")

    # Both characteristics have optional timestamp fields
    if parsed.value.optional_fields.timestamp:
        return parsed.value.optional_fields.timestamp

    # Fallback: use current time or synthetic session tracking
    raise ValueError("Timestamp required for grouping")

def on_measurement_complete(results):
    """Called when both BPM and ICP arrive for the same timestamp."""
    bpm = results[bpm_uuid].value
    icp = results[icp_uuid].value

    print(f"Blood Pressure: {bpm.systolic}/{bpm.diastolic} {results[bpm_uuid].unit}")
    print(f"Max Cuff Pressure: {icp.current_cuff_pressure} {results[icp_uuid].unit}")

    # Store to database, update UI, etc.

buffer = DependencyPairingBuffer(
    translator=translator,
    required_uuids={bpm_uuid, icp_uuid},
    group_key=group_by_timestamp,
    on_pair=on_measurement_complete,
)

# In your notification handlers (notifications arrive in any order)
async with BleakClient(device_address) as client:
    await client.start_notify(bpm_uuid, lambda s, d: buffer.ingest(bpm_uuid, d))
    await client.start_notify(icp_uuid, lambda s, d: buffer.ingest(icp_uuid, d))

    # Buffer automatically pairs when both arrive with matching timestamps
    await asyncio.sleep(30)  # Wait for measurements
```

### Why This is Useful

**Without the buffer**: You'd manually track which ICP belongs to which BPM, especially when:

- Multiple measurement sessions overlap (nurse takes measurements from multiple patients)
- Notifications arrive out of order (common with BLE)
- Network delays cause interleaving

**With the buffer**: Automatically groups by timestamp, handles out-of-order arrival, and triggers your callback only when complete pairs arrive.

### Glucose Example (Sequence Number Pairing)

For Glucose monitors, pair by sequence number and validate in your callback:

```python
# SKIP: Stream example needs completion
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.stream import DependencyPairingBuffer
from bluetooth_sig.types.gatt_enums import CharacteristicName

translator = BluetoothSIGTranslator()

gm_uuid = "2A18"
gmc_uuid = "2A34"

def group_by_sequence(uuid: str, parsed) -> int:
    """Both measurement and context have sequence_number field."""
    if not parsed.parse_success or parsed.value is None:
        raise ValueError("Unable to derive grouping key: parse failed")
    return int(parsed.value.sequence_number)

def on_glucose_pair(results):
    gm = results[gm_uuid].value
    gmc = results[gmc_uuid].value

    # Validate sequence numbers match (per GLS v1.0.1 spec requirement)
    if gm.sequence_number != gmc.sequence_number:
        raise ValueError(
            f"Sequence mismatch: measurement={gm.sequence_number}, "
            f"context={gmc.sequence_number}"
        )

    print(f"Glucose: {gm.glucose_concentration} {results[gm_uuid].unit}")
    print(f"Carbs: {gmc.carbohydrate} g, Meal: {gmc.meal}")

buffer = DependencyPairingBuffer(
    translator=translator,
    required_uuids={gm_uuid, gmc_uuid},
    group_key=group_by_sequence,
    on_pair=on_glucose_pair,
)

# In notification handlers
buffer.ingest(gm_uuid, gm_bytes)
buffer.ingest(gmc_uuid, gmc_bytes)
```

### Notes

- **Generic**: Works with any paired characteristics - you define the grouping key
- **Validation**: Implement profile-specific validation (sequence matching, etc.) in your `on_pair` callback
- **Backend-agnostic**: Buffer only handles UUID strings and bytes; keep subscription management in your BLE client
- **Order-independent**: Notifications can arrive in any order; buffer waits for both before calling your callback

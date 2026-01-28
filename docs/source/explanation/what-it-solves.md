# What Problems It Solves

This library addresses specific pain points when working with Bluetooth Low Energy (BLE) devices and Bluetooth SIG specifications.

## Problem 1: Standards Interpretation Complexity

### The Challenge (Standards Interpretation)

Bluetooth SIG specifications are detailed technical documents that define how to encode/decode data for each characteristic. Implementing these correctly requires:

- Understanding binary data formats (uint8, sint16, IEEE-11073 SFLOAT)
- Handling byte order (little-endian, big-endian)
- Implementing conditional parsing based on flags
- Managing special values (0xFFFF = "unknown", NaN representations)
- Applying correct unit conversions

### Example: Temperature Characteristic (0x2A6E)

**Specification Requirements:**

- 2 bytes (sint16)
- Little-endian byte order
- Resolution: 0.01°C
- Special value: 0x8000 (-32768) = "Not Available"
- Valid range: -273.15°C to +327.67°C

**Manual Implementation:**

```python
def parse_temperature(data: bytes) -> float | None:
    if len(data) != 2:
        raise ValueError("Temperature requires 2 bytes")

    raw_value = int.from_bytes(data, byteorder="little", signed=True)

    if raw_value == -32768:  # 0x8000
        return None  # Not available

    if raw_value < -27315 or raw_value > 32767:
        raise ValueError("Temperature out of range")

    return raw_value * 0.01
```

**With bluetooth-sig:**

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()  # See quickstart guide for setup
data = bytearray([0x04, 0x01])  # 260 = 26.0°C (resolution is 0.01°C)
result = translator.parse_characteristic("2A6E", data)
# Handles all validation, conversion, and edge cases automatically
print(f"Temperature: {result}°C")  # Temperature: 2.6°C
```

### ✅ What We Solve (Standards Interpretation)

- **Automatic standards compliance** - All 70+ characteristics follow official specs
- **Unit conversion handling** - Correct scaling factors applied automatically
- **Edge case management** - Special values and sentinels handled correctly
- **Validation** - Input data validated before parsing
- **Type safety** - Structured data returned, not raw bytes

______________________________________________________________________

## Problem 2: UUID Management & Resolution

### The Challenge (UUID Management)

Bluetooth uses UUIDs to identify services and characteristics:

- **Short form**: `180F` (16-bit)
- **Long form**: `0000180f-0000-1000-8000-00805f9b34fb` (128-bit)

Both represent "Battery Service", but you need to:

1. Maintain a mapping of UUIDs to names
1. Handle both short and long forms
1. Support reverse lookup (name → UUID)
1. Keep up with Bluetooth SIG registry updates

### Manual Approach

```python
# Maintaining a UUID registry manually
SERVICE_UUIDS = {
    "180F": "Battery Service",
    "180A": "Device Information",
    "1809": "Health Thermometer",
    # ... hundreds more
}

CHARACTERISTIC_UUIDS = {
    "2A19": "Battery Level",
    "2A6E": "Temperature",
    "2A6F": "Humidity",
    # ... hundreds more
}


# Handling lookups
def resolve_by_name(uuid: str) -> str:
    # Short form?
    if len(uuid) == 4:
        return SERVICE_UUIDS.get(uuid) or CHARACTERISTIC_UUIDS.get(uuid)
    # Long form?
    elif len(uuid) == 36:
        short = uuid[4:8]
        return SERVICE_UUIDS.get(short) or CHARACTERISTIC_UUIDS.get(short)
    return "Unknown"
```

### ✅ What We Solve (UUID Management)

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Automatic UUID resolution (short or long form)
info = translator.get_sig_info_by_uuid("180F")
info = translator.get_sig_info_by_uuid(
    "0000180f-0000-1000-8000-00805f9b34fb"
)  # Same result

# Reverse lookup
battery_service = translator.get_sig_info_by_name("Battery Service")
print(battery_service.uuid)  # "180F"

# Get full information
print(info.name)  # "Battery Service"
print(info.uuid)  # "180F"
```

- **Official registry** - Based on Bluetooth SIG YAML specifications
- **Automatic updates** - Registry updates via submodule
- **Both directions** - UUID → name and name → UUID
- **Multiple formats** - Handles short and long UUID forms

______________________________________________________________________

## Problem 3: Type Safety & Data Validation

### The Challenge (Type Safety)

Raw BLE data is just bytes. Without proper typing:

- Errors caught at runtime, not compile time
- No IDE autocomplete
- Unclear what fields are available
- Easy to make mistakes with raw bytes

### Untyped Approach

```python
# SKIP: Intentional anti-pattern demonstration
# What does this return?
def parse_battery(data: bytes):
    return data[0]


# Is it a dict? A tuple? An int?
result = parse_battery(some_data)
# No type hints, no validation, no structure
```

### ✅ What We Solve (Type Safety)

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import CharacteristicName

# ============================================
# SIMULATED DATA - Replace with actual BLE read
# ============================================
SIMULATED_BATTERY_DATA = bytearray([85])  # Simulates 85% battery

translator = BluetoothSIGTranslator()
battery_uuid = translator.get_characteristic_uuid_by_name(
    CharacteristicName.BATTERY_LEVEL
)
result = translator.parse_characteristic(
    str(battery_uuid), SIMULATED_BATTERY_DATA
)

# For simple characteristics, result is the value directly
print(result)  # 85

# For complex characteristics, result is a typed dataclass
temp_data = bytearray([0x00, 0xE4, 0x00, 0x00, 0x00])  # Flags + temperature
temp_result = translator.parse_characteristic("2A1C", temp_data)
# Returns TemperatureMeasurementData with:
#   - temperature: float
#   - unit: celsius or fahrenheit
#   - timestamp: datetime | None
print(temp_result.temperature)  # Temperature value
```

- **Full type hints** - Every function and return type annotated
- **msgspec struct returns** - Structured data, not dictionaries
- **IDE support** - Autocomplete and inline documentation
- **Type checking** - Works with mypy, pyright, etc.

______________________________________________________________________

## Problem 4: Framework Lock-in

### The Challenge (Framework Lock-in)

Many BLE libraries combine connection management with data parsing, forcing you to:

- Use their specific API
- Learn their abstractions
- Be limited to their supported platforms
- Migrate everything if you want to change BLE libraries

### ✅ What We Solve (Framework Lock-in)

**Framework-agnostic design** - Parse data from any BLE library:

```python
# SKIP: Example requires BLE hardware access and external libraries
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Works with bleak
from bleak import BleakClient

async with BleakClient(address) as client:
    data = await client.read_gatt_char(uuid)
    result = translator.parse_characteristic(uuid, data)

# Works with simplepyble
from simplepyble import Peripheral

peripheral = Peripheral(adapter, address)
data = peripheral.read(service_uuid, char_uuid)
result = translator.parse_characteristic(char_uuid, data)

# Works with your custom BLE implementation
data = my_custom_ble_lib.read_characteristic(uuid)
result = translator.parse_characteristic(uuid, data)
```

- **Separation of concerns** - Parsing separate from connection
- **Library choice** - Use any BLE connection library you prefer
- **Platform flexibility** - Not tied to specific OS/platform
- **Testing** - Easy to mock BLE interactions

______________________________________________________________________

## Problem 5: Maintenance Burden

### The Challenge (Maintenance Burden)

Maintaining a custom BLE parsing implementation requires:

- Monitoring Bluetooth SIG specification updates
- Adding new characteristics as they're adopted
- Fixing bugs in parsing logic
- Keeping up with new data formats
- Ensuring backwards compatibility

### ✅ What We Solve (Maintenance Burden)

- **Centralized maintenance** - One library, many users
- **SIG registry updates** - New characteristics added as standards evolve
- **Community testing** - Bugs found and fixed by multiple users
- **Specification compliance** - Validated against official specs
- **Version management** - Clear versioning and changelog

______________________________________________________________________

## Problem 6: Complex Multi-Field Characteristics

### The Challenge (Multi-Field Characteristics)

Many characteristics have conditional fields based on flags:

**Temperature Measurement (0x2A1C):**

```text
Byte 0: Flags
  - Bit 0: Temperature unit (0=°C, 1=°F)
  - Bit 1: Timestamp present
  - Bit 2: Temperature Type present
Bytes 1-4: Temperature value (IEEE-11073 SFLOAT)
Bytes 5-11: Timestamp (if bit 1 set)
Byte 12: Temperature Type (if bit 2 set)
```

### Manual Implementation

```python
def parse_temp_measurement(data: bytes) -> dict:
    flags = data[0]
    offset = 1

    # Parse temperature (IEEE-11073 SFLOAT - complex format)
    temp_bytes = data[offset : offset + 4]
    temp_value = parse_ieee_sfloat(temp_bytes)  # Another complex function
    offset += 4

    # Conditional fields
    timestamp = None
    if flags & 0x02:
        timestamp = parse_timestamp(data[offset : offset + 7])
        offset += 7

    temp_type = None
    if flags & 0x04:
        temp_type = data[offset]

    return {
        "value": temp_value,
        "unit": "°F" if flags & 0x01 else "°C",
        "timestamp": timestamp,
        "type": temp_type,
    }
```

### ✅ What We Solve (Multi-Field Characteristics)

```python
from bluetooth_sig import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()
# Temperature Measurement requires at least 5 bytes (flags + FLOAT temperature)
data = bytearray([0x00, 0xFE, 0x00, 0x01, 0x00])  # Celsius, ~25.4°C
result = translator.parse_characteristic("2A1C", data)

# Returns TemperatureMeasurementData with all fields parsed
# Handles all flag combinations automatically
# Returns type-safe structured data
print(result.temperature)  # Temperature in appropriate units
```

______________________________________________________________________

## Summary: Key Problems Solved

| Problem | Manual Approach | bluetooth-sig Solution |
|---------|----------------|------------------------|
| Standards interpretation | Implement specs manually | Automatic, validated parsing |
| UUID management | Maintain mappings | Official registry with auto-resolution |
| Type safety | Raw bytes/dicts | Typed msgspec structs |
| Framework lock-in | Library-specific APIs | Works with any BLE library |
| Maintenance | You maintain | Community maintained |
| Complex parsing | Custom logic for each | Built-in for 70+ characteristics |
| Validation | Manual checks | Automatic validation |
| Documentation | Write your own | Comprehensive docs |

## What's Next?

- [What It Does NOT Solve](limitations.md) - Understand the boundaries
- [Quick Start](../tutorials/quickstart.md) - Start using the library
- [Usage Guide](../how-to/usage.md) - Detailed usage examples
- [API Reference](../api/index.md) - Complete API documentation

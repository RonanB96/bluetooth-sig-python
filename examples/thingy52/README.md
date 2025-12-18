# Nordic Thingy:52 Example

This example demonstrates the power and flexibility of the `bluetooth-sig-python` library by implementing custom characteristics and services for the **Nordic Thingy:52** IoT sensor kit.

## What This Example Demonstrates

### 1. **Custom Characteristic Implementation**
Shows how to create vendor-specific GATT characteristics that aren't in the Bluetooth SIG specification:

- ✅ **Type-safe parsing** with full type hints
- ✅ **msgspec.Struct** for structured data (not raw dicts/tuples)
- ✅ **Template reuse** to eliminate boilerplate
- ✅ **Precise error handling** with custom exceptions
- ✅ **Identical API** to SIG-standard characteristics

### 2. **Custom Service Organization**
Demonstrates how to group related characteristics into logical services:

- `ThingyEnvironmentService` - Temperature, pressure, humidity, gas, color sensors
- `ThingyUserInterfaceService` - Button state
- `ThingyMotionService` - Orientation, heading sensors

### 3. **Library Value Over Raw BLE**

**Without this library** (raw BLE with bleak/simplepyble):
```python
# Raw bytes - manual struct unpacking, no validation
raw_data = await client.read_gatt_char("EF680201-9B35-4933-9B10-52FFA9740042")
temp_int = struct.unpack('<b', raw_data[0:1])[0]  # Signed 8-bit
temp_dec = struct.unpack('<B', raw_data[1:2])[0]  # Unsigned 8-bit
temperature = temp_int + (temp_dec / 100.0)
# No validation, no error handling, manual UUID strings everywhere
```

**With this library**:
```python
# Type-safe, validated, self-documenting
from examples.thingy52 import ThingyTemperatureCharacteristic

char = ThingyTemperatureCharacteristic()
temperature = char.decode_value(raw_data)  # Returns float with validation
# Automatic range checking, clear error messages, no magic numbers
```

## File Structure

```
examples/thingy52/
├── __init__.py                      # Package exports
├── __main__.py                      # CLI entry point (python -m examples.thingy52)
├── README.md                        # This file
├── thingy52_characteristics.py      # Custom characteristic implementations
├── thingy52_services.py            # Custom service definitions
└── thingy52_example.py             # Full example with real device
```

## Characteristics Implemented

### Environment Service (0x0200)
| Characteristic | UUID | Type | Description |
|---------------|------|------|-------------|
| Temperature | 0x0201 | float | °C with 0.01° resolution |
| Pressure | 0x0202 | float | hPa (hectopascals) |
| Humidity | 0x0203 | int | Relative humidity 0-100% |
| Gas Sensor | 0x0204 | ThingyGasData | eCO2 (ppm) + TVOC (ppb) |
| Color Sensor | 0x0205 | ThingyColorData | RGBC values |

### User Interface Service (0x0300)
| Characteristic | UUID | Type | Description |
|---------------|------|------|-------------|
| Button | 0x0302 | bool | Button pressed/released |

### Motion Service (0x0400)
| Characteristic | UUID | Type | Description |
|---------------|------|------|-------------|
| Orientation | 0x0403 | str | Portrait/Landscape/Reverse |
| Heading | 0x0409 | float | Compass heading in degrees |

## Key Features Demonstrated

### 1. Template System
The library provides reusable templates that handle common encoding patterns:

```python
class ThingyHumidityCharacteristic(CustomBaseCharacteristic):
    _template = Uint8Template()  # Reusable 8-bit unsigned template

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
        if len(data) != 1:
            raise InsufficientDataError("Thingy Humidity", data, 1)

        humidity = self._template.decode_value(data)

        if humidity > 100:
            raise ValueRangeError("humidity", humidity, 0, 100)

        return humidity
```

**Benefits:**
- ✅ No manual `struct.unpack()` calls
- ✅ Automatic endianness handling
- ✅ Built-in bounds checking
- ✅ Type-safe encoding/decoding

### 2. Structured Data Returns
Using `msgspec.Struct` instead of raw dictionaries:

```python
class ThingyGasData(msgspec.Struct, frozen=True, kw_only=True):
    """Gas sensor data from Nordic Thingy:52.

    Attributes:
        eco2_ppm: eCO2 concentration in parts per million
        tvoc_ppb: TVOC concentration in parts per billion
    """
    eco2_ppm: int
    tvoc_ppb: int

# Usage:
char = ThingyGasCharacteristic()
result = char.decode_value(data)
print(result.eco2_ppm)  # IDE autocomplete works!
print(result.tvoc_ppb)  # Type-safe access
```

**Benefits:**
- ✅ IDE autocomplete and type checking
- ✅ Immutable data (frozen=True)
- ✅ Self-documenting with docstrings
- ✅ Zero runtime overhead (msgspec is fast)

### 3. Precise Error Handling
Custom exceptions with actionable error messages:

```python
# ❌ Generic error (raw BLE):
# struct.error: unpack requires a buffer of 2 bytes

# ✅ Actionable error (this library):
# InsufficientDataError: Thingy Temperature characteristic requires exactly 2 bytes, got 1 bytes
```

### 4. Service-Level Organization
Services provide logical grouping and health checking:

```python
from examples.thingy52 import ThingyEnvironmentService

# Service knows which characteristics it contains
service = ThingyEnvironmentService(discovery_data=discovery_data)

# Access service info
print(service.service_info.name)  # "Thingy Environment Service"
print(service.service_info.uuid)  # UUID with proper formatting

# Service validates characteristic presence
# health_status = service.check_health()  # Future: validate required chars
```

## Running the Example

### Prerequisites
```bash
# Install with example dependencies
pip install -e ".[examples]"

# Or install specific BLE backend
pip install bluepy  # For Linux with bluepy support
```

### CLI Usage
```bash
# Discover Thingy:52 devices
python -m examples.thingy52 --discover

# Read specific sensors
python -m examples.thingy52 --temperature --humidity --pressure

# Read all environmental sensors
python -m examples.thingy52 --all-environment

# Monitor button state
python -m examples.thingy52 --button

# Full sensor suite
python -m examples.thingy52 --all
```

### As a Library
```python
from examples.thingy52 import (
    ThingyTemperatureCharacteristic,
    ThingyHumidityCharacteristic,
    ThingyGasData,
)

# Create characteristic instances
temp_char = ThingyTemperatureCharacteristic()
humidity_char = ThingyHumidityCharacteristic()

# Decode BLE data
raw_temp = bytearray([0x18, 0x32])  # From BLE read
temperature = temp_char.decode_value(raw_temp)
print(f"Temperature: {temperature}°C")  # 24.50°C

# Encode data for writing
encoded = temp_char.encode_value(25.5)
# Send encoded data via BLE write
```

## Testing

Tests are located in `tests/integration/test_thingy52_characteristics.py`:

```bash
# Run Thingy:52 tests only
python -m pytest tests/integration/test_thingy52_characteristics.py -v

# Run with coverage
python -m pytest tests/integration/test_thingy52_characteristics.py --cov=examples.thingy52
```

## Why This Matters

### Comparison Table

| Feature | Raw BLE Code | With bluetooth-sig-python |
|---------|-------------|---------------------------|
| **Lines of code** | ~50 per characteristic | ~15 per characteristic |
| **Type safety** | ❌ None | ✅ Full typing |
| **Validation** | ❌ Manual | ✅ Automatic |
| **Error messages** | ❌ Cryptic | ✅ Actionable |
| **Documentation** | ❌ Comments | ✅ Docstrings + examples |
| **Testing** | ❌ Manual | ✅ Unit + integration tests |
| **Reusability** | ❌ Copy-paste | ✅ Importable classes |
| **Maintainability** | ❌ Low | ✅ High |

### Real-World Impact

**Before (manual parsing):**
- 🐛 Silent data corruption from incorrect byte offsets
- 🐛 Crashes from out-of-range values
- 🐛 Hours debugging "what format does this use?"
- 🐛 No IDE support (magic strings, magic numbers)

**After (using this library):**
- ✅ Impossible to misalign byte offsets (templates handle it)
- ✅ ValueRangeError with min/max in error message
- ✅ Self-documenting code with docstrings and type hints
- ✅ Full IDE autocomplete and type checking

## Extension Points

Want to add more Thingy:52 characteristics? Follow the pattern:

1. **Add to `thingy52_characteristics.py`**:
```python
class ThingyNewSensorCharacteristic(CustomBaseCharacteristic):
    r"""My new sensor characteristic.

    Examples:
        >>> char = ThingyNewSensorCharacteristic()
        >>> char.decode_value(bytearray([0x01, 0x02]))
        ...
    """
    _info = CharacteristicInfo(
        uuid=BluetoothUUID(NORDIC_UUID_BASE % 0xXXXX),
        name="Thingy New Sensor",
        unit="units",
        value_type=ValueType.FLOAT,
        properties=[],
    )

    _template = Uint16Template()

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        # Your parsing logic here
        ...
```

2. **Add to appropriate service** in `thingy52_services.py`
3. **Export from `__init__.py`**
4. **Add tests** in `tests/integration/test_thingy52_characteristics.py`
5. **Update this README**

## License

This example is part of the bluetooth-sig-python project. See main LICENSE file.

## References

- [Nordic Thingy:52 Product Page](https://www.nordicsemi.com/Products/Development-hardware/Nordic-Thingy-52)
- [Thingy:52 Firmware Documentation](https://nordicsemiconductor.github.io/Nordic-Thingy52-FW/documentation)
- [Bluetooth SIG GATT Specifications](https://www.bluetooth.com/specifications/specs/)

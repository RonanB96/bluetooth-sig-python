# Nordic Thingy:52 Example

This directory contains a complete port of the Nordic Thingy:52 BluePy example to the `bluetooth-sig-python` library, demonstrating best practices for handling vendor-specific BLE characteristics alongside SIG-standard characteristics.

## Files

- **`vendor_characteristics.py`**: Nordic Thingy:52 vendor characteristic adapters
  - 15 msgspec.Struct-based data models for Nordic's vendor UUIDs
  - Standalone decode functions with comprehensive validation
  - No hardcoded UUID strings - all defined as constants
  - Full documentation with examples

- **`thingy52_port.py`**: Demonstration script
  - Shows how to parse all Thingy:52 sensors
  - Demonstrates API consistency between SIG and vendor characteristics
  - Runs with mock data (no device required)
  - Educational output explaining the architecture

- **`../tests/integration/test_thingy52_port.py`**: Comprehensive tests
  - 66 tests covering all vendor characteristics
  - Each characteristic tests success + 2-3 failure modes
  - Tests for insufficient data, invalid values, boundary conditions

## Quick Start

Run the example with mock data (no device required):

```bash
cd examples
python thingy52_port.py --mock
```

## Supported Sensors

### SIG Standard Characteristics
- ✅ **Battery Level** (0x2A19) - Uses library's `BatteryLevelCharacteristic`

### Nordic Vendor Characteristics

#### Environment Service (EF680200)
- ✅ **Temperature** (EF680201) - Integer + decimal, °C
- ✅ **Pressure** (EF680202) - Integer + decimal, Pa/hPa
- ✅ **Humidity** (EF680203) - Percentage (0-100%)
- ✅ **Gas Sensor** (EF680204) - eCO2 (ppm) + TVOC (ppb)
- ✅ **Color Sensor** (EF680205) - RGBC values (0-65535)

#### User Interface Service (EF680300)
- ✅ **Button** (EF680302) - Pressed/Released state

#### Motion Service (EF680400)
- ✅ **Tap Detection** (EF680402) - Direction + count
- ✅ **Orientation** (EF680403) - Portrait/Landscape/Reverse
- ✅ **Quaternion** (EF680404) - 4x int32 fixed-point
- ✅ **Step Counter** (EF680405) - Steps + time
- ✅ **Raw Motion** (EF680406) - Accel + Gyro + Compass
- ✅ **Euler Angles** (EF680407) - Roll/Pitch/Yaw
- ✅ **Rotation Matrix** (EF680408) - 3x3 matrix
- ✅ **Heading** (EF680409) - Compass heading in degrees
- ✅ **Gravity Vector** (EF68040A) - 3D gravity vector (m/s²)

## Architecture Highlights

This implementation showcases several architectural improvements over the original BluePy implementation:

### 1. Type Safety with msgspec.Struct

All sensor data uses frozen msgspec.Struct models:

```python
class ThingyTemperatureData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 temperature measurement."""
    temperature_celsius: int
    temperature_decimal: int
```

### 2. Clean Separation of Concerns

Decoding logic is separated from data structures:

```python
def decode_thingy_temperature(data: bytes) -> ThingyTemperatureData:
    """Decode temperature with validation."""
    if len(data) != 2:
        raise ValueError(f"Temperature data must be 2 bytes, got {len(data)}")
    
    temp_int = struct.unpack("<b", data[0:1])[0]
    temp_dec = data[1]
    
    if temp_dec > 99:
        raise ValueError(f"Decimal must be 0-99, got {temp_dec}")
    
    return ThingyTemperatureData(
        temperature_celsius=temp_int,
        temperature_decimal=temp_dec
    )
```

### 3. No Hardcoded UUIDs

All UUIDs are defined as constants:

```python
# Nordic vendor UUID base
NORDIC_UUID_BASE: Final[str] = "EF68%04X-9B35-4933-9B10-52FFA9740042"

# Environment Service
TEMPERATURE_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0201
PRESSURE_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0202
```

### 4. Consistent API Patterns

Both SIG and vendor characteristics use similar patterns:

```python
# SIG characteristic - use translator
battery_result = translator.parse_characteristic("2A19", data, None)
print(f"Battery: {battery_result.value}%")

# Vendor characteristic - use decode function
temp_data = decode_thingy_temperature(data)
print(f"Temperature: {temp_data.temperature_celsius}.{temp_data.temperature_decimal}°C")
```

### 5. Comprehensive Error Handling

All decoders validate input and raise clear errors:

```python
# Length validation
if len(data) != expected_length:
    raise ValueError(f"Data must be {expected_length} bytes, got {len(data)}")

# Range validation
if value > max_value:
    raise ValueError(f"Value must be 0-{max_value}, got {value}")
```

### 6. Extensive Testing

Each characteristic has comprehensive tests:

```python
class TestThingyTemperature:
    def test_decode_valid_temperature(self) -> None:
        """Test success case."""
        
    def test_decode_insufficient_data(self) -> None:
        """Test failure: too short."""
        
    def test_decode_invalid_decimal(self) -> None:
        """Test failure: out of range."""
```

## Integration with BLE Libraries

The vendor characteristics are framework-agnostic and work with any BLE library:

### With bleak

```python
from bleak import BleakClient
from bluetooth_sig import BluetoothSIGTranslator
from examples.vendor_characteristics import decode_thingy_temperature, TEMPERATURE_CHAR_UUID

translator = BluetoothSIGTranslator()

async with BleakClient(address) as client:
    # SIG characteristic
    battery_data = await client.read_gatt_char("2A19")
    battery_result = translator.parse_characteristic("2A19", battery_data, None)
    print(f"Battery: {battery_result.value}%")
    
    # Vendor characteristic
    temp_data = await client.read_gatt_char(TEMPERATURE_CHAR_UUID)
    temp_result = decode_thingy_temperature(temp_data)
    temp_celsius = temp_result.temperature_celsius + (temp_result.temperature_decimal / 100.0)
    print(f"Temperature: {temp_celsius:.2f}°C")
```

### With simplepyble

```python
from simplepyble import Peripheral
from bluetooth_sig import BluetoothSIGTranslator
from examples.vendor_characteristics import decode_thingy_humidity, HUMIDITY_CHAR_UUID

translator = BluetoothSIGTranslator()

# SIG characteristic
battery_data = peripheral.read("180F", "2A19")
battery_result = translator.parse_characteristic("2A19", battery_data, None)

# Vendor characteristic
humidity_data = peripheral.read("EF680200-9B35-4933-9B10-52FFA9740042", HUMIDITY_CHAR_UUID)
humidity_result = decode_thingy_humidity(humidity_data)
print(f"Humidity: {humidity_result.humidity_percent}%")
```

## Testing

Run all Thingy:52 tests:

```bash
python -m pytest tests/integration/test_thingy52_port.py -v
```

Run specific test class:

```bash
python -m pytest tests/integration/test_thingy52_port.py::TestThingyTemperature -v
```

Run with coverage:

```bash
python -m pytest tests/integration/test_thingy52_port.py --cov=examples.vendor_characteristics
```

## Fixed-Point Conversion Reference

Several characteristics use fixed-point encoding:

| Characteristic | Format | Scale Factor | Conversion |
|----------------|--------|--------------|------------|
| Temperature | int8 + uint8 | 0.01°C | `integer + (decimal / 100.0)` |
| Pressure | uint32 + uint8 | 0.01 Pa | `integer + (decimal / 100.0)` |
| Quaternion | int32 x4 | 2^30 | `value / 1073741824` |
| Euler Angles | int32 x3 | 2^16 | `value / 65536` (degrees) |
| Rotation Matrix | int16 x9 | 2^15 | `value / 32768` |
| Heading | int32 | 2^16 | `value / 65536` (degrees) |
| Gravity Vector | float32 x3 | Direct | No conversion needed |

## References

### Official Documentation
- [Nordic Thingy:52 Firmware Documentation](https://nordicsemiconductor.github.io/Nordic-Thingy52-FW/documentation)
- [Bluetooth SIG Assigned Numbers](https://www.bluetooth.com/specifications/assigned-numbers/)

### Source Code
- [Original BluePy Thingy:52 Implementation](https://github.com/IanHarvey/bluepy/blob/master/bluepy/thingy52.py)
- [bluetooth-sig-python Library](https://github.com/RonanB96/bluetooth-sig-python)

### Product Information
- [Nordic Thingy:52 Product Page](https://www.nordicsemi.com/Products/Development-hardware/Nordic-Thingy-52)
- [Thingy:52 User Guide](https://infocenter.nordicsemi.com/topic/ug_thingy52/UG/thingy52/intro/frontpage.html)

## Comparison with Original Implementation

| Aspect | Original BluePy | This Implementation |
|--------|----------------|---------------------|
| Data Models | Raw bytes/tuples | msgspec.Struct (frozen, typed) |
| Validation | Minimal | Comprehensive (length, range) |
| Error Messages | Generic or missing | Specific, actionable |
| UUID Management | Scattered string literals | Centralized constants |
| Testing | None in example | 66 comprehensive tests |
| Type Safety | None | Full mypy compliance |
| Documentation | Basic docstrings | Full docs with examples |
| Parsing Logic | Inline hex string manipulation | Clean struct.unpack |
| Framework Coupling | Tight (bluepy) | None (pure parsing) |

## Contributing

When adding support for new vendor characteristics:

1. **Define UUIDs** as constants at the top of `vendor_characteristics.py`
2. **Create msgspec.Struct** with `frozen=True` for the data model
3. **Write decode function** with comprehensive validation
4. **Add docstring** with examples and spec references
5. **Write tests** covering success + 2-3 failure modes
6. **Update this README** with the new characteristic

Follow the existing patterns to maintain consistency across all characteristics.

## License

This example is part of the bluetooth-sig-python library and is licensed under the MIT License.

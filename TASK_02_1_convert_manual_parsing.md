# Task 2.1: Convert Manual Parsing Characteristics (Batch 1)

## Priority: Phase 2 - After Phase 1 complete

## Parallelization: Can run in parallel with other 2.x tasks after Phase 1

## Objective

Convert 12 characteristics that still use manual `int.from_bytes` and `struct.unpack` calls to use the standardized utils functions and validation attributes.

## Files to Convert

1. `src/bluetooth_sig/gatt/characteristics/generic_access.py`
2. `src/bluetooth_sig/gatt/characteristics/temperature_measurement.py`
3. `src/bluetooth_sig/gatt/characteristics/weight_measurement.py`
4. `src/bluetooth_sig/gatt/characteristics/glucose_measurement_context.py`
5. `src/bluetooth_sig/gatt/characteristics/pulse_oximetry_measurement.py`
6. `src/bluetooth_sig/gatt/characteristics/blood_pressure_measurement.py`
7. `src/bluetooth_sig/gatt/characteristics/heart_rate_measurement.py`
8. `src/bluetooth_sig/gatt/characteristics/glucose_measurement.py`
9. `src/bluetooth_sig/gatt/characteristics/weight_scale_feature.py`
10. `src/bluetooth_sig/gatt/characteristics/body_composition_feature.py`
11. `src/bluetooth_sig/gatt/characteristics/body_composition_measurement.py`
12. `src/bluetooth_sig/gatt/characteristics/glucose_feature.py`

## Implementation Pattern

For each file, apply this standardized conversion:

### 1. Update Imports

Replace manual parsing imports with utils:

```python
# Remove these imports:
import struct

# Add these imports:
from .utils import DataParser, IEEE11073Parser, DataValidator
```

### 2. Add Validation Attributes

Add appropriate class-level validation:

```python
class ExampleCharacteristic(BaseCharacteristic):
    # Add validation attributes based on data format
    expected_length = 2  # or min_length/max_length for variable
    min_value = 0
    max_value = 65535
    expected_type = int  # or float
```

### 3. Replace Manual Parsing

Convert all manual parsing patterns using simplified API:

```python
# Replace this pattern:
raw_value = int.from_bytes(data[0:2], byteorder="little", signed=False)

# With this:
raw_value = DataParser.parse_int16(data, 0, signed=False)

# Replace this pattern:
value = struct.unpack("<H", data[0:2])[0]

# With this:
value = DataParser.parse_int16(data, 0, signed=False)

# Replace this pattern:
speed_raw = struct.unpack("<H", data[1:3])[0]

# With this:
speed_raw = DataParser.parse_int16(data, 1, signed=False)

# Replace this pattern:
systolic_raw, diastolic_raw, map_raw = struct.unpack("<HHH", data[1:7])

# With this:
systolic_raw = DataParser.parse_int16(data, 1, signed=False)
diastolic_raw = DataParser.parse_int16(data, 3, signed=False)
map_raw = DataParser.parse_int16(data, 5, signed=False)

# Replace this pattern:
temperature = int.from_bytes(data[1:3], byteorder="little", signed=True) * 0.01

# With this:
temperature = DataParser.parse_int16(data, 1, signed=True) * 0.01

# Replace this pattern:
flags = data[0]

# With this:
flags = DataParser.parse_int8(data, 0, signed=False)
```

### 4. Remove Manual Length Validation

Remove manual length checks (handled by BaseCharacteristic):

```python
# Remove these patterns:
if len(data) < 2:
    raise ValueError("Insufficient data")

# BaseCharacteristic handles this automatically with expected_length attribute
```

### 5. Use IEEE 11073 Parser for Medical Characteristics

For characteristics using IEEE 11073 format:

```python
# Replace manual IEEE parsing:
def decode_value(self, data: bytearray) -> float:
    # Manual IEEE 11073 parsing code...

# With utils:
def decode_value(self, data: bytearray) -> float:
    return IEEE11073Parser.parse_sfloat(data, 0)
```

## Specific File Conversions

### temperature_measurement.py

- Use `IEEE11073Parser.parse_sfloat()` for temperature value
- Add `allow_variable_length = True` (has optional timestamp)
- Use `DataParser.parse_int8()` for flags

### weight_measurement.py

- Use `IEEE11073Parser.parse_sfloat()` for weight value
- Add `min_length = 3, max_length = 13` for variable data
- Use `DataParser.parse_int16/int8()` for all integer fields

### glucose_measurement.py

- Use `IEEE11073Parser.parse_sfloat()` for glucose concentration
- Use `DataParser.parse_int16()` for sequence number
- Handle variable length with proper attributes

### heart_rate_measurement.py

- Use `DataParser.parse_int8/16()` based on format flags
- Add `allow_variable_length = True`
- Use `BitFieldUtils` for flag parsing

## Success Criteria

- All `int.from_bytes` calls replaced with `DataParser` methods
- All `struct.unpack` calls replaced with appropriate utils
- All manual length validation removed
- Validation attributes properly set for each characteristic
- All characteristics use appropriate utils imports
- Encoding methods also updated to use utils
- All tests still pass for each converted characteristic

## Dependencies

- **REQUIRES**: All Phase 1 tasks (1.1, 1.2, 1.3) must complete first
- **PARALLEL**: Can run with Tasks 2.2, 2.3, 2.4, 2.5, 2.6, 2.7
- **ENABLES**: Final quality assurance (Phase 3)

## Testing Strategy

Test each file individually during conversion:

```bash
# Test specific characteristic
python -c "from src.bluetooth_sig.gatt.characteristics.temperature_measurement import TemperatureMeasurementCharacteristic; char = TemperatureMeasurementCharacteristic(); print('✅ Import successful')"

# Test parsing with sample data
python -m pytest tests/test_temperature_measurement.py -v

# Test all converted characteristics
python -m pytest tests/ -k "temperature_measurement or weight_measurement or glucose" -v
```

## Conversion Checklist

For each file:

- [ ] Remove `import struct`
- [ ] Add `from .utils import DataParser, IEEE11073Parser`
- [ ] Add validation attributes to class
- [ ] Replace all `int.from_bytes()` calls
- [ ] Replace all `struct.unpack()` calls
- [ ] Remove manual length validation
- [ ] Update `encode_value()` method if present
- [ ] Test characteristic still works
- [ ] Verify all tests pass

## Expected Code Reduction

- Remove approximately 150-200 lines of manual parsing code
- Eliminate 50+ manual length validation checks
- Standardize error messages across all characteristics
- Reduce complexity in each `decode_value()` method by 30-50%

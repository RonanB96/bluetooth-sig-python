# Task 2.3: Replace Hardcoded Range Validation

## Priority: Phase 2 - After Phase 1 complete

## Parallelization: Can run in parallel with other 2.x tasks

## Objective

Replace hardcoded range validation in 6 identified characteristics with declarative min_value/max_value attributes handled by BaseCharacteristic.

## Files to Convert

1. `src/bluetooth_sig/gatt/characteristics/supported_power_range.py`
2. `src/bluetooth_sig/gatt/characteristics/cycling_power_control_point.py`
3. `src/bluetooth_sig/gatt/characteristics/rsc_measurement.py`
4. `src/bluetooth_sig/gatt/characteristics/cycling_power_measurement.py`
5. `src/bluetooth_sig/gatt/characteristics/weight_measurement.py`
6. `src/bluetooth_sig/gatt/characteristics/glucose_measurement.py`

## Implementation Pattern

### 1. Identify Hardcoded Range Validation

Find and remove these patterns:

```python
# Pattern 1: Direct value comparison
if value > 65535:
    raise ValueError("Value exceeds uint16 range")

# Pattern 2: Range checking with constants
if value < 0 or value > MAX_POWER:
    raise ValueError("Power value out of range")

# Pattern 3: Type-specific range validation
if not 0 <= power_value <= 65534:
    raise ValueError("Power must be 0-65534 watts")

# Pattern 4: Multiple condition checks
if value < MIN_VALUE:
    raise ValueError("Value too small")
if value > MAX_VALUE:
    raise ValueError("Value too large")
```

### 2. Replace with Validation Attributes

Add appropriate class-level validation:

```python
class ExampleCharacteristic(BaseCharacteristic):
    # Replace hardcoded checks with declarative attributes
    min_value = 0
    max_value = 65535
    expected_type = int
```

## File-Specific Conversions

### supported_power_range.py

**Current pattern:**
```python
def decode_value(self, data: bytearray) -> dict:
    min_power = DataParser.parse_sint16(data, 0)
    max_power = DataParser.parse_sint16(data, 2)

    if min_power < -32768 or min_power > 32767:
        raise ValueError("Minimum power exceeds sint16 range")
    if max_power < -32768 or max_power > 32767:
        raise ValueError("Maximum power exceeds sint16 range")
```

**Convert to:**
```python
class SupportedPowerRangeCharacteristic(BaseCharacteristic):
    expected_length = 4
    # Remove hardcoded validation - sint16 range automatically validated
    # by DataParser.parse_sint16()

    def decode_value(self, data: bytearray) -> dict:
        min_power = DataParser.parse_int16(data, 0, signed=True)
        max_power = DataParser.parse_int16(data, 2, signed=True)

        # Additional business logic validation (not range checking)
        if min_power > max_power:
            raise ValueError("Minimum power cannot exceed maximum power")

        return {"min_power": min_power, "max_power": max_power}
```

### cycling_power_measurement.py

**Current pattern:**
```python
def decode_value(self, data: bytearray) -> dict:
    power = DataParser.parse_uint16(data, 2)

    if power > 65534:  # Reserve 65535 for invalid
        raise ValueError("Power value exceeds valid range")
```

**Convert to:**
```python
class CyclingPowerMeasurementCharacteristic(BaseCharacteristic):
    min_length = 4
    allow_variable_length = True
    min_value = 0
    max_value = 65534  # Reserve 65535 for invalid

    def decode_value(self, data: bytearray) -> dict:
        power = DataParser.parse_int16(data, 2, signed=False)
        # Range validation handled automatically

        if power == 65535:
            power = None  # Invalid value indicator

        return {"power": power, ...}
```

### weight_measurement.py

**Current pattern:**
```python
def decode_value(self, data: bytearray) -> dict:
    weight = IEEE11073Parser.parse_sfloat(data, 1)

    if weight < 0:
        raise ValueError("Weight cannot be negative")
    if weight > 500:  # Reasonable maximum
        raise ValueError("Weight exceeds reasonable maximum")
```

**Convert to:**
```python
class WeightMeasurementCharacteristic(BaseCharacteristic):
    min_length = 3
    max_length = 13
    allow_variable_length = True
    min_value = 0.0
    max_value = 500.0  # Reasonable maximum weight in kg
    expected_type = float

    def decode_value(self, data: bytearray) -> dict:
        weight = IEEE11073Parser.parse_sfloat(data, 1)
        # Range validation handled automatically

        return {"weight": weight, ...}
```

### glucose_measurement.py

**Current pattern:**
```python
def decode_value(self, data: bytearray) -> dict:
    concentration = IEEE11073Parser.parse_sfloat(data, 3)

    if concentration < 0:
        raise ValueError("Glucose concentration cannot be negative")
    if concentration > 1000:  # mg/dL reasonable maximum
        raise ValueError("Glucose concentration exceeds reasonable range")
```

**Convert to:**
```python
class GlucoseMeasurementCharacteristic(BaseCharacteristic):
    min_length = 10
    allow_variable_length = True
    min_value = 0.0
    max_value = 1000.0  # mg/dL reasonable maximum
    expected_type = float

    def decode_value(self, data: bytearray) -> dict:
        concentration = IEEE11073Parser.parse_sfloat(data, 3)
        # Range validation handled automatically

        return {"concentration": concentration, ...}
```

### rsc_measurement.py (Running Speed and Cadence)

**Current pattern:**
```python
def decode_value(self, data: bytearray) -> dict:
    speed = DataParser.parse_uint16(data, 0)  # 0.1 m/s resolution
    cadence = DataParser.parse_uint8(data, 2)  # steps/min

    if speed > 6553:  # 655.3 m/s unreasonable
        raise ValueError("Speed value unreasonably high")
    if cadence > 250:  # 250 steps/min maximum reasonable
        raise ValueError("Cadence value unreasonably high")
```

**Convert to:**
```python
class RSCMeasurementCharacteristic(BaseCharacteristic):
    min_length = 4
    allow_variable_length = True

    def decode_value(self, data: bytearray) -> dict:
        raw_speed = DataParser.parse_int16(data, 0, signed=False)
        cadence = DataParser.parse_int8(data, 2, signed=False)

        # Convert speed to m/s with validation
        speed = raw_speed * 0.1
        if speed > 655.3:  # Reasonable maximum
            raise ValueError("Speed value unreasonably high")
        if cadence > 250:
            raise ValueError("Cadence value unreasonably high")

        return {"speed": speed, "cadence": cadence, ...}
```

### cycling_power_control_point.py

**Current pattern:**
```python
def decode_value(self, data: bytearray) -> dict:
    opcode = DataParser.parse_uint8(data, 0)

    if opcode < 1 or opcode > 7:
        raise ValueError("Invalid opcode value")
```

**Convert to:**
```python
class CyclingPowerControlPointCharacteristic(BaseCharacteristic):
    min_length = 1
    allow_variable_length = True
    min_value = 1
    max_value = 7

    def decode_value(self, data: bytearray) -> dict:
        opcode = DataParser.parse_int8(data, 0, signed=False)
        # Range validation handled automatically

        return self._parse_command(opcode, data[1:])
```

## Success Criteria

- All hardcoded range validation patterns removed
- Validation attributes properly set for each characteristic
- Range validation now handled by BaseCharacteristic
- Error messages are consistent and descriptive
- Business logic validation (non-range) preserved where appropriate
- All tests continue to pass

## Dependencies

- **REQUIRES**: Task 1.1 (BaseCharacteristic validation) must complete first
- **PARALLEL**: Can run with all other 2.x tasks
- **ENABLES**: Phase 3 quality assurance

## Testing

```bash
# Test range validation is working
python -c "
from src.bluetooth_sig.gatt.characteristics.weight_measurement import WeightMeasurementCharacteristic
char = WeightMeasurementCharacteristic()
try:
    char._validate_range(-5.0)  # Should fail
except ValueError as e:
    print('✅ Range validation working:', e)
"

# Test all converted characteristics
python -m pytest tests/test_weight_measurement.py -v
python -m pytest tests/test_glucose_measurement.py -v
python -m pytest tests/test_cycling_power_measurement.py -v
```

## Expected Impact

- Remove 20-30 hardcoded validation lines
- Standardize range validation across characteristics
- Enable automatic range testing
- Improve error message consistency
- Reduce characteristic implementation complexity

# Task 2.2: Standardize All Length Validation

## Priority: Phase 2 - After Phase 1 complete

## Parallelization: Can run in parallel with other 2.x tasks

## Objective

Remove all manual length validation patterns from ALL 138 characteristic files and replace with declarative validation attributes handled by BaseCharacteristic.

## Scope

This task applies to ALL characteristic files in `src/bluetooth_sig/gatt/characteristics/` directory (138 files total).

## Implementation Pattern

### 1. Identify Manual Length Validation Patterns

Find and remove these patterns in ALL characteristics:

```python
# Pattern 1: Simple length check
if len(data) < 2:
    raise ValueError("Insufficient data")

# Pattern 2: Range length check
if len(data) < 1 or len(data) > 10:
    raise ValueError("Invalid data length")

# Pattern 3: Exact length check
if len(data) != 4:
    raise ValueError("Expected 4 bytes")

# Pattern 4: Complex conditional checks
if not data or len(data) < self.min_bytes:
    raise ValueError("Data too short")
```

### 2. Replace with Validation Attributes

For each characteristic, add appropriate class attributes:

```python
class ExampleCharacteristic(BaseCharacteristic):
    # For fixed-length characteristics:
    expected_length = 2

    # For variable-length with minimum:
    min_length = 1
    max_length = 20
    allow_variable_length = True

    # For characteristics that can be any length:
    allow_variable_length = True
```

### 3. Common Length Patterns by Characteristic Type

#### Simple sensor values (most common):
```python
expected_length = 2  # uint16 values
expected_length = 1  # uint8 values
expected_length = 4  # uint32 values
```

#### Medical measurements with optional data:
```python
min_length = 3        # Base measurement
max_length = 13       # With all optional fields
allow_variable_length = True
```

#### String characteristics:
```python
min_length = 0        # Can be empty
max_length = 248      # BLE characteristic max
allow_variable_length = True
```

#### Complex structured data:
```python
min_length = 7        # Minimum required fields
allow_variable_length = True  # Additional optional data
```

## File-by-File Conversion Strategy

### Batch A: Simple Fixed-Length (40+ files)
Characteristics with single value (uint8, uint16, uint32):
- `battery_level.py` → `expected_length = 1`
- `temperature.py` → `expected_length = 2`
- `humidity.py` → `expected_length = 2`
- `pressure.py` → `expected_length = 4`
- All concentration characteristics → `expected_length = 2`
- All voltage/current characteristics → `expected_length = 2`

### Batch B: Variable Medical Data (15+ files)
Medical characteristics with optional timestamps/flags:
- `glucose_measurement.py` → `min_length = 10, allow_variable_length = True`
- `blood_pressure_measurement.py` → `min_length = 7, allow_variable_length = True`
- `weight_measurement.py` → `min_length = 3, max_length = 13, allow_variable_length = True`
- `heart_rate_measurement.py` → `min_length = 2, allow_variable_length = True`

### Batch C: String/Complex Data (20+ files)
Characteristics with string or complex variable data:
- `device_name.py` → `max_length = 248, allow_variable_length = True`
- `manufacturer_name.py` → `max_length = 248, allow_variable_length = True`
- `software_revision.py` → `max_length = 248, allow_variable_length = True`

### Batch D: Control Points (10+ files)
Command/control characteristics with variable commands:
- `cycling_power_control_point.py` → `min_length = 1, allow_variable_length = True`
- `glucose_control_point.py` → `min_length = 1, allow_variable_length = True`

### Batch E: Remaining Characteristics (50+ files)
All other characteristics not covered in A-D.

## Standard Validation Attribute Patterns

```python
# Fixed-length patterns
expected_length = 1    # uint8, percentage, flags
expected_length = 2    # uint16, most sensor values
expected_length = 4    # uint32, timestamps
expected_length = 6    # 3D vectors (3x uint16)
expected_length = 8    # 64-bit values, some complex

# Variable-length patterns
min_length = 1, allow_variable_length = True           # Commands
min_length = 2, max_length = 20, allow_variable_length = True  # Measurements
max_length = 248, allow_variable_length = True         # Strings
allow_variable_length = True                           # Any length
```

## Systematic Conversion Process

### Step 1: Scan Each File
```bash
# Find all length validation patterns
grep -n "len(data)" src/bluetooth_sig/gatt/characteristics/*.py
```

### Step 2: Categorize by Pattern
- Identify whether fixed or variable length
- Determine minimum/maximum requirements
- Check for optional data fields

### Step 3: Apply Attributes
- Add appropriate validation attributes
- Remove ALL manual length checks
- Update docstrings if needed

### Step 4: Verify Conversion
- Ensure no manual length validation remains
- Test characteristic still parses correctly
- Verify error messages are appropriate

## Success Criteria

- Zero manual length validation patterns remain in any characteristic
- All characteristics have appropriate length validation attributes
- Error messages are consistent and descriptive
- All existing tests continue to pass
- New validation provides same or better error detection

## Dependencies

- **REQUIRES**: Task 1.1 (BaseCharacteristic validation) must complete first
- **PARALLEL**: Can run with all other 2.x tasks
- **ENABLES**: Phase 3 quality assurance

## Testing

```bash
# Verify no manual length validation remains
grep -r "len(data)" src/bluetooth_sig/gatt/characteristics/ --exclude="base.py" --exclude="utils.py" | wc -l
# Should return 0

# Test validation attributes work
python -m pytest tests/ -v

# Test specific error cases
python -c "
char = SomeCharacteristic()
try:
    char.parse_value(b'x')  # Too short
except ValueError as e:
    print('✅ Length validation working:', e)
"
```

## Expected Impact

- Remove 200+ manual length validation lines
- Standardize all error messages
- Eliminate 50+ different validation patterns
- Reduce cognitive load in characteristic implementations
- Enable automatic validation testing

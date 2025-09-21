# Task 2.4: Convert Concentration Characteristics

## Priority: Phase 2 - After Phase 1 complete

## Parallelization: Can run in parallel with other 2.x tasks

## Objective

Standardize all 8 concentration characteristics to use the ConcentrationCharacteristic template and eliminate duplicate parsing logic.

## Files to Convert

1. `src/bluetooth_sig/gatt/characteristics/co_concentration.py`
2. `src/bluetooth_sig/gatt/characteristics/co2_concentration.py`
3. `src/bluetooth_sig/gatt/characteristics/methane_concentration.py`
4. `src/bluetooth_sig/gatt/characteristics/no2_concentration.py`
5. `src/bluetooth_sig/gatt/characteristics/pm1_concentration.py`
6. `src/bluetooth_sig/gatt/characteristics/pm25_concentration.py`
7. `src/bluetooth_sig/gatt/characteristics/pm10_concentration.py`
8. `src/bluetooth_sig/gatt/characteristics/tvoc_concentration.py`

## Implementation Pattern

### 1. Current Duplicate Pattern

All concentration characteristics currently follow this duplicate pattern:

```python
class COConcentrationCharacteristic(BaseCharacteristic):
    def decode_value(self, data: bytearray) -> float:
        if len(data) < 2:
            raise ValueError("CO concentration data must be at least 2 bytes")

        raw_value = int.from_bytes(data[:2], byteorder="little", signed=False)
        concentration = raw_value * 1.0  # 1 ppm resolution

        if concentration < 0:
            raise ValueError("CO concentration cannot be negative")
        if concentration > 65535:
            raise ValueError("CO concentration exceeds maximum range")

        return concentration

    @property
    def unit(self) -> str:
        return "ppm"
```

### 2. Convert to Template Inheritance

Replace with standardized template usage:

```python
from .templates import ConcentrationCharacteristic

class COConcentrationCharacteristic(ConcentrationCharacteristic):
    """Carbon monoxide concentration measurement."""

    resolution = 1.0  # 1 ppm resolution
    concentration_unit = "ppm"
    # All parsing, validation, and encoding handled by template
```

## Specific Conversions

### co_concentration.py

```python
from __future__ import annotations
from .templates import ConcentrationCharacteristic

class COConcentrationCharacteristic(ConcentrationCharacteristic):
    """Carbon monoxide concentration measurement per SIG spec."""

    resolution = 1.0
    concentration_unit = "ppm"
```

### co2_concentration.py

```python
from __future__ import annotations
from .templates import ConcentrationCharacteristic

class CO2ConcentrationCharacteristic(ConcentrationCharacteristic):
    """Carbon dioxide concentration measurement per SIG spec."""

    resolution = 1.0
    concentration_unit = "ppm"
```

### methane_concentration.py

```python
from __future__ import annotations
from .templates import ConcentrationCharacteristic

class MethaneConcentrationCharacteristic(ConcentrationCharacteristic):
    """Methane concentration measurement per SIG spec."""

    resolution = 1.0
    concentration_unit = "ppm"
```

### no2_concentration.py

```python
from __future__ import annotations
from .templates import ConcentrationCharacteristic

class NO2ConcentrationCharacteristic(ConcentrationCharacteristic):
    """Nitrogen dioxide concentration measurement per SIG spec."""

    resolution = 1.0
    concentration_unit = "ppm"
```

### pm1_concentration.py

```python
from __future__ import annotations
from .templates import ConcentrationCharacteristic

class PM1ConcentrationCharacteristic(ConcentrationCharacteristic):
    """PM1 particulate matter concentration measurement per SIG spec."""

    resolution = 1.0
    concentration_unit = "μg/m³"
```

### pm25_concentration.py

```python
from __future__ import annotations
from .templates import ConcentrationCharacteristic

class PM25ConcentrationCharacteristic(ConcentrationCharacteristic):
    """PM2.5 particulate matter concentration measurement per SIG spec."""

    resolution = 1.0
    concentration_unit = "μg/m³"
```

### pm10_concentration.py

```python
from __future__ import annotations
from .templates import ConcentrationCharacteristic

class PM10ConcentrationCharacteristic(ConcentrationCharacteristic):
    """PM10 particulate matter concentration measurement per SIG spec."""

    resolution = 1.0
    concentration_unit = "μg/m³"
```

### tvoc_concentration.py

```python
from __future__ import annotations
from .templates import ConcentrationCharacteristic

class TVOCConcentrationCharacteristic(ConcentrationCharacteristic):
    """Total volatile organic compounds concentration measurement per SIG spec."""

    resolution = 1.0
    concentration_unit = "ppb"  # Parts per billion for TVOC
```

## Conversion Process

### Step 1: Remove All Manual Implementation

For each file, remove:
- Manual length validation (`if len(data) < 2:`)
- Manual parsing (`int.from_bytes(data[:2], ...)`)
- Manual range validation (`if concentration > 65535:`)
- Manual unit property implementation
- Manual encode_value implementation

### Step 2: Add Template Import

```python
from .templates import ConcentrationCharacteristic
```

### Step 3: Update Class Inheritance

```python
class XConcentrationCharacteristic(ConcentrationCharacteristic):
```

### Step 4: Set Resolution and Unit

Add only the specific resolution and unit for each characteristic.

### Step 5: Remove All Methods

Remove `decode_value`, `encode_value`, and `unit` property - all handled by template.

## Resolution and Unit Reference

| Characteristic | Resolution | Unit | Notes |
|---------------|------------|------|-------|
| CO | 1.0 | ppm | Carbon monoxide |
| CO2 | 1.0 | ppm | Carbon dioxide |
| Methane | 1.0 | ppm | Methane gas |
| NO2 | 1.0 | ppm | Nitrogen dioxide |
| PM1 | 1.0 | μg/m³ | Particulate matter 1μm |
| PM2.5 | 1.0 | μg/m³ | Particulate matter 2.5μm |
| PM10 | 1.0 | μg/m³ | Particulate matter 10μm |
| TVOC | 1.0 | ppb | Total volatile organic compounds |

## Success Criteria

- All 8 concentration characteristics inherit from ConcentrationCharacteristic
- No duplicate parsing logic remains
- Each characteristic only specifies resolution and unit
- All manual validation removed
- File sizes reduced by 80-90%
- All tests continue to pass
- Consistent behavior across all concentration types

## Dependencies

- **REQUIRES**: Task 1.2 (ConcentrationCharacteristic template) must complete first
- **PARALLEL**: Can run with other 2.x tasks after templates available
- **ENABLES**: Phase 3 quality assurance

## Testing

```bash
# Test template inheritance works
python -c "
from src.bluetooth_sig.gatt.characteristics.co_concentration import COConcentrationCharacteristic
char = COConcentrationCharacteristic()
print('Resolution:', char.resolution)
print('Unit:', char.unit)
print('✅ Template inheritance working')
"

# Test parsing functionality
python -c "
from src.bluetooth_sig.gatt.characteristics.co_concentration import COConcentrationCharacteristic
char = COConcentrationCharacteristic()
result = char.parse_value(b'\\x64\\x00')  # 100 ppm
print('Parsed:', result.value, result.unit)
"

# Run all concentration tests
python -m pytest tests/ -k "concentration" -v
```

## Expected Code Reduction

- Reduce each file from ~50 lines to ~10 lines
- Remove 200+ lines of duplicate parsing code
- Remove 40+ duplicate validation checks
- Eliminate 8 duplicate unit property implementations
- Standardize error messages across all concentration types

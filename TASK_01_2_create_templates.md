# Task 1.2: Create Template Characteristic Classes

## Priority: Phase 1 (Foundation) - After Task 1.1

## Parallelization: Can start after Task 1.1 completes

## Objective

Create reusable template characteristic classes for common patterns to eliminate code duplication across the 138+ characteristic implementations.

## Files to Create

- `src/bluetooth_sig/gatt/characteristics/templates.py` (new file)

## Implementation Details

### 1. Create SimpleUint8Characteristic Template

```python
from __future__ import annotations
from .base import BaseCharacteristic
from .utils import DataParser

class SimpleUint8Characteristic(BaseCharacteristic):
    """Template for simple 1-byte unsigned integer characteristics."""

    expected_length = 1
    min_value = 0
    max_value = 255
    expected_type = int

    def decode_value(self, data: bytearray) -> int:
        """Parse single byte as uint8."""
        return DataParser.parse_int8(data, 0, signed=False)

    def encode_value(self, value: int) -> bytearray:
        """Encode uint8 value to bytes."""
        return DataParser.encode_int8(value, signed=False)
```

### 2. Create SimpleUint16Characteristic Template

```python
class SimpleUint16Characteristic(BaseCharacteristic):
    """Template for simple 2-byte unsigned integer characteristics."""

    expected_length = 2
    min_value = 0
    max_value = 65535
    expected_type = int

    def decode_value(self, data: bytearray) -> int:
        """Parse 2 bytes as uint16."""
        return DataParser.parse_int16(data, 0, signed=False)

    def encode_value(self, value: int) -> bytearray:
        """Encode uint16 value to bytes."""
        return DataParser.encode_int16(value, signed=False)
```

### 3. Create ConcentrationCharacteristic Template

```python
class ConcentrationCharacteristic(BaseCharacteristic):
    """Template for concentration measurements (uint16 with resolution)."""

    expected_length = 2
    min_value = 0
    max_value = 65535
    expected_type = float

    # Subclasses should override these
    resolution: float = 1.0  # Default resolution
    concentration_unit: str = "ppm"  # Default unit

    def decode_value(self, data: bytearray) -> float:
        """Parse concentration with resolution."""
        raw_value = DataParser.parse_int16(data, 0, signed=False)
        return raw_value * self.resolution

    def encode_value(self, value: float) -> bytearray:
        """Encode concentration value to bytes."""
        raw_value = int(value / self.resolution)
        return DataParser.encode_int16(raw_value, signed=False)

    @property
    def unit(self) -> str:
        return self.concentration_unit
```

### 4. Create TemperatureCharacteristic Template

```python
class TemperatureCharacteristic(BaseCharacteristic):
    """Template for temperature measurements (sint16, 0.01°C resolution)."""

    expected_length = 2
    min_value = -273.15  # Absolute zero in Celsius
    max_value = 327.67   # Max sint16 * 0.01
    expected_type = float

    def decode_value(self, data: bytearray) -> float:
        """Parse temperature in 0.01°C resolution."""
        raw_value = DataParser.parse_int16(data, 0, signed=True)
        return raw_value * 0.01

    def encode_value(self, value: float) -> bytearray:
        """Encode temperature to bytes."""
        raw_value = int(value / 0.01)
        return DataParser.encode_int16(raw_value, signed=True)

    @property
    def unit(self) -> str:
        return "°C"
```

### 5. Create IEEE11073FloatCharacteristic Template

```python
class IEEE11073FloatCharacteristic(BaseCharacteristic):
    """Template for IEEE 11073 SFLOAT format characteristics."""

    expected_length = 2
    expected_type = float
    allow_variable_length = True  # Some have additional data

    def decode_value(self, data: bytearray) -> float:
        """Parse IEEE 11073 SFLOAT format."""
        return IEEE11073Parser.parse_sfloat(data, 0)

    def encode_value(self, value: float) -> bytearray:
        """Encode float to IEEE 11073 format."""
        return IEEE11073Parser.encode_sfloat(value)
```

### 6. Create PercentageCharacteristic Template

```python
class PercentageCharacteristic(BaseCharacteristic):
    """Template for percentage values (0-100%)."""

    expected_length = 1
    min_value = 0
    max_value = 100
    expected_type = int

    def decode_value(self, data: bytearray) -> int:
        """Parse percentage value."""
        return DataParser.parse_int8(data, 0, signed=False)

    def encode_value(self, value: int) -> bytearray:
        """Encode percentage to bytes."""
        return DataParser.encode_int8(value, signed=False)

    @property
    def unit(self) -> str:
        return "%"
```

### 7. Update Templates Module Exports

```python
__all__ = [
    "SimpleUint8Characteristic",
    "SimpleUint16Characteristic",
    "ConcentrationCharacteristic",
    "TemperatureCharacteristic",
    "IEEE11073FloatCharacteristic",
    "PercentageCharacteristic"
]
```

## Success Criteria

- All template classes properly inherit from BaseCharacteristic
- Templates use validation attributes correctly
- Templates use utils functions instead of manual parsing
- Each template has comprehensive docstrings with usage examples
- Templates can be imported and used by other characteristics
- All templates pass basic instantiation tests

## Dependencies

- **BLOCKS**: Task 1.1 (BaseCharacteristic enhancements) must complete first
- **ENABLES**: All characteristic conversion tasks (2.x series)

## Testing

```bash
# Test template creation
python -c "from src.bluetooth_sig.gatt.characteristics.templates import SimpleUint16Characteristic; print('✅ Templates importable')"

# Test template inheritance
python -m pytest tests/ -k "template" -v

# Test integration with base class
python -m pytest tests/test_base_characteristic.py -v
```

## Usage Examples for Future Tasks

```python
# Instead of manual implementation:
class BatteryLevelCharacteristic(BaseCharacteristic):
    def decode_value(self, data: bytearray) -> int:
        if len(data) < 1:
            raise ValueError("Battery level requires 1 byte")
        value = data[0]
        if value > 100:
            raise ValueError("Battery level cannot exceed 100%")
        return value

# Use template:
class BatteryLevelCharacteristic(PercentageCharacteristic):
    """Battery level percentage (0-100%)."""
    pass  # Everything handled by template!
```

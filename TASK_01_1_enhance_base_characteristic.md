# Task 1.1: Enhance BaseCharacteristic with Validation Attributes

## Priority: Phase 1 (Foundation) - Must Complete First
## Parallelization: BLOCKING - Required before all other tasks

## Objective
Add declarative validation attributes to BaseCharacteristic to eliminate hardcoded validation throughout all characteristic implementations.

## Files to Modify
- `src/bluetooth_sig/gatt/characteristics/base.py`

## Implementation Details

### 1. Add Class-Level Validation Attributes
Add these optional class attributes to BaseCharacteristic:
```python
# Value range validation
min_value: int | float | None = None
max_value: int | float | None = None

# Data length validation
expected_length: int | None = None
min_length: int | None = None
max_length: int | None = None
allow_variable_length: bool = False

# Type validation
expected_type: type | None = None
```

### 2. Add Validation Methods
Add these methods to BaseCharacteristic:
```python
def _validate_range(self, value: Any) -> None:
    """Validate value is within min/max range."""
    if self.min_value is not None and value < self.min_value:
        raise ValueError(f"Value {value} below minimum {self.min_value}")
    if self.max_value is not None and value > self.max_value:
        raise ValueError(f"Value {value} exceeds maximum {self.max_value}")

def _validate_length(self, data: bytes | bytearray) -> None:
    """Validate data length meets requirements."""
    length = len(data)
    if self.expected_length is not None and length != self.expected_length:
        raise ValueError(f"Expected {self.expected_length} bytes, got {length}")
    if self.min_length is not None and length < self.min_length:
        raise ValueError(f"Minimum {self.min_length} bytes required, got {length}")
    if self.max_length is not None and length > self.max_length:
        raise ValueError(f"Maximum {self.max_length} bytes allowed, got {length}")

def _validate_value(self, value: Any) -> None:
    """Validate parsed value meets all requirements."""
    if self.expected_type is not None and not isinstance(value, self.expected_type):
        raise TypeError(f"Expected {self.expected_type.__name__}, got {type(value).__name__}")
    self._validate_range(value)
```

### 3. Update parse_value Method
Modify the abstract `parse_value` method to automatically call validations:
```python
def parse_value(self, data: bytes | bytearray) -> CharacteristicData:
    """Parse characteristic data with automatic validation."""
    # Validate input data length
    self._validate_length(data)

    # Call subclass implementation
    try:
        parsed_value = self.decode_value(data)

        # Validate parsed value
        self._validate_value(parsed_value)

        return CharacteristicData(
            value=parsed_value,
            unit=self.unit,
            raw_data=bytes(data),
            parse_success=True,
            error_message=None
        )
    except (ValueError, TypeError, struct.error) as e:
        return CharacteristicData(
            value=None,
            unit=self.unit,
            raw_data=bytes(data),
            parse_success=False,
            error_message=str(e)
        )
```

### 4. Update Documentation
Add docstring examples showing how subclasses should use the new attributes:
```python
class ExampleCharacteristic(BaseCharacteristic):
    """Example showing validation attributes usage."""

    # Declare validation constraints
    expected_length = 2
    min_value = 0
    max_value = 65535
    expected_type = int

    def decode_value(self, data: bytearray) -> int:
        # Just parse - validation happens automatically
        return DataParser.parse_uint16(data, 0)
```

## Success Criteria
- All validation attributes properly defined
- Validation methods implemented with clear error messages
- `parse_value` method updated to use automatic validation
- Maintains backward compatibility
- All existing tests pass
- New validation can be tested independently

## Dependencies
- Must be completed before ANY other task
- Blocks all characteristic refactoring tasks
- Required for template class creation

## Testing
```bash
python -m pytest tests/test_base_characteristic.py -v
python -m pytest tests/ -k "base" -v
```

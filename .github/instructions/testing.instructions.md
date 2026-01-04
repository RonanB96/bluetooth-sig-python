---
applyTo: "**/tests/**/*.py,**/test_*.py,**/*_test.py"
---

# Testing Requirements & Guidelines

## Testing Policy (MANDATORY)

**No untested code. Period.**

- Every new function/method needs tests
- Minimum: success case + 2 failure cases
- Run full test suite before completion: `python -m pytest tests/ -v`
- Claiming "it works" without running tests is unacceptable

## Test Structure Requirements

Each new or modified characteristic/service MUST include:

1. **Parsing success test** - Canonical example from spec table
2. **Length violation test** - Too short, too long, empty payload
3. **Range violation test** - Out of range or reserved value
4. **Registry resolution test** - Name-to-UUID resolution works
5. **Multi-packet test** (where applicable) - Variable length handling

**Example structure:**
```python
import pytest
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
from bluetooth_sig.gatt.exceptions import InsufficientDataError, ValueRangeError

class TestBatteryLevelCharacteristic:
    """Test suite for Battery Level characteristic."""

    def test_decode_valid_value(self):
        """Test decoding valid battery level."""
        char = BatteryLevelCharacteristic()
        data = bytearray([75])  # 75%

        result = char.parse_value(data)

        assert result == 75
        assert isinstance(result, int)

    def test_decode_boundary_values(self):
        """Test decoding boundary values."""
        char = BatteryLevelCharacteristic()

        # Minimum
        assert char.parse_value(bytearray([0])) == 0

        # Maximum
        assert char.parse_value(bytearray([100])) == 100

    def test_decode_insufficient_data(self):
        """Test error on insufficient data."""
        char = BatteryLevelCharacteristic()

        with pytest.raises(InsufficientDataError) as exc_info:
            char.parse_value(bytearray([]))

        assert "requires exactly 1 byte" in str(exc_info.value).lower()

    def test_decode_out_of_range(self):
        """Test error on out-of-range value."""
        char = BatteryLevelCharacteristic()

        with pytest.raises(ValueRangeError) as exc_info:
            char.parse_value(bytearray([101]))

        assert "0-100" in str(exc_info.value)

    def test_registry_resolution(self):
        """Test characteristic name resolves to correct UUID."""
        from bluetooth_sig.gatt.uuid_registry import uuid_registry
        from bluetooth_sig.types.gatt_enums import CharacteristicName

        info = uuid_registry.get_characteristic_info(
            CharacteristicName.BATTERY_LEVEL
        )

        assert info is not None
        assert info.uuid == "2A19"
        assert "battery" in info.name.lower()
```

## Test Organization

**Directory structure:**
```
tests/
├── conftest.py                    # Shared fixtures
├── test_characteristics/
│   ├── test_battery_level.py
│   ├── test_temperature.py
│   └── test_humidity.py
├── test_services/
│   ├── test_battery_service.py
│   └── test_environmental_sensing.py
└── test_registry/
    ├── test_uuid_registry.py
    └── test_name_resolver.py
```

## Fixtures and Test Data

**Use conftest.py for shared fixtures:**
```python
# tests/conftest.py
import pytest

@pytest.fixture
def valid_battery_data():
    """Valid battery level characteristic data."""
    return bytearray([75])  # 75%

@pytest.fixture
def invalid_short_data():
    """Invalid data - too short."""
    return bytearray([])

@pytest.fixture
def invalid_range_data():
    """Invalid data - out of range."""
    return bytearray([255])
```

## Edge Cases to Test

Always test these scenarios:
- Empty payload: `bytearray([])`
- Too short: One byte less than minimum
- Too long: One byte more than maximum
- Minimum valid value: Lower bound
- Maximum valid value: Upper bound
- Just below minimum: Invalid low
- Just above maximum: Invalid high
- Special sentinels: 0xFF, 0xFFFF, NaN markers
- Reserved values: Per specification

## Testing Special Values

**Handle sentinel values:**
```python
def test_decode_unknown_value(self):
    """Test decoding special 'unknown' sentinel value."""
    char = HumidityCharacteristic()

    # 0xFFFF = "Unknown" per spec
    data = bytearray([0xFF, 0xFF])
    result = char.parse_value(data)

    assert result is None  # Unknown maps to None
```

## Mock Dependencies

**Mock external dependencies, not core logic:**
```python
from unittest.mock import Mock, patch

def test_with_context():
    """Test characteristic with mocked context."""
    char = TemperatureCharacteristic()
    mock_context = Mock(spec=CharacteristicContext)
    mock_context.flags = {"celsius": True}

    data = bytearray([0x00, 0x10])  # Some temperature value
    result = char.parse_value(data, ctx=mock_context)

    assert isinstance(result, float)
```

## Parametrized Tests

**Use parametrize for multiple similar cases:**
```python
@pytest.mark.parametrize("data,expected", [
    (bytearray([0]), 0),
    (bytearray([50]), 50),
    (bytearray([100]), 100),
])
def test_decode_various_valid_values(data, expected):
    """Test decoding various valid battery levels."""
    char = BatteryLevelCharacteristic()
    assert char.parse_value(data) == expected

@pytest.mark.parametrize("invalid_data", [
    bytearray([]),           # Too short
    bytearray([101]),        # Too high
    bytearray([255]),        # Way too high
    bytearray([50, 60]),     # Too long
])
def test_decode_invalid_data(invalid_data):
    """Test that invalid data raises appropriate errors."""
    char = BatteryLevelCharacteristic()
    with pytest.raises((InsufficientDataError, ValueRangeError)):
        char.parse_value(invalid_data)
```

## Performance Tests

**For characteristics with complex parsing:**
```python
import time

def test_decode_performance():
    """Test decoding performance is acceptable."""
    char = ComplexCharacteristic()
    data = bytearray([...])  # Valid data

    start = time.perf_counter()
    for _ in range(1000):
        char.parse_value(data)
    elapsed = time.perf_counter() - start

    # Should decode 1000 times in less than 100ms
    assert elapsed < 0.1, f"Decoding too slow: {elapsed:.3f}s for 1000 iterations"
```

## Integration Tests

**Test with real characteristic discovery:**
```python
@pytest.mark.integration
def test_service_discovery_integration():
    """Test service and characteristic discovery together."""
    # This test is marked and skipped by default
    # Run with: pytest -v -m integration
    ...
```

## Test Naming Conventions

- `test_<action>_<scenario>` - e.g., `test_decode_valid_value`
- `test_<action>_<error_type>` - e.g., `test_decode_insufficient_data`
- Be descriptive - test names should explain what's being tested

## Assertions

**Be specific in assertions:**
```python
# ❌ Not specific enough
assert result

# ✅ Better
assert result == 75
assert isinstance(result, int)
assert 0 <= result <= 100

# ✅ Even better with message
assert result == 75, f"Expected 75, got {result}"
```

## Coverage Requirements

**Aim for high coverage:**
- Production code: Target 90%+ coverage
- Test code: Not measured (tests test themselves)
- Run coverage report: `pytest --cov=src/bluetooth_sig --cov-report=html`

## Testing Command Reference

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_battery_level.py -v

# Run specific test
python -m pytest tests/test_battery_level.py::TestBatteryLevelCharacteristic::test_decode_valid_value -v

# Run with coverage
pytest --cov=src/bluetooth_sig --cov-report=term-missing

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "battery" -v

# Run with detailed output
pytest -vv

# Stop on first failure
pytest -x
```

## Deterministic Tests

**All tests must be deterministic:**
- No reliance on live devices (unless explicitly marked and skipped by default)
- No network calls (mock them)
- No time-dependent behaviour (mock datetime)
- Use fixed random seeds if randomness needed
- Tests should pass in any order

## Test Documentation

**Document complex test scenarios:**
```python
def test_complex_multi_field_parsing():
    """Test parsing complex characteristic with multiple fields.

    This test validates:
    1. Flags byte parsing (bit 0: unit, bit 1: timestamp)
    2. Multi-byte temperature value (little-endian)
    3. Optional timestamp field (only present if flag bit 1 set)
    4. Proper handling of missing optional fields

    Spec reference: Temperature Measurement (0x2A1C), Section 3.1
    """
    ...
```

## Before Claiming Completion

Run the full test suite and verify all tests pass:
```bash
python -m pytest tests/ -v
```

If any test fails, you MUST fix it before claiming the task is complete.

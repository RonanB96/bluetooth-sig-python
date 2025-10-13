# Testing Guide

Comprehensive guide to testing with the Bluetooth SIG Standards Library.

## Running Tests

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run with Coverage

```bash
python -m pytest tests/ --cov=src/bluetooth_sig --cov-report=html --cov-report=term-missing
```

### Run Specific Tests

```bash
# Run tests for a specific module
python -m pytest tests/test_battery_level.py -v

# Run a specific test
python -m pytest tests/test_battery_level.py::TestBatteryLevel::test_decode_valid -v

# Run tests matching a pattern
python -m pytest tests/ -k "battery" -v
```

## Testing Without Hardware

One of the key advantages of this library's architecture is that you can test BLE data parsing **without any BLE hardware**.

### Unit Testing Example

```python
import pytest
from bluetooth_sig.core import BluetoothSIGTranslator

class TestBLEParsing:
    """Test BLE characteristic parsing without hardware."""
    
    def test_battery_level_parsing(self):
        """Test battery level parsing with mock data."""
        translator = BluetoothSIGTranslator()
        
        # Mock raw BLE data (no hardware needed)
        mock_data = bytearray([75])
        
        # Parse
        result = translator.parse_characteristic_data("2A19", mock_data)
        
        # Assert
        assert result.value == 75
        assert 0 <= result.value <= 100
    
    def test_temperature_parsing(self):
        """Test temperature parsing with mock data."""
        translator = BluetoothSIGTranslator()
        
        # Mock temperature data: 24.36°C
        mock_data = bytearray([0x64, 0x09])
        
        result = translator.parse_characteristic_data("2A6E", mock_data)
        
        assert result.value == 24.36
        assert isinstance(result.value, float)
```

### Testing Error Conditions

```python
import pytest
from bluetooth_sig.gatt.exceptions import (
    InsufficientDataError,
    ValueRangeError
)

class TestErrorHandling:
    """Test error handling without hardware."""
    
    def test_insufficient_data(self):
        """Test error when data is too short."""
        translator = BluetoothSIGTranslator()
        
        # Empty data
        with pytest.raises(InsufficientDataError):
            translator.parse_characteristic_data("2A19", bytearray([]))
    
    def test_out_of_range_value(self):
        """Test error when value is out of range."""
        translator = BluetoothSIGTranslator()
        
        # Battery level > 100%
        with pytest.raises(ValueRangeError):
            translator.parse_characteristic_data("2A19", bytearray([150]))
```

## Mocking BLE Interactions

When integrating with BLE libraries, you can mock the BLE operations:

### Mocking bleak

```python
import pytest
from unittest.mock import AsyncMock, patch
from bluetooth_sig.core import BluetoothSIGTranslator

@pytest.fixture
def mock_bleak_client():
    """Mock BleakClient for testing."""
    with patch('bleak.BleakClient') as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        yield client

@pytest.mark.asyncio
async def test_read_battery_with_mock(mock_bleak_client):
    """Test reading battery level with mocked BLE."""
    # Setup mock
    mock_bleak_client.read_gatt_char.return_value = bytearray([85])
    
    # Your application code
    translator = BluetoothSIGTranslator()
    raw_data = await mock_bleak_client.read_gatt_char("2A19")
    result = translator.parse_characteristic_data("2A19", raw_data)
    
    # Assert
    assert result.value == 85
    mock_bleak_client.read_gatt_char.assert_called_once_with("2A19")
```

### Mocking simplepyble

```python
from unittest.mock import Mock, patch

def test_read_battery_simplepyble_mock():
    """Test reading battery with mocked simplepyble."""
    # Create mock peripheral
    mock_peripheral = Mock()
    mock_peripheral.read.return_value = bytes([75])
    
    # Your application code
    translator = BluetoothSIGTranslator()
    raw_data = mock_peripheral.read("180F", "2A19")
    result = translator.parse_characteristic_data("2A19", bytearray(raw_data))
    
    # Assert
    assert result.value == 75
    mock_peripheral.read.assert_called_once()
```

## Test Data Generation

### Creating Test Vectors

```python
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def battery_level(percentage: int) -> bytearray:
        """Create battery level test data."""
        assert 0 <= percentage <= 100
        return bytearray([percentage])
    
    @staticmethod
    def temperature(celsius: float) -> bytearray:
        """Create temperature test data."""
        # Temperature encoded as sint16 with 0.01°C resolution
        value = int(celsius * 100)
        return bytearray(value.to_bytes(2, byteorder='little', signed=True))
    
    @staticmethod
    def humidity(percentage: float) -> bytearray:
        """Create humidity test data."""
        # Humidity encoded as uint16 with 0.01% resolution
        value = int(percentage * 100)
        return bytearray(value.to_bytes(2, byteorder='little', signed=False))

# Usage
def test_with_factory():
    translator = BluetoothSIGTranslator()
    
    # Generate test data
    battery_data = TestDataFactory.battery_level(85)
    temp_data = TestDataFactory.temperature(24.36)
    humidity_data = TestDataFactory.humidity(49.42)
    
    # Test parsing
    assert translator.parse_characteristic_data("2A19", battery_data).value == 85
    assert translator.parse_characteristic_data("2A6E", temp_data).value == 24.36
    assert translator.parse_characteristic_data("2A6F", humidity_data).value == 49.42
```

## Parametrized Testing

Test multiple scenarios efficiently:

```python
import pytest

@pytest.mark.parametrize("battery_level,expected", [
    (0, 0),
    (25, 25),
    (50, 50),
    (75, 75),
    (100, 100),
])
def test_battery_levels(battery_level, expected):
    """Test various battery levels."""
    translator = BluetoothSIGTranslator()
    data = bytearray([battery_level])
    result = translator.parse_characteristic_data("2A19", data)
    assert result.value == expected

@pytest.mark.parametrize("invalid_data", [
    bytearray([]),      # Too short
    bytearray([101]),   # Too high
    bytearray([255]),   # Way too high
])
def test_invalid_battery_data(invalid_data):
    """Test error handling for invalid data."""
    translator = BluetoothSIGTranslator()
    with pytest.raises((InsufficientDataError, ValueRangeError)):
        translator.parse_characteristic_data("2A19", invalid_data)
```

## Testing with Fixtures

### Pytest Fixtures

```python
import pytest
from bluetooth_sig.core import BluetoothSIGTranslator

@pytest.fixture
def translator():
    """Provide a translator instance."""
    return BluetoothSIGTranslator()

@pytest.fixture
def valid_battery_data():
    """Provide valid battery level data."""
    return bytearray([75])

@pytest.fixture
def valid_temp_data():
    """Provide valid temperature data."""
    return bytearray([0x64, 0x09])  # 24.36°C

def test_with_fixtures(translator, valid_battery_data):
    """Test using fixtures."""
    result = translator.parse_characteristic_data("2A19", valid_battery_data)
    assert result.value == 75
```

## Integration Testing

Test complete workflows:

```python
class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_multiple_characteristics(self):
        """Test parsing multiple characteristics."""
        translator = BluetoothSIGTranslator()
        
        # Simulate reading multiple characteristics
        sensor_data = {
            "2A19": bytearray([85]),           # Battery: 85%
            "2A6E": bytearray([0x64, 0x09]),   # Temp: 24.36°C
            "2A6F": bytearray([0x3A, 0x13]),   # Humidity: 49.42%
        }
        
        results = {}
        for uuid, data in sensor_data.items():
            results[uuid] = translator.parse_characteristic_data(uuid, data)
        
        # Verify all parsed correctly
        assert results["2A19"].value == 85
        assert results["2A6E"].value == 24.36
        assert results["2A6F"].value == 49.42
    
    def test_uuid_resolution_workflow(self):
        """Test UUID resolution workflow."""
        translator = BluetoothSIGTranslator()
        
        # Resolve UUID to name
        char_info = translator.resolve_uuid("2A19")
        assert char_info.name == "Battery Level"
        
        # Resolve name to UUID
        battery_uuid = translator.resolve_name("Battery Level")
        assert battery_uuid.uuid == "2A19"
        
        # Round-trip
        assert translator.resolve_uuid(battery_uuid.uuid).name == char_info.name
```

## Performance Testing

```python
import time

def test_parsing_performance():
    """Test parsing performance."""
    translator = BluetoothSIGTranslator()
    data = bytearray([75])
    
    # Warm up
    for _ in range(100):
        translator.parse_characteristic_data("2A19", data)
    
    # Measure
    start = time.perf_counter()
    iterations = 10000
    for _ in range(iterations):
        translator.parse_characteristic_data("2A19", data)
    elapsed = time.perf_counter() - start
    
    # Should be fast (< 100μs per parse)
    avg_time = elapsed / iterations
    assert avg_time < 0.0001, f"Parsing too slow: {avg_time:.6f}s per iteration"
    print(f"Average parse time: {avg_time * 1000000:.1f}μs")
```

## Test Organization

Recommended test structure:

```
tests/
├── conftest.py                 # Shared fixtures
├── test_core/
│   ├── test_translator.py      # Core API tests
│   └── test_uuid_resolution.py # UUID resolution tests
├── test_characteristics/
│   ├── test_battery_level.py   # Battery characteristic
│   ├── test_temperature.py     # Temperature characteristic
│   └── test_humidity.py        # Humidity characteristic
├── test_services/
│   └── test_battery_service.py # Service tests
├── test_registry/
│   └── test_uuid_registry.py   # Registry tests
└── test_integration/
    └── test_workflows.py        # End-to-end tests
```

## Continuous Integration

Example GitHub Actions workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e ".[dev,test]"
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src/bluetooth_sig --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Best Practices

### 1. Test One Thing at a Time

```python
# ✅ Good - tests one aspect
def test_battery_valid_value():
    translator = BluetoothSIGTranslator()
    result = translator.parse_characteristic_data("2A19", bytearray([75]))
    assert result.value == 75

def test_battery_invalid_value():
    translator = BluetoothSIGTranslator()
    with pytest.raises(ValueRangeError):
        translator.parse_characteristic_data("2A19", bytearray([150]))

# ❌ Bad - tests multiple things
def test_battery_everything():
    translator = BluetoothSIGTranslator()
    # Tests too many scenarios in one test
    ...
```

### 2. Use Descriptive Names

```python
# ✅ Good
def test_battery_level_rejects_value_above_100():
    ...

# ❌ Bad
def test_battery_1():
    ...
```

### 3. Arrange-Act-Assert Pattern

```python
def test_temperature_parsing():
    # Arrange
    translator = BluetoothSIGTranslator()
    data = bytearray([0x64, 0x09])
    
    # Act
    result = translator.parse_characteristic_data("2A6E", data)
    
    # Assert
    assert result.value == 24.36
```

## Next Steps

- [Contributing Guide](contributing.md) - Contribute to the project
- [API Reference](api/core.md) - API documentation
- [Examples](https://github.com/RonanB96/bluetooth-sig-python/tree/main/examples) - More examples

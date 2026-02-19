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

### Type-Safe Unit Testing (Recommended)

For known characteristics, use characteristic classes directly for full type inference in your tests:

```python
import pytest

from bluetooth_sig.gatt.characteristics import (
    BatteryLevelCharacteristic,
    TemperatureCharacteristic,
)


class TestTypeSafeParsing:
    """Type-safe tests with full IDE support."""

    def test_battery_level_parsing(self):
        """Test battery level with type-safe API."""
        battery = BatteryLevelCharacteristic()
        mock_data = bytearray([75])  # 75% battery

        # Parse - result is int (IDE knows!)
        level = battery.parse_value(mock_data)

        assert level == 75
        assert 0 <= level <= 100

    def test_temperature_parsing(self):
        """Test temperature with type-safe API."""
        temp = TemperatureCharacteristic()
        mock_data = bytearray([0x64, 0x09])  # 24.04°C

        # Parse - result is Temperature dataclass (IDE knows!)
        result = temp.parse_value(mock_data)

        assert result.temperature == pytest.approx(24.04, rel=0.01)
        assert isinstance(result.temperature, float)

    def test_round_trip(self):
        """Test encode/decode round-trip."""
        battery = BatteryLevelCharacteristic()
        original_value = 85

        # Encode
        encoded = battery.build_value(original_value)

        # Decode back
        decoded = battery.parse_value(encoded)

        assert decoded == original_value
```

### Dynamic Unit Testing (Discovery Scenarios)

Use the Translator API when testing code that handles unknown devices or UUID-based discovery:

```python
import pytest

from bluetooth_sig import BluetoothSIGTranslator


class TestDynamicParsing:
    """Test dynamic parsing for discovery scenarios."""

    def test_battery_level_parsing(self):
        """Test battery level parsing with UUID from discovery."""
        # Simulates UUID received from BLE device discovery
        battery_uuid = "2A19"  # From device.services
        mock_data = bytearray([75])  # 75% battery

        translator = BluetoothSIGTranslator()

        # Parse - library auto-identifies the characteristic
        value = translator.parse_characteristic(battery_uuid, mock_data)
        info = translator.get_characteristic_info_by_uuid(battery_uuid)

        assert value == 75
        assert info.name == "Battery Level"

    def test_unknown_characteristic(self):
        """Test handling of unknown/custom characteristics."""
        custom_uuid = "12345678-1234-1234-1234-123456789abc"
        mock_data = bytearray([0x01, 0x02, 0x03])

        translator = BluetoothSIGTranslator()

        # Unknown characteristics are not supported
        assert not translator.supports(custom_uuid)

        # Attempting to parse raises CharacteristicParseError
        from bluetooth_sig.gatt.exceptions import CharacteristicParseError

        with pytest.raises(CharacteristicParseError):
            translator.parse_characteristic(custom_uuid, mock_data)
```

### Testing Error Conditions

Test error handling with characteristic classes (type-safe):

```python
import pytest

from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
from bluetooth_sig.gatt.exceptions import (
    InsufficientDataError,
    ValueRangeError,
)


class TestErrorHandling:
    """Test error handling with type-safe API."""

    def test_insufficient_data(self):
        """Test error when data is too short."""
        battery = BatteryLevelCharacteristic()

        with pytest.raises(InsufficientDataError):
            battery.parse_value(bytearray([]))  # Empty data

    def test_out_of_range_value(self):
        """Test error when value is out of range."""
        battery = BatteryLevelCharacteristic()

        with pytest.raises(ValueRangeError):
            battery.parse_value(bytearray([150]))  # > 100%
```

## Mocking BLE Interactions

When integrating with BLE libraries, you can mock the BLE operations:

### Type-Safe Mocking with bleak (Recommended)

```python
from unittest.mock import AsyncMock, patch

import pytest

from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic


@pytest.fixture
def mock_bleak_client():
    """Mock BleakClient for testing."""
    with patch("bleak.BleakClient") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        yield client


@pytest.mark.asyncio
async def test_read_battery_type_safe(mock_bleak_client):
    """Test reading battery level with type-safe API."""
    battery = BatteryLevelCharacteristic()
    mock_battery_data = bytearray([85])  # 85% battery

    # Setup mock
    mock_bleak_client.read_gatt_char.return_value = mock_battery_data

    # Read using characteristic's UUID property
    raw_data = await mock_bleak_client.read_gatt_char(str(battery.uuid))

    # Parse with type-safety - level is int
    level = battery.parse_value(bytearray(raw_data))

    assert level == 85
    mock_bleak_client.read_gatt_char.assert_called_once_with(str(battery.uuid))
```

### Dynamic Mocking with bleak

For testing discovery scenarios with unknown UUIDs:

```python
from unittest.mock import AsyncMock, patch

import pytest

from bluetooth_sig import BluetoothSIGTranslator


@pytest.fixture
def mock_bleak_client():
    """Mock BleakClient for testing."""
    with patch("bleak.BleakClient") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        yield client


@pytest.mark.asyncio
async def test_read_battery_dynamic(mock_bleak_client):
    """Test reading battery level with dynamic API."""
    # UUID from device discovery
    discovered_uuid = "2A19"
    mock_battery_data = bytearray([85])  # 85% battery

    mock_bleak_client.read_gatt_char.return_value = mock_battery_data

    translator = BluetoothSIGTranslator()
    raw_data = await mock_bleak_client.read_gatt_char(discovered_uuid)
    value = translator.parse_characteristic(discovered_uuid, raw_data)
    info = translator.get_characteristic_info_by_uuid(discovered_uuid)

    assert value == 85
    assert info.name == "Battery Level"
```

### Mocking simplepyble

```python
from unittest.mock import Mock

from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
from bluetooth_sig.gatt.services import BatteryService


def test_read_battery_simplepyble_mock():
    """Test reading battery with mocked simplepyble."""
    battery = BatteryLevelCharacteristic()
    battery_service = BatteryService()
    mock_battery_data = bytes([75])  # 75% battery

    # Create mock peripheral
    mock_peripheral = Mock()
    mock_peripheral.read.return_value = mock_battery_data

    # Read using service and characteristic UUIDs
    raw_data = mock_peripheral.read(
        str(battery_service.uuid), str(battery.uuid)
    )

    # Parse with type-safety
    level = battery.parse_value(bytearray(raw_data))

    assert level == 75
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
        return bytearray(value.to_bytes(2, byteorder="little", signed=True))

    @staticmethod
    def humidity(percentage: float) -> bytearray:
        """Create humidity test data."""
        # Humidity encoded as uint16 with 0.01% resolution
        value = int(percentage * 100)
        return bytearray(value.to_bytes(2, byteorder="little", signed=False))


# Usage
def test_with_factory():
    # ============================================
    # TEST DATA - From factory helpers
    # ============================================
    BATTERY_UUID = "2A19"
    TEMP_UUID = "2A6E"
    HUMIDITY_UUID = "2A6F"

    translator = BluetoothSIGTranslator()

    # Generate test data
    battery_data = TestDataFactory.battery_level(85)
    temp_data = TestDataFactory.temperature(24.04)
    humidity_data = TestDataFactory.humidity(49.22)

    # Test parsing - returns values directly (not wrapped)
    assert translator.parse_characteristic(BATTERY_UUID, battery_data) == 85
    assert translator.parse_characteristic(TEMP_UUID, temp_data) == 24.04
    assert (
        translator.parse_characteristic(HUMIDITY_UUID, humidity_data) == 49.22
    )
```

## Parametrized Testing

Test multiple scenarios efficiently:

```python
import pytest


@pytest.mark.parametrize(
    "battery_level,expected",
    [
        (0, 0),
        (25, 25),
        (50, 50),
        (75, 75),
        (100, 100),
    ],
)
def test_battery_levels(battery_level, expected):
    """Test various battery levels."""
    BATTERY_LEVEL_UUID = "2A19"  # UUID from BLE spec
    translator = BluetoothSIGTranslator()
    data = bytearray([battery_level])
    value = translator.parse_characteristic(BATTERY_LEVEL_UUID, data)
    assert value == expected


@pytest.mark.parametrize(
    "invalid_data",
    [
        bytearray([]),  # Too short
        bytearray([101]),  # Too high
        bytearray([255]),  # Way too high
    ],
)
def test_invalid_battery_data(invalid_data):
    """Test error handling for invalid data."""
    BATTERY_LEVEL_UUID = "2A19"  # UUID from BLE spec
    translator = BluetoothSIGTranslator()
    with pytest.raises((InsufficientDataError, ValueRangeError)):
        translator.parse_characteristic(BATTERY_LEVEL_UUID, invalid_data)
```

## Testing with Fixtures

### Pytest Fixtures

```python
import pytest

from bluetooth_sig import BluetoothSIGTranslator


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
    return bytearray([0x64, 0x09])  # 24.04°C


def test_with_fixtures(translator, valid_battery_data):
    """Test using fixtures."""
    BATTERY_LEVEL_UUID = "2A19"  # UUID from BLE spec
    value = translator.parse_characteristic(
        BATTERY_LEVEL_UUID, valid_battery_data
    )
    assert value == 75
```

## Integration Testing

Test complete workflows:

```python
class TestIntegration:
    """Integration tests for complete workflows."""

    def test_multiple_characteristics(self):
        """Test parsing multiple characteristics."""
        # ============================================
        # SIMULATED DATA - Multiple sensor readings
        # ============================================
        BATTERY_UUID = "2A19"
        TEMP_UUID = "2A6E"
        HUMIDITY_UUID = "2A6F"

        translator = BluetoothSIGTranslator()

        # Simulate reading multiple characteristics
        sensor_data = {
            BATTERY_UUID: bytearray([85]),  # Battery: 85%
            TEMP_UUID: bytearray([0x64, 0x09]),  # Temp: 24.04°C
            HUMIDITY_UUID: bytearray([0x3A, 0x13]),  # Humidity: 49.22%
        }

        results = {}
        for uuid, data in sensor_data.items():
            results[uuid] = translator.parse_characteristic(uuid, data)

        # Verify all parsed correctly - values returned directly
        assert results[BATTERY_UUID] == 85
        assert results[TEMP_UUID] == 24.04
        assert results[HUMIDITY_UUID] == 49.22

    def test_uuid_resolution_workflow(self):
        """Test UUID resolution workflow."""
        BATTERY_LEVEL_UUID = "2A19"  # UUID from BLE spec
        translator = BluetoothSIGTranslator()

        # Resolve UUID to name
        char_info = translator.get_sig_info_by_uuid(BATTERY_LEVEL_UUID)
        assert char_info.name == "Battery Level"

        # Resolve name to UUID
        battery_uuid = translator.get_sig_info_by_name("Battery Level")
        assert battery_uuid.uuid == BATTERY_LEVEL_UUID

        # Round-trip
        assert (
            translator.get_sig_info_by_uuid(battery_uuid.uuid).name
            == char_info.name
        )
```

## Performance Testing

```python
import time


def test_parsing_performance():
    """Test parsing performance."""
    BATTERY_LEVEL_UUID = "2A19"  # UUID from BLE spec
    data = bytearray([75])  # Test data
    translator = BluetoothSIGTranslator()

    # Warm up
    for _ in range(100):
        translator.parse_characteristic(BATTERY_LEVEL_UUID, data)

    # Measure
    start = time.perf_counter()
    iterations = 10000
    for _ in range(iterations):
        translator.parse_characteristic(BATTERY_LEVEL_UUID, data)
    elapsed = time.perf_counter() - start

    # Should be fast (< 100μs per parse)
    avg_time = elapsed / iterations
    assert avg_time < 0.0001, (
        f"Parsing too slow: {avg_time:.6f}s per iteration"
    )
    print(f"Average parse time: {avg_time * 1000000:.1f}μs")
```

## Test Organization

Recommended test structure:

```text
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
        python-version: ["3.10", "3.11", "3.12"]

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
    BATTERY_LEVEL_UUID = "2A19"  # UUID from BLE spec
    translator = BluetoothSIGTranslator()
    value = translator.parse_characteristic(
        BATTERY_LEVEL_UUID, bytearray([75])
    )
    assert value == 75


def test_battery_invalid_value():
    BATTERY_LEVEL_UUID = "2A19"  # UUID from BLE spec
    translator = BluetoothSIGTranslator()
    with pytest.raises(ValueRangeError):
        translator.parse_characteristic(BATTERY_LEVEL_UUID, bytearray([150]))


# ❌ Bad - tests multiple things
def test_battery_everything():
    translator = BluetoothSIGTranslator()
    # Tests too many scenarios in one test
    ...
```

### 2. Use Descriptive Names

```python
# ✅ Good
def test_battery_level_rejects_value_above_100(): ...


# ❌ Bad
def test_battery_1(): ...
```

### 3. Arrange-Act-Assert Pattern

```python
def test_temperature_parsing():
    # Arrange
    TEMP_UUID = "2A6E"  # Temperature characteristic UUID
    data = bytearray([0x64, 0x09])  # 24.04°C
    translator = BluetoothSIGTranslator()

    # Act
    value = translator.parse_characteristic(TEMP_UUID, data)

    # Assert
    assert value == 24.04
```

## Next Steps

- [Contributing Guide](contributing.md) - Contribute to the project
- [API Reference](../api/index.md) - API documentation
- [Examples](https://github.com/RonanB96/bluetooth-sig-python/tree/main/examples) - More examples

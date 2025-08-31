# Home Assistant Integration Architecture

This document describes the proper separation of concerns between the BLE GATT framework and Home Assistant integration.

## Architecture Overview

The framework follows a strict three-layer architecture:

```
Home Assistant Integration Layer
            ↓ (calls)
    Translation Layer  
            ↓ (calls)
       GATT Layer
```

**IMPORTANT**: Dependencies flow in one direction only: HA → Translation → GATT (never reverse)

## Layer Responsibilities

### 1. GATT Layer (`src/ble_gatt_device/gatt/`)

**Purpose**: Pure Bluetooth functionality with metadata properties for translation layer

**Contains**:
- Bluetooth SIG UUID resolution
- Raw BLE data parsing according to specifications
- Characteristic and service implementations
- Metadata properties for HA integration (`device_class`, `state_class`, `unit`)

**Must NOT contain**:
- Any `homeassistant` imports
- HA entity creation logic
- HA-specific configuration
- Direct HA API calls

### 2. Translation Layer (`src/ble_gatt_device/gatt/ha_translation.py`)

**Purpose**: Convert GATT data to Home Assistant-compatible format

**Contains**:
- Data type mapping (BLE → HA entity types)
- Unit conversions and normalization
- HA entity configuration generation
- State class and device class mapping

**Example Implementation**:
```python
def translate_temperature_data(char: TemperatureCharacteristic, raw_data: bytearray) -> dict:
    """Translate temperature data for Home Assistant."""
    value = char.parse_value(raw_data)
    return {
        "state": value,
        "attributes": {
            "device_class": char.device_class,  # "temperature"
            "state_class": char.state_class,    # "measurement"
            "unit_of_measurement": char.unit,   # "°C"
            "friendly_name": "BLE Temperature Sensor"
        }
    }
```

**Must NOT contain**:
- Direct HA entity creation
- HA API calls or imports
- Device-specific configuration

### 3. Home Assistant Integration Layer (Future/External)

**Purpose**: Create actual HA entities and handle HA-specific logic

**Will contain**:
- HA entity creation and lifecycle management
- Device discovery and registration
- Configuration flow implementation
- HA service and platform registration

**Example Implementation** (Future):
```python
from homeassistant.components.sensor import SensorEntity
from ble_gatt_device.gatt.ha_translation import translate_temperature_data

class BLETemperatureSensor(SensorEntity):
    """Home Assistant temperature sensor entity for BLE devices."""
    
    def __init__(self, device, characteristic):
        self._device = device
        self._characteristic = characteristic
        
    @property
    def state(self):
        """Return the current temperature."""
        raw_data = self._device.read_characteristic(self._characteristic.uuid)
        ha_data = translate_temperature_data(self._characteristic, raw_data)
        return ha_data["state"]
        
    @property
    def device_class(self):
        return self._characteristic.device_class
```

## Validation Rules

The framework includes tests to validate architectural boundaries and ensure clean separation of concerns.

### Architectural Tests

1. **Import Validation**: Ensures GATT layer has no `homeassistant` imports
2. **Dependency Direction**: Validates one-way dependency flow
3. **Metadata Availability**: Ensures all characteristics provide HA metadata
4. **Translation Completeness**: Validates all characteristic data can be translated

### Example Validation

```python
def test_gatt_layer_isolation():
    """Test that GATT layer has no HA dependencies."""
    import ast
    import inspect
    from ble_gatt_device.gatt.characteristics import TemperatureCharacteristic
    
    # Check no homeassistant imports in source
    source = inspect.getsource(TemperatureCharacteristic)
    tree = ast.parse(source)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith('homeassistant')
```

## Implementation Patterns

### Characteristic Implementation Pattern

All characteristics must follow this pattern for HA compatibility:

```python
@dataclass
class ExampleCharacteristic(BaseCharacteristic):
    """Example characteristic with HA metadata."""
    
    def __post_init__(self):
        self.value_type = "float"  # Data type
        super().__post_init__()
    
    def parse_value(self, data: bytearray) -> float:
        """Parse raw BLE data to meaningful value."""
        # Bluetooth SIG specified parsing logic
        return parsed_value
    
    @property
    def unit(self) -> str:
        """Unit of measurement for HA."""
        return "°C"
    
    @property
    def device_class(self) -> str:
        """HA device class."""
        return "temperature"
    
    @property 
    def state_class(self) -> str:
        """HA state class."""
        return "measurement"
```

### Service Implementation Pattern

Services organize characteristics and provide discovery capabilities:

```python
@dataclass
class ExampleService(BaseGattService):
    """Example service implementation."""
    
    SERVICE_UUID = "1809"  # Health Thermometer
    
    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Define expected characteristics."""
        return {
            "Temperature Measurement": TemperatureMeasurementCharacteristic,
        }
    
    def get_ha_entities(self) -> List[Dict]:
        """Generate HA entity configurations."""
        entities = []
        for char in self.characteristics.values():
            entities.append({
                "platform": "sensor",
                "device_class": char.device_class,
                "state_class": char.state_class,
                "unit_of_measurement": char.unit,
                "name": f"BLE {char.name}"
            })
        return entities
```

## Benefits of This Architecture

1. **Clean Separation**: Each layer has a single responsibility
2. **Testability**: Each layer can be tested independently
3. **Reusability**: GATT layer can work without HA
4. **Maintainability**: Changes in one layer don't affect others
5. **Extensibility**: Easy to add new characteristics or HA features

### Real-World Example

Here's how the three layers work together for a heart rate sensor:

```python
# 1. GATT Layer - Pure Bluetooth parsing
from ble_gatt_device.gatt.characteristics.heart_rate_measurement import HeartRateMeasurementCharacteristic

# Raw BLE data from heart rate sensor
raw_data = bytearray([0x16, 0x5A, 0x03, 0xE8])

# Parse using Bluetooth SIG specification
hr_char = HeartRateMeasurementCharacteristic()
parsed_data = hr_char.parse_value(raw_data)
# Result: {"heart_rate": 90, "sensor_contact_detected": True, "energy_expended": 1000}

# 2. Translation Layer - HA format conversion
ha_data = {
    "state": parsed_data["heart_rate"],
    "attributes": {
        "device_class": hr_char.device_class,  # "heart_rate"
        "state_class": hr_char.state_class,    # "measurement" 
        "unit_of_measurement": hr_char.unit,   # "bpm"
        "sensor_contact": parsed_data["sensor_contact_detected"],
        "energy_expended": parsed_data.get("energy_expended")
    }
}

# 3. HA Integration Layer - Entity creation (Future)
# This layer would create actual HA entities using the translated data
```

### Testing Strategy

Each layer can be tested independently:

```python
# Test GATT layer parsing
def test_heart_rate_parsing():
    char = HeartRateMeasurementCharacteristic()
    data = bytearray([0x16, 0x5A])
    result = char.parse_value(data)
    assert result["heart_rate"] == 90

# Test translation layer
def test_ha_translation():
    char = HeartRateMeasurementCharacteristic()
    raw_data = {"heart_rate": 90, "sensor_contact_detected": True}
    ha_data = translate_heart_rate_data(char, raw_data)
    assert ha_data["attributes"]["device_class"] == "heart_rate"

# Test HA integration (when implemented)
def test_ha_entity_creation():
    # Mock HA environment and test entity behavior
    pass
```

## Migration and Compatibility

### From v0.2.0 to v0.3.0

All existing GATT layer code remains compatible. New features added:

- HA metadata properties on all characteristics
- Translation layer foundation
- Enhanced architectural validation

### Future HA Integration

When the HA integration layer is implemented:

1. Install as HA custom component
2. Configure BLE device discovery
3. Automatic entity creation from GATT characteristics
4. Real-time data updates via BLE notifications

The clean architecture ensures smooth migration and zero impact on existing GATT functionality.
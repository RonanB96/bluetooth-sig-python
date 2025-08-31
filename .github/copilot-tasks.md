# AI Coding Agent Development Tasks

This file contains detailed development tasks for AI coding agents working on the BLE GATT Device framework.

## Current Development Tasks 🔄

### 1. Expand Sensor Characteristics 
**Priority: High** | **Status: In Progress**

Implement missing sensor characteristics from Bluetooth SIG registry to expand device compatibility.

#### Missing Sensor Characteristics to Implement:

**Environmental Sensors:**
- Light/Illuminance Characteristic (0x2AFB) - Illuminance measurement in lux
- Sound Level Characteristic (0x2B28) - Sound pressure level in dBA
- Apparent Wind Direction (0x2A73) - Wind direction measurement
- Apparent Wind Speed (0x2A72) - Wind speed measurement
- Dew Point (0x2A7B) - Dew point temperature
- Heat Index (0x2A7A) - Heat index temperature
- Rainfall (0x2A78) - Rainfall measurement
- Irradiance (0x2A77) - Solar irradiance measurement

**Motion and Orientation:**
- Magnetic Declination (0x2A2C) - Magnetic declination angle
- Magnetic Flux Density 2D (0x2AA0) - 2D magnetic field measurement
- Magnetic Flux Density 3D (0x2AA1) - 3D magnetic field measurement

**Air Quality:**
- Sulfur Dioxide Concentration (0x2BD0) - SO2 gas concentration
- Nitrogen Dioxide Concentration (0x2BCE) - NO2 gas concentration
- Carbon Monoxide Concentration (0x2BD6) - CO gas concentration
- Particulate Matter PM1 (0x2BD5) - PM1.0 particle concentration
- Particulate Matter PM2.5 (0x2BD1) - PM2.5 particle concentration
- Particulate Matter PM10 (0x2BD2) - PM10 particle concentration
- Volatile Organic Compounds (0x2BE7) - VOC concentration

#### Implementation Checklist:
- [ ] Create individual characteristic files for each sensor type
- [ ] Implement proper data parsing with correct units
- [ ] Add characteristics to Environmental Sensing Service
- [ ] Create comprehensive test coverage
- [ ] Update characteristic registry with new types
- [ ] Validate UUID resolution and name parsing
- [ ] Test with real device data where possible

#### File Structure:
```
src/ble_gatt_device/gatt/characteristics/
├── sensors/
│   ├── __init__.py
│   ├── light.py               # IlluminanceCharacteristic
│   ├── sound.py               # SoundLevelCharacteristic  
│   ├── wind.py                # Wind direction/speed characteristics
│   ├── air_quality.py         # Gas concentration characteristics
│   └── magnetic.py            # Magnetic field characteristics
```

### 2. Add Major Services
**Priority: Medium** | **Status: Planned**

Expand service coverage beyond the current 4 services:

#### Services to Implement:
- **Health Thermometer Service (0x1809)** - Medical temperature readings
- **Heart Rate Service (0x180D)** - Pulse and heart rate monitoring  
- **Blood Pressure Service (0x1810)** - Blood pressure measurements
- **Glucose Service (0x1808)** - Blood glucose monitoring
- **Cycling Power Service (0x1818)** - Bicycle power meter data
- **Running Speed and Cadence (0x1814)** - Running metrics
- **Location and Navigation Service (0x1819)** - GPS and navigation data

### 3. Convert Scripts to Pytest  
**Priority: Medium** | **Status: Planned**

Improve test coverage and CI integration:

- [ ] Convert `scripts/test_*.py` to proper pytest test cases
- [ ] Add integration tests for real device connections  
- [ ] Create mock device testing framework
- [ ] Add performance benchmarking tests
- [ ] Set up GitHub Actions CI/CD pipeline

### 4. Home Assistant Architecture
**Priority: Low** | **Status: Planned**

Clean separation between GATT and HA integration layers:

- [ ] Create HA translation layer (`src/ble_gatt_device/homeassistant/`)
- [ ] Implement device class mappings for HA entities
- [ ] Add state class and device class properties
- [ ] Create HA custom component structure
- [ ] Add configuration flow for device discovery

## Implementation Guidelines

### Sensor Characteristic Pattern
Each sensor characteristic should follow this pattern:

```python
@dataclass
class ExampleSensorCharacteristic(BaseCharacteristic):
    """Example sensor measurement characteristic."""
    
    _characteristic_name: str = "Example Sensor"
    
    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"  # or int, string, boolean, bytes
        super().__post_init__()
    
    def parse_value(self, data: bytearray) -> float:
        """Parse sensor data according to Bluetooth SIG specification."""
        if len(data) < 2:
            raise ValueError("Sensor data must be at least 2 bytes")
        
        # Implement parsing according to spec
        raw_value = int.from_bytes(data[:2], byteorder="little", signed=False)
        return raw_value * 0.01  # Apply scaling factor
    
    @property 
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "unit"  # e.g., "lux", "dBA", "°", "m/s", "μg/m³"
```

### Testing Requirements
- All characteristics must pass UUID resolution tests
- Parsing functions must handle edge cases (empty data, malformed data)
- Integration tests should validate against real device patterns
- Performance tests for parsing large datasets

### Documentation Standards
- Each characteristic needs comprehensive docstring
- Include reference to Bluetooth SIG specification
- Document data format and scaling factors
- Provide example usage in device integration
# BLE GATT Device Framework

A comprehensive registry-driven BLE GATT framework with real device integration and Home Assistant compatibility. This project provides a robust, extensible architecture for BLE device communication with automatic UUID resolution, data parsing, and clean separation between Bluetooth and application layers.

## Features

- **Registry-Driven Architecture**: YAML-based UUID registry with automatic class name resolution
- **Real Device Integration**: Bleak-based BLE connection with optimized timeouts (10s for reliability)
- **Data Parsing Framework**: Convert raw BLE data to meaningful sensor values with units
- **Home Assistant Ready**: Clean separation between GATT and HA integration layers
- **Comprehensive Testing**: 56+ validation tests covering all services and characteristics
- **Type-Safe Implementation**: Complete type hints and dataclass-based design

## Supported GATT Services

### Core Services

- **Automation IO Service (0x181C)**
  - Electric Current (0x2AEE)
  - Voltage (0x2B18)
  - Average Current (0x2AE0)
  - Average Voltage (0x2AE1)
  - Electric Current Range (0x2AEF)
  - Electric Current Specification (0x2AF0)
  - Electric Current Statistics (0x2AF1)
  - Voltage Specification (0x2B19)
  - Voltage Statistics (0x2B1A)
  - High Voltage (0x2B3A)
  - Voltage Frequency (0x2B4C)
  - Supported Power Range (0x2A66)
  - Tx Power Level (0x2A07)

- **Battery Service (0x180F)**
  - Battery Level (0x2A19)
  
- **Device Information Service (0x180A)**
  - Manufacturer Name String (0x2A29)
  - Model Number String (0x2A24)
  - Serial Number String (0x2A25)
  - Hardware Revision String (0x2A27)
  - Firmware Revision String (0x2A26)
  - Software Revision String (0x2A28)
  
- **Environmental Sensing Service (0x181A)**
  - Temperature (0x2A6E)
  - Humidity (0x2A6F)
  - Pressure (0x2A6D)
  - UV Index (0x2A76)
  - Illuminance (0x2A77)
  - Sound Pressure Level (Power Specification)
  
- **Generic Access Profile (0x1800)**
  - Device Name (0x2A00)
  - Appearance (0x2A01)

- **Health Thermometer Service (0x1809)**
  - Temperature Measurement (0x2A1C)
  
- **Heart Rate Service (0x180D)**
  - Heart Rate Measurement (0x2A37)
  - Blood Pressure Measurement (0x2A35)
  - Pulse Oximetry Measurement (PLX Continuous Measurement)
  
- **Running Speed and Cadence Service (0x1814)**
  - RSC Measurement (0x2A53)
  
- **Cycling Speed and Cadence Service (0x1816)**
  - CSC Measurement (0x2A5B)

- **Cycling Power Service (0x1818)**
  - Cycling Power Measurement (0x2A63)
  - Cycling Power Feature (0x2A65)
  - Cycling Power Vector (0x2A64)
  - Cycling Power Control Point (0x2A66)

- **Body Composition Service (0x181B)**
  - Body Composition Measurement (0x2A9C)
  - Body Composition Feature (0x2A9B)

- **Weight Scale Service (0x181D)**
  - Weight Measurement (0x2A9D)
  - Weight Scale Feature (0x2A9E)

### Registry Coverage

- **Comprehensive characteristics** fully implemented with validation
- **Complete Bluetooth SIG compliance** via official UUID registry
- **Automatic name resolution** with multiple format attempts

## Architecture

### Four-Layer Design

1. **UUID Registry** (`src/ble_gatt_device/gatt/uuid_registry.py`): Loads Bluetooth SIG official UUIDs from YAML files
2. **Base Classes** (`src/ble_gatt_device/gatt/{services,characteristics}/base.py`): Automatic UUID resolution via class name parsing
3. **Implementations**: Concrete services/characteristics with data parsing capabilities
4. **Real Device Integration** (`src/ble_gatt_device/core.py`): Bleak-based BLE connection and data parsing

### Key Architectural Principles

- **Name-Based UUID Resolution**: `BatteryService` → "Battery" → UUID "180F"
- **Clean Layer Separation**: GATT ← Translation ← Home Assistant (never reverse)
- **Data Parsing**: Raw bytes → meaningful values with units
- **Connection Optimization**: 10-second timeout for reliable device connections
- **Type Safety**: Complete type hints throughout the framework

### Testing Framework

- **56+ Comprehensive Tests**: Full validation of services, characteristics, and registry
- **Dynamic Discovery**: Automatic detection of all service and characteristic classes  
- **Real Device Testing**: Scripts for testing with actual BLE hardware (Nordic Thingy:52 validated)
- **Registry Validation**: Ensures all implementations match Bluetooth SIG standards
- **Architecture Separation**: Validates clean layer boundaries between GATT and HA

## Home Assistant Integration Architecture

The framework follows a strict three-layer architecture designed for Home Assistant integration:

### Architecture Layers

```
Home Assistant Integration Layer (Future)
            ↓ (calls)
    Translation Layer (HA Metadata)
            ↓ (calls)
       GATT Layer (Pure Bluetooth)
```

### Layer Responsibilities

1. **GATT Layer** (`src/ble_gatt_device/gatt/`):
   - Pure Bluetooth functionality with no Home Assistant dependencies
   - Raw BLE data parsing according to Bluetooth SIG specifications
   - Metadata properties for translation layer (`device_class`, `state_class`, `unit`)
   - Characteristic and service implementations with automatic UUID resolution

2. **Translation Layer** (`src/ble_gatt_device/gatt/ha_translation.py`):
   - Converts GATT data to Home Assistant-compatible format
   - Maps BLE characteristics to HA entity types
   - Handles unit conversions and data normalization
   - Provides HA entity configuration

3. **Home Assistant Integration Layer** (External/Future):
   - Creates actual HA entities and handles HA-specific logic
   - Manages device discovery and entity lifecycle
   - Handles HA configuration and state management

### Key Benefits

- **Clean Separation**: Each layer has a single responsibility
- **Testability**: Each layer can be tested independently  
- **Reusability**: GATT layer works without Home Assistant
- **Maintainability**: Changes in one layer don't affect others
- **Extensibility**: Easy to add new characteristics or HA features

### Example Implementation

```python
# GATT Layer - Pure Bluetooth
from ble_gatt_device.gatt.characteristics.temperature import TemperatureCharacteristic

temp_char = TemperatureCharacteristic()
raw_value = temp_char.parse_value(bytearray([0x64, 0x09]))  # 24.36°C

# Translation Layer - HA Metadata
ha_config = {
    "device_class": temp_char.device_class,  # "temperature"
    "state_class": temp_char.state_class,    # "measurement"
    "unit_of_measurement": temp_char.unit,   # "°C"
    "value": raw_value
}
```

## Real Device Integration

### Supported Devices

- **Nordic Thingy:52**: Environmental sensor with battery, temperature, humidity, pressure
- **Connection Requirements**: 10-second timeout for reliable service discovery
- **Services Tested**: Battery (180F), Environmental Sensing (181A), Device Information (180A)

### Testing Commands

```bash
# Scan for BLE devices
python scripts/test_real_device.py scan

# Test connection to specific device  
python scripts/test_real_device.py AA:BB:CC:DD:EE:FF

# Debug connection issues
python scripts/test_real_device_debug.py AA:BB:CC:DD:EE:FF

# Test parsing with simulated data
python scripts/test_parsing.py
```

## Development Setup

### Prerequisites

- Python 3.9+ (tested with 3.9, 3.10, 3.11, 3.12)
- Git

### Installation

1. Clone the repository:

```bash
git clone https://github.com/RonanB96/ble_gatt_device.git
cd ble_gatt_device
```

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

1. Install development dependencies:

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run core validation tests (56+ tests)
python -m pytest tests/test_registry_validation.py -v

# Quick validation check
python tests/test_registry_validation.py

# Run with coverage
pytest --cov=src/ble_gatt_device tests/
```

### Development Scripts

The project includes several utility scripts for development and testing:

```bash
# Core framework validation
python tests/test_registry_validation.py

# Real device testing
python scripts/test_real_device.py scan
python scripts/test_real_device.py <MAC_ADDRESS>

# Data parsing testing  
python scripts/test_parsing.py
python scripts/test_core.py
```

## Usage Examples

### Real Device Connection

```python
from ble_gatt_device.core import BLEGATTDevice
import asyncio

async def read_device_data():
    device = BLEGATTDevice("AA:BB:CC:DD:EE:FF")
    
    # Read raw characteristics data
    raw_data = await device.read_characteristics()
    print(f"Raw data: {raw_data}")
    
    # Read parsed data with units
    parsed_data = await device.read_parsed_characteristics()
    print(f"Parsed data: {parsed_data}")

asyncio.run(read_device_data())
```

### Basic Service Usage

```python
from ble_gatt_device.gatt.services.battery_service import BatteryService
from ble_gatt_device.gatt.characteristics.battery_level import BatteryLevelCharacteristic

# Create service instance
battery_service = BatteryService()
print(f"Service UUID: {battery_service.SERVICE_UUID}")  # 180F

# Get expected characteristics
characteristics = battery_service.get_expected_characteristics()
print(characteristics)  # {'Battery Level': BatteryLevelCharacteristic}

# Parse characteristic data
char = BatteryLevelCharacteristic()
value = char.parse_value(bytearray([85]))  # 85% battery
print(f"Battery level: {value}{char.unit}")  # Battery level: 85%
```

### Health Monitoring Examples

```python
from ble_gatt_device.gatt.characteristics.heart_rate_measurement import HeartRateMeasurementCharacteristic
from ble_gatt_device.gatt.characteristics.temperature_measurement import TemperatureMeasurementCharacteristic

# Heart rate measurement with multiple data fields
hr_char = HeartRateMeasurementCharacteristic()
hr_data = bytearray([0x16, 0x5A, 0x03, 0xE8])  # Complex HR data
parsed_hr = hr_char.parse_value(hr_data)
print(f"Heart rate: {parsed_hr['heart_rate']}{hr_char.unit}")
print(f"Sensor contact: {parsed_hr['sensor_contact_detected']}")

# Medical-grade temperature measurement (IEEE-11073 format)
temp_char = TemperatureMeasurementCharacteristic()
temp_data = bytearray([0x00, 0xFF, 0x54, 0x16, 0x00, 0xFE])  # IEEE-11073 format
parsed_temp = temp_char.parse_value(temp_data)
print(f"Body temperature: {parsed_temp['temperature']:.1f}{temp_char.unit}")
```

### Environmental Sensing Examples

```python
from ble_gatt_device.gatt.characteristics.illuminance import IlluminanceCharacteristic
from ble_gatt_device.gatt.characteristics.sound_pressure_level import SoundPressureLevelCharacteristic

# Light level measurement
light_char = IlluminanceCharacteristic()
light_data = bytearray([0x10, 0x27])  # 10000 lux
light_level = light_char.parse_value(light_data)
print(f"Illuminance: {light_level}{light_char.unit}")

# Sound pressure level
sound_char = SoundPressureLevelCharacteristic()
sound_data = bytearray([0x32])  # 50 dB
sound_level = sound_char.parse_value(sound_data)
print(f"Sound level: {sound_level}{sound_char.unit}")
```

### Fitness Tracking Examples

```python
from ble_gatt_device.gatt.characteristics.rsc_measurement import RSCMeasurementCharacteristic
from ble_gatt_device.gatt.characteristics.csc_measurement import CSCMeasurementCharacteristic

# Running speed and cadence
rsc_char = RSCMeasurementCharacteristic()
rsc_data = bytearray([0x03, 0x32, 0x00, 0x00, 0x96])  # Speed + cadence
parsed_rsc = rsc_char.parse_value(rsc_data)
print(f"Running speed: {parsed_rsc['instantaneous_speed']:.1f} m/s")
print(f"Cadence: {parsed_rsc['instantaneous_cadence']} steps/min")

# Cycling speed and cadence
csc_char = CSCMeasurementCharacteristic()
csc_data = bytearray([0x03, 0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC])
parsed_csc = csc_char.parse_value(csc_data)
print(f"Wheel revolutions: {parsed_csc['cumulative_wheel_revolutions']}")
print(f"Crank revolutions: {parsed_csc['cumulative_crank_revolutions']}")
```

### UUID Registry Usage

```python
from ble_gatt_device.gatt.uuid_registry import uuid_registry

# Look up service by name
service_info = uuid_registry.get_service_info("Battery")
print(f"UUID: {service_info.uuid}, ID: {service_info.id}")

# Look up characteristic by UUID
char_info = uuid_registry.get_characteristic_info("2A19")
print(f"Name: {char_info.name}, Properties: {char_info.properties}")
```

## Project Status & Roadmap

### Completed ✅

- **Registry-Driven Architecture**: Complete base classes and UUID registry system
- **Real Device Integration**: Bleak-based BLE connection with working Nordic Thingy:52 support
- **Data Parsing Framework**: Convert raw bytes to meaningful sensor values with units  
- **Service Implementation**: 8 major GATT services with 20+ characteristics
- **Health & Fitness Services**: Heart rate, blood pressure, pulse oximetry, temperature measurement
- **Sports Monitoring**: Running and cycling speed and cadence measurements
- **Environmental Sensing**: Temperature, humidity, pressure, UV index, illuminance, sound pressure
- **Home Assistant Integration**: Complete 3-layer architecture (GATT → Translation → HA)
- **IEEE-11073 Support**: Medical device data format parsing utilities
- **Testing Framework**: 56+ comprehensive tests with dynamic discovery
- **Connection Optimization**: 10-second timeout for reliable device compatibility

### Current Development Tasks 🔄

See `.github/copilot-tasks.md` for detailed agent tasks:

1. **Additional Health Services**: Weight Scale, Glucose monitoring, Blood Oxygen
2. **Enhanced HA Integration**: Auto-discovery and entity configuration
3. **Performance Optimization**: Real-time data streaming and connection pooling
4. **Extended Environmental Sensors**: Air quality, noise monitoring, light sensors

### Future Roadmap 🚀

- **Dynamic Service Discovery**: Automatic detection of device capabilities
- **Advanced Error Handling**: Reconnection strategies and fault tolerance
- **Performance Optimization**: Connection pooling and data caching
- **Custom UUID Support**: User-defined services and characteristics
- **Home Assistant Custom Component**: Full HA integration with UI

## Contributing

See `.github/copilot-tasks.md` for current development priorities and agent tasks.

### Development Workflow

1. Fork the repository
1. Create a feature branch (`git checkout -b feature/amazing-feature`)
1. Make your changes with tests
1. Run the test suite (`pytest`)
1. Ensure architectural separation (GATT ← Translation ← HA)
1. Commit your changes (`git commit -m 'Add amazing feature'`)
1. Push to the branch (`git push origin feature/amazing-feature`)
1. Open a Pull Request

### Adding New Services

1. Create service class inheriting from `BaseGattService`
1. Implement required methods and characteristics mapping
1. Add to `src/ble_gatt_device/gatt/services/__init__.py`
1. Add corresponding test cases
1. Ensure UUID exists in registry

### Adding New Characteristics

1. Create characteristic class inheriting from `BaseCharacteristic`
1. Implement `parse_value()` method for data parsing
1. Add `unit`, `device_class`, `state_class` properties for HA metadata
1. Add to appropriate service's expected characteristics
1. Maintain clean separation: no HA imports in GATT layer

## Dependency Management and Security

### Automated Dependency Updates

This project uses [Dependabot](https://docs.github.com/en/code-security/dependabot) to automatically manage dependency updates:

- **Python dependencies**: Weekly updates on Mondays for packages in `pyproject.toml`
- **GitHub Actions**: Weekly updates on Mondays for workflow dependencies
- **Security updates**: Applied immediately when vulnerabilities are detected
- **Grouped updates**: Related dependencies are updated together to reduce PR noise

### Security Alerts

GitHub security alerts are enabled for this repository to automatically detect known vulnerabilities in dependencies. When a security vulnerability is found:

1. A security alert is created in the repository
2. Dependabot automatically creates a pull request with the security fix
3. The maintainers are notified via GitHub notifications

### Enabling Security Features

Repository maintainers can ensure security features are enabled:

1. **Dependabot security updates**: Go to Settings → Security & analysis → Dependabot security updates
2. **Dependabot alerts**: Go to Settings → Security & analysis → Dependabot alerts  
3. **Security advisories**: Go to Settings → Security & analysis → Private vulnerability reporting

For more information, see the [GitHub documentation on managing security and analysis settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-security-and-analysis-settings-for-your-repository).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Bluetooth SIG** for the official UUID registry
- **Home Assistant Community** for inspiration and standards
- **Bleak Library** for cross-platform BLE support

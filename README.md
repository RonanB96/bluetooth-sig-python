# Bluetooth SIG Standards Library

[![Coverage Status](https://img.shields.io/endpoint?url=https://ronanb96.github.io/bluetooth-sig-python/coverage/coverage-badge.json)](https://ronanb96.github.io/bluetooth-sig-python/coverage/)

A pure Python library for Bluetooth SIG standards interpretation, providing comprehensive GATT characteristic and service parsing with automatic UUID resolution. This project offers a robust, standards-compliant architecture for Bluetooth device communication with type-safe data parsing and clean API design.

## Features

- **Standards-Based Architecture**: Official Bluetooth SIG YAML registry with automatic UUID resolution
- **Type-Safe Data Parsing**: Convert raw Bluetooth data to meaningful sensor values with comprehensive typing
- **Modern Python API**: Dataclass-based design with Python 3.9+ compatibility
- **Comprehensive Coverage**: Support for 70+ GATT characteristics across multiple service categories
- **Production Ready**: Extensive validation, perfect code quality scores, and comprehensive testing

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
  - Battery Level Status (0x2BED)

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
  - Dew Point (0x2A7B)
  - Heat Index (0x2A7A)
  - Wind Chill (0x2A79)
  - True Wind Speed (0x2A70)
  - True Wind Direction (0x2A71)
  - Apparent Wind Speed (0x2A72)
  - Apparent Wind Direction (0x2A73)
  - CO2 Concentration (0x2B8C)
  - TVOC Concentration (0x2BE7)
  - Ammonia Concentration (0x2BCF)
  - Methane Concentration (0x2BD1)
  - Nitrogen Dioxide Concentration (0x2BD2)
  - Ozone Concentration (0x2BD4)
  - PM1 Concentration (0x2BD5)
  - PM2.5 Concentration (0x2BD6)
  - PM10 Concentration (0x2BD7)
  - Sulfur Dioxide Concentration (0x2BD8)

- **Generic Access Profile (0x1800)**
  - Device Name (0x2A00)
  - Appearance (0x2A01)

- **Health Thermometer Service (0x1809)**
  - Temperature Measurement (0x2A1C)

- **Heart Rate Service (0x180D)**
  - Heart Rate Measurement (0x2A37)
  - Blood Pressure Measurement (0x2A35)
  - Pulse Oximetry Measurement (PLX Continuous Measurement)

- **Glucose Monitoring Service (0x1808)**
  - Glucose Measurement (0x2A18) - Core glucose readings with IEEE-11073 SFLOAT
  - Glucose Measurement Context (0x2A34) - Carbohydrate, exercise, medication data
  - Glucose Feature (0x2A51) - Device capabilities bitmap

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
- **Multiple services** including glucose monitoring, environmental sensing, and health tracking
- **Complete Bluetooth SIG compliance** via official UUID registry
- **Automatic name resolution** with multiple format attempts

## Architecture

### Clean API Design

1. **UUID Registry** (`src/bluetooth_sig/gatt/uuid_registry.py`): Loads official Bluetooth SIG UUIDs from YAML
2. **Standards Parser** (`src/bluetooth_sig/core.py`): Type-safe parsing with dataclass returns
3. **Characteristic Library**: Standards-compliant implementations for 70+ characteristics
4. **Service Definitions**: Official GATT service specifications with automatic discovery

### Key Architectural Principles

- **Standards Compliance**: Direct interpretation of official Bluetooth SIG specifications
- **Type Safety**: Rich dataclass returns with comprehensive validation
- **Modern Python**: Python 3.9+ compatibility with future annotations support
- **Clean API**: Intuitive method names with consistent return types

### Testing Framework

- **Comprehensive Validation**: Full coverage of standards interpretation and UUID resolution
- **Type Safety Testing**: Validation of dataclass parsing and return types
- **Standards Compliance**: Tests ensure correct interpretation of Bluetooth SIG specifications
- **Quality Metrics**: Perfect pylint scores and comprehensive linting validation

## API Examples

### Basic UUID Resolution

```python
from bluetooth_sig.core import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Resolve UUIDs to human-readable information
uuid_info = translator.resolve_uuid("180F")
print(f"Service: {uuid_info.name}")  # "Battery Service"

char_info = translator.resolve_uuid("2A19")
print(f"Characteristic: {char_info.name}")  # "Battery Level"
```

### Standards-Based Parsing

```python
# Parse characteristic data according to Bluetooth SIG standards
from bluetooth_sig.core import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Parse battery level data
parsed = translator.parse_characteristic_data("2A19", bytearray([85]))
print(f"Battery: {parsed.value}%")  # "Battery: 85%"

# Parse temperature data
parsed = translator.parse_characteristic_data("2A6E", bytearray([0x64, 0x09]))
print(f"Temperature: {parsed.value}°C")  # "Temperature: 24.36°C"
```

## Framework-Agnostic BLE Integration

The `bluetooth_sig` library is designed to work with **any BLE connection library**. It provides pure SIG standards parsing while you choose your preferred BLE library for connections.

### Integration Pattern

```python
# Step 1: Get raw data (using ANY BLE library)
raw_data = await your_ble_library.read_characteristic(device, uuid)

# Step 2: Parse with bluetooth_sig (connection-agnostic)
from bluetooth_sig import BluetoothSIGTranslator
translator = BluetoothSIGTranslator()
result = translator.parse_characteristic(uuid, raw_data)

# Step 3: Use parsed result
print(f"Value: {result.value} {result.unit}")
```

### Supported BLE Libraries

The same parsing code works with all BLE libraries:

- **bleak** - Cross-platform async BLE library *(recommended)*
- **bleak-retry-connector** - Robust connections with retry logic *(recommended for production)*
- **simplepyble** - Cross-platform sync BLE library
- **Any custom BLE implementation**

### Examples

See the [`examples/`](examples/) directory for comprehensive integration examples:

- [`pure_sig_parsing.py`](examples/pure_sig_parsing.py) - Pure SIG parsing without BLE connections
- [`with_bleak.py`](examples/with_bleak.py) - Integration with Bleak
- [`with_bleak_retry.py`](examples/with_bleak_retry.py) - Production-ready robust connections
- [`with_simpleble.py`](examples/with_simpleble.py) - Alternative BLE library integration
- [`library_comparison.py`](examples/library_comparison.py) - Compare multiple BLE libraries
- [`testing_with_mocks.py`](examples/testing_with_mocks.py) - Testing without BLE hardware

All examples demonstrate the same core principle: **bluetooth_sig provides pure SIG standards parsing that works identically across all BLE libraries**.

## Development Setup

### Prerequisites

- Python 3.9+ (tested with 3.9, 3.10, 3.11, 3.12)
- Git

### Installation

1. Clone the repository:

```bash
git clone https://github.com/RonanB96/bluetooth-sig-python.git
cd bluetooth-sig-python
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

# Run core validation tests
python -m pytest tests/test_registry_validation.py -v

# Run with coverage
pytest --cov=src/bluetooth_sig tests/
```

### Development Scripts

The project includes utility scripts for validation and testing:

```bash
# Core validation
python -m pytest tests/test_registry_validation.py -v

# Standards compliance testing
python -m pytest tests/test_data_parsing.py -v
```

## Detailed Usage Examples

### UUID Information Resolution

```python
from bluetooth_sig.core import BluetoothSIGTranslator

translator = BluetoothSIGTranslator()

# Get comprehensive service information
service_info = translator.resolve_uuid("180F")  # Battery Service
print(f"Name: {service_info.name}")
print(f"Type: {service_info.type}")  # "service"
print(f"UUID: {service_info.uuid}")

# Get comprehensive characteristic information
char_info = translator.resolve_uuid("2A19")  # Battery Level
print(f"Name: {char_info.name}")
print(f"Type: {char_info.type}")  # "characteristic"
print(f"UUID: {char_info.uuid}")
```

### Name-Based UUID Resolution

```python
# Resolve by human-readable names
battery_service = translator.resolve_name("Battery Service")
print(f"UUID: {battery_service.uuid}")  # "180F"

battery_level = translator.resolve_name("Battery Level")
print(f"UUID: {battery_level.uuid}")  # "2A19"
```

### Data Parsing with Standards Compliance

```python
# Parse various characteristic data types
translator = BluetoothSIGTranslator()

# Battery level (uint8 percentage)
battery_data = translator.parse_characteristic_data("2A19", bytearray([85]))
print(f"Battery: {battery_data.value}%")

# Temperature (sint16, 0.01°C resolution)
temp_data = translator.parse_characteristic_data("2A6E", bytearray([0x64, 0x09]))
print(f"Temperature: {temp_data.value}°C")

# Humidity (uint16, 0.01% resolution)
humidity_data = translator.parse_characteristic_data("2A6F", bytearray([0x3A, 0x13]))
print(f"Humidity: {humidity_data.value}%")
```

## Standards Coverage

This library provides comprehensive support for official Bluetooth SIG standards:

### Supported Standards Categories

- **Core Device Information**: Manufacturer, model, firmware details
- **Battery Management**: Level, power state, and charging status
- **Environmental Sensors**: Temperature, humidity, pressure, air quality
- **Health Monitoring**: Heart rate, blood pressure, glucose, body composition
- **Fitness Tracking**: Running, cycling speed/cadence, power measurement
- **Device Communication**: Generic access and automation protocols

### Bluetooth SIG Compliance

- **Official Registry**: Direct YAML parsing from Bluetooth SIG assigned numbers
- **Standards Validation**: Comprehensive testing against official specifications
- **Type Safety**: Rich dataclass returns with proper validation
- **Coverage**: Support for 70+ official GATT characteristics across all major categories

## Testing

The library includes comprehensive test coverage with standards validation:

```bash
python -m pytest tests/ -v
```

## Contributing

We welcome contributions! This project follows Bluetooth SIG standards for consistent specification interpretation.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Adding New Standards Support

1. Identify the official Bluetooth SIG specification
2. Add characteristic parsing logic following existing patterns
3. Include comprehensive unit tests with official test vectors
4. Ensure type safety with proper dataclass definitions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Bluetooth SIG** for the official standards and UUID registry
- **Python Community** for excellent tooling and libraries


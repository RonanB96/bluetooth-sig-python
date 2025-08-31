# BLE GATT Device Framework

A comprehensive registry-driven BLE GATT framework with real device integration and Home Assistant compatibility. This project provides a robust, extensible architecture for BLE device communication with automatic UUID resolution, data parsing, and clean separation between Bluetooth and application layers.

## Features

- **Registry-Driven Architecture**: YAML-based UUID registry with automatic class name resolution
- **Real Device Integration**: Bleak-based BLE connection with optimized timeouts (10s for reliability)
- **Data Parsing Framework**: Convert raw BLE data to meaningful sensor values with units
- **Home Assistant Ready**: Clean separation between GATT and HA integration layers
- **Comprehensive Testing**: 80+ validation tests covering all services and characteristics
- **Type-Safe Implementation**: Complete type hints and dataclass-based design

## Supported GATT Services

### Core Services (4 implemented)

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
  
- **Generic Access Profile (0x1800)**
  - Device Name (0x2A00)
  - Appearance (0x2A01)

### Registry Coverage

- **13 Characteristics** fully implemented with validation
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

- **80+ Comprehensive Tests**: Full validation of services, characteristics, and registry
- **Dynamic Discovery**: Automatic detection of all service and characteristic classes  
- **Real Device Testing**: Scripts for testing with actual BLE hardware (Nordic Thingy:52 validated)
- **Registry Validation**: Ensures all implementations match Bluetooth SIG standards
- **Architecture Separation**: Validates clean layer boundaries between GATT and HA

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

# Run core validation tests (80+ tests)
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
- **Service Implementation**: 4 major GATT services with 13 characteristics
- **Testing Framework**: 80+ comprehensive tests with dynamic discovery
- **Connection Optimization**: 10-second timeout for reliable device compatibility

### Current Development Tasks 🔄

See `.github/copilot-tasks.md` for detailed agent tasks:

1. **Expand Sensor Characteristics**: Implement missing sensor characteristics from YAML registry
2. **Add Major Services**: Environmental Sensing Service (ESS), Health services, etc.
3. **Convert Scripts to Pytest**: Improve test coverage and CI integration
4. **Home Assistant Architecture**: Clean separation between GATT and HA integration layers

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

# Bluetooth SIG Standards Library Architecture

**Updated: September 2025**

## Current Implementation Status

### ✅ Phase 1: Complete - Core GATT Layer with Modern API
- **BluetoothSIGTranslator**: Pure SIG standards translation with type-safe dataclasses
- **Registry-driven UUID resolution**: Multi-stage intelligent name parsing
- **Modern Python syntax**: Using `Class | None` unions with `__future__` annotations for Python 3.9+ compatibility
- **Rich return types**: Structured dataclasses instead of primitive types
- **Comprehensive validation**: 70+ characteristics, extensive test suite
- **Real device integration**: Tested with Nordic Thingy:52 and other BLE devices

## Current API (Phase 1 - Implemented)

### Core BluetoothSIGTranslator API

```python
from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.core import (
    CharacteristicInfo,
    ServiceInfo,
    ParsedData,
    ValidationResult
)

# Initialize the pure SIG standards translator
translator = BluetoothSIGTranslator()
```

### 1. Characteristic Data Parsing (Production Ready)

```python
# Parse raw characteristic data with rich return types
result: ParsedData = translator.parse_characteristic("2A19", b"\x64")
print(f"Value: {result.value}")        # 100
print(f"Unit: {result.unit}")          # "%"
print(f"Type: {result.value_type}")    # "int"
print(f"Success: {result.parse_success}")  # True

# Batch processing for multiple characteristics
char_data = {
    "2A19": b"\x64",                   # Battery Level: 100%
    "2A6E": bytearray([0x90, 0x01]),   # Temperature: 4.0°C
}
results: dict[str, ParsedData] = translator.parse_characteristics(char_data)
```

### 2. SIG Information Lookup (Production Ready)

```python
# Get characteristic information by UUID
info: CharacteristicInfo | None = translator.get_characteristic_info("2A19")
if info:
    print(f"Name: {info.name}")           # "Battery Level"
    print(f"UUID: {info.uuid}")           # "2A19"
    print(f"Unit: {info.unit}")           # "%"
    print(f"Type: {info.value_type}")     # "int"

# Get service information
service: ServiceInfo | None = translator.get_service_info("180F")
if service:
    print(f"Name: {service.name}")        # "Battery Service"
    print(f"UUID: {service.uuid}")        # "180F"
```

### 3. Enhanced Resolution Methods (New in Current API)

```python
# NEW: Rich object resolution instead of simple strings
result: CharacteristicInfo | ServiceInfo | None = translator.resolve_uuid("Battery Level")
if result:
    print(f"Full info: {result}")  # Complete dataclass with all metadata

# UUID to rich information resolution
result: CharacteristicInfo | ServiceInfo | None = translator.resolve_name("2A19")
if result:
    print(f"Name: {result.name}, Unit: {result.unit}")

# Batch information retrieval
infos: dict[str, CharacteristicInfo | None] = translator.get_characteristics_info([
    "2A19", "2A6E", "2A1C"
])
```

### 4. Data Validation (Production Ready)

```python
# Validate characteristic data against SIG specifications
validation: ValidationResult = translator.validate_characteristic_data("2A19", b"\x64")
print(f"Valid: {validation.is_valid}")              # True
print(f"Length: {validation.actual_length}")        # 1
print(f"Error: {validation.error_message}")         # None if valid
```

### 5. Service Relationship Discovery

```python
# Get characteristics associated with a service
characteristics: list[str] = translator.get_service_characteristics("180F")
print(f"Battery service chars: {characteristics}")  # ["2A19", ...]

# List all supported characteristics
all_chars: dict[str, str] = translator.list_supported_characteristics()
print(f"Total characteristics: {len(all_chars)}")   # 70+

# List all supported services
all_services: dict[str, str] = translator.list_supported_services()
```

## Type-Safe Dataclass Architecture

### Core Dataclasses (Implemented)

```python
from __future__ import annotations  # Python 3.9+ compatibility

@dataclass
class SIGInfo:
    """Base information about Bluetooth SIG characteristics or services."""
    uuid: str
    name: str
    description: str | None = None

@dataclass
class CharacteristicInfo(SIGInfo):
    """Information about a Bluetooth characteristic."""
    value_type: str | None = None      # "int", "float", "string", etc.
    unit: str | None = None            # "%", "°C", "hPa", etc.
    properties: list[str] | None = None

@dataclass
class ServiceInfo(SIGInfo):
    """Information about a Bluetooth service."""
    characteristics: list[str] | None = None

@dataclass
class ParsedData(CharacteristicInfo):
    """Result of parsing characteristic data."""
    value: Any | None = None           # Parsed value with proper type
    raw_data: bytes | None = None      # Original raw bytes
    parse_success: bool = True         # Parse success indicator
    error_message: str | None = None   # Error details if failed

@dataclass
class ValidationResult(SIGInfo):
    """Result of data validation."""
    is_valid: bool = True
    expected_length: int | None = None
    actual_length: int | None = None
    error_message: str | None = None
```

```

## Integration Patterns (Production Ready)

### Pattern 1: Pure SIG Translation (Recommended Core Use Case)

```python
from bluetooth_sig import BluetoothSIGTranslator

def parse_sensor_reading(char_uuid: str, raw_data: bytes) -> ParsedData:
    """Pure SIG standard translation - no connection dependencies."""
    translator = BluetoothSIGTranslator()
    return translator.parse_characteristic(char_uuid, raw_data)

# Usage
result = parse_sensor_reading("2A19", b"\x64")
print(f"Battery: {result.value}{result.unit}")  # "Battery: 100%"
```

### Pattern 2: With bleak-retry-connector (Recommended for Applications)

```python
from bleak_retry_connector import establish_connection
from bleak import BleakClient
from bluetooth_sig import BluetoothSIGTranslator

async def read_device_sensors(address: str) -> dict[str, ParsedData]:
    """Read and parse device sensors using proven connection management."""
    translator = BluetoothSIGTranslator()
    results = {}

    async with establish_connection(BleakClient, address, timeout=10.0) as client:
        for service in await client.get_services():
            service_info = translator.get_service_info(service.uuid)
            if service_info:
                for char in service.characteristics:
                    try:
                        raw_data = await client.read_gatt_char(char.uuid)
                        parsed = translator.parse_characteristic(char.uuid, raw_data)
                        results[char.uuid] = parsed
                    except Exception as e:
                        print(f"Failed to read {char.uuid}: {e}")

    return results
```

### Pattern 3: Validation and Quality Assurance

```python
from bluetooth_sig import BluetoothSIGTranslator

async def robust_characteristic_read(client: BleakClient, char_uuid: str) -> ParsedData:
    """Read characteristic with validation and error handling."""
    translator = BluetoothSIGTranslator()

    # Read raw data
    raw_data = await client.read_gatt_char(char_uuid)

    # Validate data format
    validation = translator.validate_characteristic_data(char_uuid, raw_data)
    if not validation.is_valid:
        print(f"Validation warning for {char_uuid}: {validation.error_message}")

    # Parse with rich error information
    result = translator.parse_characteristic(char_uuid, raw_data)
    if not result.parse_success:
        print(f"Parse error: {result.error_message}")

    return result
```

## Planned API Improvements (Future Phases)

### Phase 2: GAP Layer - Advertisement Interpretation (Planned)

```python
# Future GAP API for advertisement interpretation
from bluetooth_sig.gap import AdvertisementInterpreter

# Enhanced advertisement analysis
interpreter = AdvertisementInterpreter()

# Resolve service UUIDs in advertisements with rich metadata
services = interpreter.resolve_services(["180F", "181A"])
# Returns: [ServiceInfo(uuid="180F", name="Battery Service"), ...]

# Analyze device capabilities from advertisements
capabilities = interpreter.analyze_device_capabilities(advertisement_data)
# Returns: DeviceCapabilities(services=[], estimated_features=[], compliance_level=...)

# SIG compliance validation
compliance = interpreter.validate_advertisement_compliance(advertisement_data)
# Returns: ComplianceResult(is_compliant=True, violations=[], recommendations=...)
```

### Phase 3: Enhanced Validation and Analysis (Planned)

```python
# Advanced validation capabilities
from bluetooth_sig.validation import SIGValidator

validator = SIGValidator()

# Deep characteristic validation against SIG specifications
result = validator.deep_validate_characteristic(
    uuid="2A19",
    data=raw_data,
    context={"service_uuid": "180F", "device_type": "sensor"}
)
# Returns: DetailedValidation(spec_compliance=True, range_check=True, context_valid=True)

# Service composition validation
service_validation = validator.validate_service_composition(
    service_uuid="180F",
    discovered_characteristics=["2A19", "2A1A"]
)
# Returns: ServiceValidation(required_chars_present=True, optional_chars=[], violations=[])
```

### Phase 4: Compiled Registry System (Performance Optimization)

```python
# Future compiled classes for zero-overhead access
from bluetooth_sig.compiled.characteristics import BatteryLevel2A19
from bluetooth_sig.compiled.services import BatteryService180F

# Direct instantiation with compile-time optimization
parser = BatteryLevel2A19()  # 1000x faster than runtime lookup
result = parser.parse_value(raw_data)

# Static service definitions
service = BatteryService180F()
required_chars = service.get_required_characteristics()  # Pre-compiled list
```

## Current Repository Structure

```text
bluetooth-sig-python/
├── src/
│   └── bluetooth_sig/                   # Core SIG Standards Library
│       ├── __init__.py                  # Exports BluetoothSIGTranslator
│       ├── core.py                      # ✅ Main API with dataclasses
│       └── gatt/                        # ✅ GATT Layer (Phase 1 Complete)
│           ├── characteristics/         # ✅ 70+ SIG Characteristic Parsers
│           ├── services/                # ✅ SIG Service Definitions
│           └── uuid_registry.py         # ✅ Registry-driven UUID resolution
├── tests/                               # ✅ Comprehensive test suite
│   ├── test_bluetooth_sig_translator.py # ✅ 16 API tests passing
│   ├── test_registry_validation.py     # ✅ 128+ characteristic tests
│   └── test_*.py                        # ✅ Full coverage
├── scripts/                             # ✅ Development and demo scripts
│   ├── test_real_device.py             # ✅ Real device testing
│   └── ble_debug.py                    # ✅ Enhanced with new API
├── docs/                                # ✅ Architecture documentation
└── bluetooth_sig/                      # ✅ SIG data submodule
    ├── assigned_numbers/uuids/          # ✅ Service and characteristic UUIDs
    └── gss/                             # ✅ Detailed specifications
```

## Key Architectural Improvements (Current Implementation)

### ✅ Type-Safe Modern API

- **Rich dataclasses** instead of primitive returns
- **Python 3.9+ compatibility** with `__future__` annotations
- **Modern union syntax**: `Class | None` for all optional returns
- **Comprehensive type hints** for excellent IDE support

### ✅ Registry-Driven Design

- **Intelligent UUID resolution** with 4-stage name parsing
- **Multi-format UUID support**: short (2A19), full, dashes, case-insensitive
- **Dynamic characteristic discovery** with comprehensive validation
- **Extensible parser system** for custom implementations

### ✅ Production-Ready Quality

- **Perfect pylint score** (10.00/10) maintained consistently
- **Zero linting violations** with ruff and shellcheck
- **Comprehensive test coverage** with 16 API tests + 128+ registry tests
- **Real device validation** with Nordic Thingy:52 and other BLE devices

### ✅ Framework Agnostic Integration

- **Zero connection dependencies** - pure SIG standard interpretation
- **Works with any BLE library** (bleak, bleak-retry-connector, custom)
- **Clean separation** between standards and connectivity
- **Ecosystem ready** for integration with existing tools

## Development Phases Timeline

### ✅ Phase 1: Core GATT Layer (Complete)

- ✅ BluetoothSIGTranslator with type-safe dataclasses
- ✅ Registry-driven UUID resolution
- ✅ 70+ characteristic parsers with comprehensive validation
- ✅ Integration patterns with bleak/bleak-retry-connector
- ✅ Real device testing and validation
- ✅ Modern Python type annotations with 3.9+ compatibility

### 🔄 Phase 2: GAP Layer Enhancement (Planned - 6 months)

- 🚧 Advertisement data interpretation using SIG standards
- 🚧 Device capability analysis from advertisements
- 🚧 Service discovery optimization with intelligent caching
- 🚧 Integration with bluetooth-data-tools ecosystem
- 🚧 SIG compliance validation for advertisements

### 📋 Phase 3: Performance & Validation (Planned - 12 months)

- 📋 Advanced validation against complete SIG specifications
- 📋 Service composition and dependency validation
- 📋 Enhanced error reporting with diagnostic information
- 📋 Performance profiling and optimization
- 📋 Compiled registry system for zero-overhead access

### 🎯 Phase 4: Ecosystem Integration (Planned - 18 months)

- 🎯 Home Assistant integration patterns and helpers
- 🎯 IoT platform connectors and adapters
- 🎯 Plugin system for custom characteristic parsers
- 🎯 Advanced device fingerprinting and capabilities
- 🎯 Complete SIG standard coverage (1000+ characteristics)

## Benefits of Current Architecture

1. **🎯 Pure SIG Standards Focus**: Clean separation from connection management
2. **🔧 Type-Safe API**: Rich dataclasses with full IDE support
3. **🔌 Universal Integration**: Works with any BLE connection library
4. **🏗️ Modern Python**: Future annotations for 3.9+ compatibility
5. **🧪 Production Quality**: Perfect linting scores and comprehensive testing
6. **📦 Lightweight Core**: Zero connection dependencies, focused value
7. **🔄 Future Proof**: Extensible architecture for new SIG standards
8. **🌐 Ecosystem Ready**: Designed for integration with existing tools

This architecture establishes `bluetooth-sig-python` as the definitive library for Bluetooth SIG standard interpretation, providing type-safe, production-ready APIs while maintaining compatibility and extensibility for future enhancements.

```text
│       │   ├── advertisements/          # Advertisement interpreters
│       │   │   ├── __init__.py
│       │   │   └── service_resolver.py  # Service UUID interpretation
│       │   └── validators/              # SIG compliance validation
│       │       ├── __init__.py
│       │       └── standard_compliance.py
│       ├── registry/                    # Registry System (Core)
│       │   ├── __init__.py
│       │   ├── loader.py                # YAML database loader
│       │   ├── resolver.py              # Name-to-UUID resolution
│       │   ├── cache.py                 # Runtime caching system
│       │   └── compiled.py              # Compiled/pre-processed registry (Phase 3)
│       ├── database/                    # SIG Database (Git Submodule)
│       │   ├── characteristics/         # YAML characteristic definitions
│       │   ├── services/                # YAML service definitions
│       │   └── data_types/              # YAML data type definitions
│       ├── codegen/                     # Code Generation (Phase 3)
│       │   ├── __init__.py
│       │   ├── compiler.py              # YAML-to-Python compiler
│       │   ├── templates/               # Code generation templates
│       │   │   ├── characteristic.py.j2 # Characteristic class template
│       │   │   ├── service.py.j2        # Service class template
│       │   │   └── registry.py.j2       # Registry mapping template
│       │   └── validators.py            # Generated code validation
│       └── utils/                       # Utilities
│           ├── __init__.py
│           ├── uuid_helpers.py          # UUID manipulation
│           └── exceptions.py            # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest configuration
│   ├── test_gatt/                       # GATT layer tests
│   │   ├── test_characteristics.py
│   │   ├── test_services.py
│   │   └── test_parsers.py
│   ├── test_registry/                   # Registry tests
│   │   ├── test_uuid_registry.py
│   │   └── test_name_resolver.py
│   ├── test_integration/                # Integration tests
│   │   ├── test_bleak_integration.py
│   │   └── test_real_devices.py
│   └── benchmarks/                      # Performance benchmarks
│       └── test_parsing_performance.py
├── examples/                            # Usage examples
│   ├── basic_usage.py                   # Simple characteristic parsing
│   ├── bleak_integration.py             # With bleak-retry-connector
│   ├── service_discovery.py             # Service and characteristic discovery
│   └── custom_parsers.py                # Extending with custom parsers
├── docs/                                # Documentation
│   ├── index.md
│   ├── installation.md
│   ├── usage.md
│   └── contributing.md
├── bluetooth_sig_data/                  # Bluetooth SIG specification data
│   ├── services/                        # Service specifications
│   ├── characteristics/                 # Characteristic specifications
│   └── data_types/                      # Standard data type definitions
└── scripts/                             # Development scripts
    ├── generate_docs.py
    └── update_sig_data.py

## Core Architecture Layers

### 1. GATT Layer (`src/bluetooth_sig/gatt/`) - Phase 1

**Purpose**: Pure SIG GATT standard interpretation and parsing

**Responsibilities**:

- Characteristic data parsing with proper types/units
- Service definition and structure mapping
- GATT-level SIG standard compliance
- Device interaction data interpretation

```python
# Core GATT API - Pure SIG standard translation
from bluetooth_sig.gatt import CharacteristicRegistry, ServiceRegistry

# Parse raw characteristic data
parser = CharacteristicRegistry.get_parser("2A19")  # Battery Level
result = parser.parse_value(raw_data)
# Returns: ParsedCharacteristic(value=85, unit="%", device_class="battery")

# Resolve UUIDs by intelligent name matching
uuid = CharacteristicRegistry.resolve_uuid("BatteryLevel")
# Returns: "2A19"
```

### 2. GAP Layer (`src/bluetooth_sig/gap/`) - Phase 2 (Future)

**Purpose**: SIG standard interpretation for advertisement data

**Responsibilities**:

- Service UUID resolution in advertisements
- SIG standard compliance validation
- Advertisement data interpretation
- Device capability inference from advertisements

```python
# Future GAP API - Advertisement interpretation
from bluetooth_sig.gap import AdvertisementInterpreter

# Interpret service UUIDs in advertisements
services = AdvertisementInterpreter.resolve_services(["180F", "181A"])
# Returns: [BatteryService, EnvironmentalSensingService]
```

### 3. Registry Layer (`src/bluetooth_sig/registry/`) - Core Foundation

**Purpose**: Intelligent UUID resolution and SIG standard lookup

**Responsibilities**:

- Multi-stage name parsing and resolution
- SIG specification data management
- UUID registry maintenance
- Cross-layer standard definitions

```python
# Registry API - Universal SIG standard lookup
from bluetooth_sig.registry import UUIDRegistry

# Intelligent name resolution
uuid = UUIDRegistry.resolve("TemperatureCharacteristic")
# Tries: "TemperatureCharacteristic" → "Temperature" → org.bluetooth format
name = UUIDRegistry.get_name("2A1C")  # Returns: "Temperature Measurement"
```

## Integration Patterns

### Pattern 1: Pure SIG Translation (Core Use Case)

```python
from bluetooth_sig.gatt import CharacteristicRegistry

def parse_sensor_reading(char_uuid: str, raw_data: bytes):
    """Pure SIG standard translation - no connection dependencies."""
    parser = CharacteristicRegistry.get_parser(char_uuid)
    if parser:
        return parser.parse_value(raw_data)
    return raw_data  # Fallback to raw data
```

### Pattern 2: With bleak-retry-connector (Recommended for Applications)

```python
from bleak_retry_connector import establish_connection
from bleak import BleakClient
from bluetooth_sig.gatt import CharacteristicRegistry, ServiceRegistry

async def read_device_sensors(address: str):
    """Read and parse device sensors using proven connection management."""
    async with establish_connection(BleakClient, address, timeout=10.0) as client:
        results = {}

        for service in await client.get_services():
            if service_info := ServiceRegistry.get_service_info(service.uuid):
                for char in service.characteristics:
                    if parser := CharacteristicRegistry.get_parser(char.uuid):
                        raw_data = await client.read_gatt_char(char.uuid)
                        results[char.uuid] = parser.parse_value(raw_data)

        return results
```

### Pattern 3: With Direct Bleak (Simple Cases)

```python
from bleak import BleakClient
from bluetooth_sig.gatt import CharacteristicRegistry

async def simple_characteristic_read(address: str, char_uuid: str):
    """Simple characteristic reading with pure bleak."""
    async with BleakClient(address, timeout=10.0) as client:
        raw_data = await client.read_gatt_char(char_uuid)
        parser = CharacteristicRegistry.get_parser(char_uuid)
        return parser.parse_value(raw_data) if parser else raw_data
```

### Pattern 4: Integration with bluetooth-data-tools

```python
from bluetooth_data_tools import parse_advertisement_data
from bluetooth_sig.gap import AdvertisementInterpreter  # Future
from bluetooth_sig.gatt import ServiceRegistry

async def discover_and_interpret_device(advertisement_data):
    """Combine advertisement parsing with SIG interpretation."""
    # Parse raw advertisement
    adv = parse_advertisement_data(advertisement_data)

    # Interpret using SIG standards (future functionality)
    interpreted_services = []
    for service_uuid in adv.service_uuids:
        if service_info := ServiceRegistry.get_service_info(service_uuid):
            interpreted_services.append(service_info)

    return {
        'device_name': adv.local_name,
        'services': interpreted_services,
        'capabilities': [s.category for s in interpreted_services]
    }
```

## Development Phases

### Phase 1: Core GATT Layer (MVP)
- Basic characteristic and service parsing
- Registry-driven UUID resolution
- Integration with bleak/bleak-retry-connector
- Essential SIG standard characteristics

### Phase 2: GAP Layer Enhancement
- Advertisement data interpretation
- Service discovery optimization
- SIG compliance validation
- bluetooth-data-tools integration

### Phase 3: Compiled Registry System (Performance Optimization)

**Purpose**: Pre-compiled Python classes for zero-overhead SIG standard access

**Problem**: Runtime YAML parsing overhead and dynamic lookups
**Solution**: Code generation system that pre-compiles YAML specifications into optimized Python classes

```python
# Phase 3: Compiled Registry Architecture
bluetooth-sig/
├── src/bluetooth_sig/
│   ├── codegen/                         # Code Generation System
│   │   ├── compiler.py                  # YAML-to-Python compiler
│   │   ├── templates/                   # Jinja2 code templates
│   │   │   ├── characteristic.py.j2     # Characteristic class template
│   │   │   ├── service.py.j2            # Service class template
│   │   │   └── registry.py.j2           # Static registry template
│   │   └── validators.py                # Generated code validation
│   ├── compiled/                        # Generated Code (Build Artifact)
│   │   ├── __init__.py
│   │   ├── characteristics/             # Pre-compiled characteristic classes
│   │   │   ├── battery_level_2a19.py    # class BatteryLevel2A19(BaseCharacteristic)
│   │   │   ├── temperature_2a1c.py      # class Temperature2A1C(BaseCharacteristic)
│   │   │   └── humidity_2a6f.py         # class Humidity2A6F(BaseCharacteristic)
│   │   ├── services/                    # Pre-compiled service classes
│   │   │   ├── battery_service_180f.py  # class BatteryService180F(BaseService)
│   │   │   └── environmental_181a.py    # class EnvironmentalSensing181A(BaseService)
│   │   └── registry.py                  # Static lookup dictionaries
│   └── runtime/                         # Runtime System (Fallback)
│       ├── loader.py                    # Dynamic YAML loader (Phase 1)
│       └── resolver.py                  # Runtime name resolution
└── build_tools/
    ├── compile_sig_database.py          # Build script for releases
    └── validate_generated_code.py       # Quality assurance
```

**Build Process**:
```bash
# During release preparation
python build_tools/compile_sig_database.py \
    --input database/ \
    --output src/bluetooth_sig/compiled/ \
    --validate

# Generates optimized Python classes with:
# - Zero YAML parsing overhead
# - Direct memory access to specifications
# - Type hints for IDE support
# - Compile-time validation
```

**Runtime Performance**:
```python
# Phase 1: Runtime YAML parsing
parser = CharacteristicRegistry.get_parser("2A19")  # ~1-5ms YAML lookup

# Phase 3: Compiled classes
from bluetooth_sig.compiled.characteristics import BatteryLevel2A19
parser = BatteryLevel2A19()  # ~0.001ms direct instantiation

# 1000x+ performance improvement for parser instantiation
# Zero memory overhead for registry lookups
# Better IDE support with static typing
```

**Generated Code Example**:
```python
# Generated: src/bluetooth_sig/compiled/characteristics/battery_level_2a19.py
from bluetooth_sig.gatt.base import BaseCharacteristic
from typing import Dict, Any

class BatteryLevel2A19(BaseCharacteristic):
    """Battery Level - Compiled SIG Standard Implementation."""

    UUID = "2A19"
    NAME = "Battery Level"
    UNIT = "%"
    DATA_TYPE = "uint8"
    RANGE_MIN = 0
    RANGE_MAX = 100

    def parse_value(self, data: bytes) -> Dict[str, Any]:
        """Parse battery level with compile-time optimized logic."""
        if len(data) != 1:
            raise ValueError("Battery Level requires exactly 1 byte")

        value = data[0]
        if value > 100:
            raise ValueError("Battery Level must be 0-100%")

        return {
            "value": value,
            "unit": "%",
            "device_class": "battery"
        }
```

**Distribution Strategy**:
```python
# PyPI package includes both modes
import bluetooth_sig

# Production mode: Use compiled classes (default)
from bluetooth_sig import get_characteristic_parser
parser = get_characteristic_parser("2A19")  # Uses compiled BatteryLevel2A19

# Development mode: Use runtime YAML (optional)
from bluetooth_sig.runtime import CharacteristicRegistry
parser = CharacteristicRegistry.get_parser("2A19")  # Dynamic YAML parsing
```

**Benefits of Compiled Approach**:

1. **Performance**: 1000x+ faster parser instantiation
2. **Memory**: Zero YAML parsing overhead in production
3. **IDE Support**: Full type hints and autocompletion
4. **Validation**: Compile-time specification checking
5. **Distribution**: Single wheel with pre-compiled standards
6. **Backwards Compatibility**: Runtime mode still available for development

**Release Workflow**:
```bash
# 1. Update SIG database submodule
git submodule update --remote database/

# 2. Compile specifications to Python classes
python build_tools/compile_sig_database.py

# 3. Validate generated code
python build_tools/validate_generated_code.py

# 4. Package with compiled classes
python -m build

# 5. Publish to PyPI with optimized registry
twine upload dist/bluetooth_sig-*.whl
```

This compiled approach transforms the library from a runtime YAML processor into a compile-time optimized SIG standard implementation, providing production-grade performance while maintaining development flexibility.

## Key Architectural Decisions

### ✅ Pure SIG Standards Library

- **Zero connection dependencies** - focuses purely on SIG standard interpretation
- **Framework agnostic** - works with any connection library
- **Reusable across platforms** - pure Python implementation

### ✅ Layered Architecture

- **GATT Layer**: Device interaction and characteristic parsing
- **GAP Layer**: Advertisement interpretation (future)
- **Registry Layer**: Universal SIG standard lookup and resolution

### ✅ Registry-Driven Design

- **Intelligent UUID resolution** with multi-stage name parsing
- **Automatic characteristic discovery** based on SIG standards
- **Extensible parser registration** system for custom implementations

### ✅ Integration Flexibility

- **Works with any BLE library** (bleak, bleak-retry-connector, custom)
- **Optional enhancement** for existing tools (bluetooth-data-tools)
- **Framework ready** for IoT platforms, applications, and integrations

## Package Distribution

### Core Package: `bluetooth-sig`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "bluetooth-sig"
description = "Python library for Bluetooth SIG standard interpretation and parsing"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Hardware",
    "Topic :: Communications",
]
dependencies = [
    "pyyaml>=6.0",  # SIG specification data parsing
]
dynamic = ["version"]

[project.optional-dependencies]
# Integration examples and testing
integration = [
    "bleak>=0.20.0",
    "bleak-retry-connector>=3.0.0",
]

# Development dependencies
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "isort>=5.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
    "pre-commit>=2.20.0",
]

# Documentation
docs = [
    "mkdocs>=1.4.0",
    "mkdocs-material>=8.0.0",
    "mkdocstrings[python]>=0.20.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/bluetooth-sig"
Documentation = "https://bluetooth-sig.readthedocs.io"
Repository = "https://github.com/yourusername/bluetooth-sig"
Issues = "https://github.com/yourusername/bluetooth-sig/issues"
Changelog = "https://github.com/yourusername/bluetooth-sig/blob/main/CHANGELOG.md"

[tool.setuptools.dynamic]
version = {attr = "bluetooth_sig.__version__"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q --strict-markers --strict-config"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]

[tool.black]
target-version = ["py38"]
line-length = 88

[tool.isort]
profile = "black"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Installation Options

```bash
# Core SIG standards library only
pip install bluetooth-sig

# With integration examples for development
pip install bluetooth-sig[integration]

# For development
pip install bluetooth-sig[dev]

# Full installation with docs
pip install bluetooth-sig[integration,dev,docs]

# Integration with ecosystem libraries (user choice)
pip install bluetooth-sig bleak-retry-connector  # Recommended
pip install bluetooth-sig bleak                  # Basic
pip install bluetooth-sig bluetooth-data-tools   # With advertisement parsing
```

## Benefits of This Architecture

1. **🎯 Focused Value Proposition**: Pure SIG standard expertise and interpretation
2. **🔌 Universal Integration**: Works with any BLE connection library or framework
3. **🏗️ Clean Architecture**: Clear separation between standards and connectivity
4. **🧪 Comprehensive Testing**: Real device validation through integration tests
5. **📦 Lightweight Core**: Zero connection dependencies, pure standards implementation
6. **🔄 Future Proof**: Extensible to new SIG standards and connection technologies
7. **🌐 Ecosystem Ready**: Designed for integration with existing Bluetooth libraries

This architecture makes `bluetooth-sig` the definitive Python library for Bluetooth SIG standard interpretation while leveraging the ecosystem's best connection management and data parsing solutions.

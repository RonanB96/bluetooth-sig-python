# Test Suite README

This directory contains the comprehensive test suite for the Bluetooth SIG Standards Library. The test suite has been carefully organized to follow proper separation of concerns and provide clear boundaries between different test categories.

## Test Organization

The tests are organized into logical directories that map directly to the source code structure:

```text
tests/
├── conftest.py                         # Pytest configuration and fixtures
│
├── core/                              # Core framework functionality
│   └── test_translator.py            # BluetoothSIGTranslator tests
│
├── gatt/                              # GATT layer tests
│   ├── characteristics/               # Individual characteristic implementations
│   │   ├── test_base_characteristic.py
│   │   ├── test_battery_power_state.py
│   │   ├── test_custom_characteristics.py
│   │   ├── test_cycling_power.py
│   │   ├── test_environmental_sensors.py
│   │   ├── test_gas_sensors.py
│   │   ├── test_glucose_monitoring.py
│   │   └── test_new_sensors.py
│   ├── services/                      # Service implementations
│   │   ├── test_body_composition_service.py
│   │   ├── test_custom_services.py
│   │   └── test_weight_scale_service.py
│   ├── test_context.py               # GATT context parsing
│   ├── test_exceptions.py            # GATT exceptions
│   ├── test_resolver.py              # UUID resolution
│   ├── test_service_validation.py    # Service validation
│   ├── test_service_validation_extended.py
│   ├── test_uuid_registry.py         # UUID registry functionality
│   └── test_validation.py            # General GATT validation
│
├── device/                            # Device management and advertising
│   ├── test_advertising_parser.py    # BLE advertising data parsing
│   ├── test_device.py                # Device class functionality
│   └── test_device_types.py          # Device type definitions
│
├── registry/                          # YAML registry and UUID resolution
│   ├── test_registry_validation.py   # Registry validation
│   ├── test_yaml_cross_reference.py  # YAML cross-reference functionality
│   └── test_yaml_units.py            # YAML unit definitions
│
├── utils/                             # Utility functions and helpers
│   ├── test_bit_field_utils.py       # Bit field manipulation utilities
│   ├── test_performance_tracking.py  # Performance monitoring
│   └── test_profiling.py             # Profiling utilities
│
├── integration/                       # End-to-end and comprehensive scenarios
│   ├── test_basic_scenarios.py       # Basic integration scenarios
│   ├── test_custom_registration.py   # Custom characteristic/service registration
│   ├── test_end_to_end.py            # Multi-characteristic parsing
│   ├── test_examples.py              # Example usage scenarios
│   └── test_round_trip.py            # Round-trip encoding/decoding
│
└── diagnostics/                       # Logging and diagnostics
    ├── test_field_errors.py          # Field-level error handling
    ├── test_field_level_diagnostics.py
    └── test_logging.py               # General logging functionality
```

## Getting Started

To run the test suite, ensure you have the development dependencies installed:

```bash
pip install -e .[dev,test]
```

## Running Tests

The test organization maintains full compatibility with existing test commands:

```bash
# Run all tests
python -m pytest tests/

# Run tests for specific modules
python -m pytest tests/core/               # Core functionality
python -m pytest tests/gatt/characteristics/  # GATT characteristics
python -m pytest tests/integration/        # Integration tests

# Run specific test files
python -m pytest tests/gatt/characteristics/test_battery_power_state.py

# Run with coverage
python -m pytest tests/ --cov=src/bluetooth_sig
```

## Test Categories

### 1. Clear Separation of Concerns

- **Core**: Framework-level functionality (translator)
- **GATT**: GATT-specific functionality split between characteristics and services
- **Device**: Device management and advertising functionality
- **Registry**: YAML/UUID registry functionality
- **Utils**: Utility functions that don't fit elsewhere
- **Integration**: End-to-end scenarios and comprehensive tests
- **Diagnostics**: Logging and error handling tests

### 2. Hierarchical Organization

- Tests are grouped by the source code modules they test
- Related functionality is kept together
- Clear boundaries prevent overlap

### 3. Eliminated Overlaps

- Each test file has a specific, well-defined scope
- No duplicate testing of the same functionality
- Clear naming conventions make scope obvious

### 4. Improved Discoverability

- Easy to find tests related to specific functionality
- Structure matches source code organization
- Clear categorization of different test types

## Contributing

When adding new tests:

1. **Choose the right directory**: Place tests in the directory that matches the source code being tested
2. **Follow naming conventions**: Use `test_` prefix for test files and functions
3. **Maintain separation**: Don't mix different types of functionality in the same test file
4. **Use fixtures**: Leverage the shared fixtures in `conftest.py` for common setup

## Test Configuration

The `conftest.py` file provides:

- **Path management**: Ensures `src/` is on the Python path
- **ROOT_DIR constant**: For constructing paths relative to the project root
- **Registry cleanup**: Automatic cleanup of custom registrations between tests
- **Shared fixtures**: Common test utilities and mock objects

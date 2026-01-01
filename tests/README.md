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
├── diagnostics/                       # Logging and diagnostics
│   ├── test_field_errors.py          # Field-level error handling
│   ├── test_field_level_diagnostics.py
│   └── test_logging.py               # General logging functionality
│
└── docs/                              # Documentation tests
    ├── conftest.py                   # Shared fixtures for docs tests
    ├── test_source_content.py        # Markdown source validation
    ├── test_generate_diagrams.py     # Diagram generation tests
    ├── test_sidebar_structure.py     # Sidebar structure validation
    ├── html/                         # Static HTML validation (BeautifulSoup)
    │   ├── test_accessibility_static.py
    │   ├── test_structure_static.py
    │   └── test_content_quality_static.py
    └── playwright_tests/             # Interactive browser tests
        ├── test_accessibility.py
        ├── test_navigation.py
        ├── test_diataxis_structure.py
        ├── test_sidebar_content.py
        └── test_documentation_quality.py
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

# Run documentation tests
python -m pytest tests/docs/test_source_content.py -v  # Markdown source
python -m pytest tests/docs/html/ -v -n auto -m built_docs -p no:playwright  # Static HTML
python -m pytest tests/docs/playwright_tests/ -v -n auto -m "built_docs and playwright"  # Browser
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
- **Docs**: Documentation validation (Markdown source, HTML parsing, and Playwright browser tests)

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

## Documentation Tests

The `tests/docs/` directory contains three test suites with increasing complexity:

- **Markdown Source** (`test_source_content.py`): Fastest validation on raw markdown
  - Content quality (alt text, link text, code block languages)
  - Heading hierarchy and document structure
  - Writing style and Diataxis compliance
  - No build required, tests source files directly

- **HTML Parsing** (`tests/docs/html/`): Fast static validation using BeautifulSoup
  - Theme-generated elements (navigation, footer, breadcrumbs)
  - Sphinx-added accessibility attributes
  - Generated anchor IDs and internal links
  - 10-50× faster than browser tests, no Chromium required

- **Playwright** (`tests/docs/playwright_tests/`): Interactive browser testing
  - JavaScript functionality and keyboard navigation
  - CSS rendering and computed styles
  - Performance metrics and page load timing
  - Requires Chromium installation

See individual READMEs for detailed usage: [`tests/docs/html/README.md`](docs/html/README.md) and [`tests/docs/playwright_tests/README.md`](docs/playwright_tests/README.md)

## Test Configuration

The `conftest.py` file provides:

- **Path management**: Ensures `src/` is on the Python path
- **ROOT_DIR constant**: For constructing paths relative to the project root
- **Registry cleanup**: Automatic cleanup of custom registrations between tests
- **Shared fixtures**: Common test utilities and mock objects

# Test Suite README

This directory contains the comprehensive test suite for the Bluetooth SIG Standards Library. The test suite has been carefully organized to follow proper separation of concerns and provide clear boundaries between different test categories.

## Test Organization

The tests are organized into logical directories that map directly to the source code structure:

```text
tests/
├── conftest.py                          # Pytest configuration and fixtures
├── test_browse_groups_registry.py       # Browse group registry validation
├── test_declarations_registry.py        # Declarations registry validation
├── test_members_registry.py             # Members registry validation
├── test_mesh_profiles_registry.py       # Mesh profiles registry validation
├── test_object_types_registry.py        # Object types registry validation
├── test_sdo_uuids_registry.py           # SDO UUIDs registry validation
├── test_service_classes_registry.py     # Service classes registry validation
├── test_units_registry.py               # Units registry validation
│
├── advertising/                         # BLE advertising data tests
│   ├── test_advertisement_builder.py
│   ├── test_advertising_framework.py
│   ├── test_channel_map_update.py
│   ├── test_ead_decryption.py
│   ├── test_ead_decryptor_class.py
│   ├── test_encryption_provider.py
│   ├── test_exceptions.py
│   ├── test_indoor_positioning.py
│   ├── test_payload_interpreter.py
│   ├── test_pdu_parser_32bit_uuids.py
│   ├── test_pdu_parser_solicited.py
│   ├── test_service_data_parser.py
│   ├── test_service_resolver.py
│   ├── test_sig_characteristic_interpreter.py
│   ├── test_state.py
│   ├── test_three_d_information.py
│   └── test_transport_discovery.py
│
├── benchmarks/                          # Performance benchmarks (--benchmark-only)
│   ├── conftest.py
│   ├── test_comparison.py              # Library vs manual parsing
│   └── test_performance.py             # UUID resolution, parsing throughput
│
├── core/                                # Core framework functionality
│   ├── test_async_translator.py        # Async translator tests
│   ├── test_translator.py             # BluetoothSIGTranslator tests
│   └── test_translator_encoding.py    # Encoding round-trip tests
│
├── descriptors/                         # GATT descriptor implementations
│   ├── conftest.py
│   ├── test_aggregate_format.py
│   ├── test_base.py
│   ├── test_cccd.py
│   ├── test_complete_br_edr_transport_block.py
│   ├── test_environmental_sensing.py
│   ├── test_extended_properties.py
│   ├── test_external_report_reference.py
│   ├── test_imd_trigger_setting.py
│   ├── test_integration.py
│   ├── test_manufacturer_limits.py
│   ├── test_measurement_description.py
│   ├── test_number_of_digitals.py
│   ├── test_observation_schedule.py
│   ├── test_presentation_format.py
│   ├── test_process_tolerances.py
│   ├── test_registry.py
│   ├── test_report_reference.py
│   ├── test_sccd.py
│   ├── test_time_trigger_setting.py
│   ├── test_user_description.py
│   ├── test_valid_range.py
│   ├── test_valid_range_and_accuracy.py
│   ├── test_value_trigger_setting.py
│   └── test_writability.py
│
├── device/                              # Device management and advertising
│   ├── test_advertising_appearance.py  # Appearance parsing
│   ├── test_advertising_cod_integration.py  # Class of Device integration
│   ├── test_advertising_parser.py      # BLE advertising data parsing
│   ├── test_device.py                  # Device class functionality
│   ├── test_device_advertising.py      # Device advertising features
│   ├── test_device_async_methods.py    # Async device methods
│   ├── test_device_batch_ops.py        # Batch operations
│   ├── test_device_types.py            # Device type definitions
│   ├── test_peripheral_device.py       # Peripheral device (GATT server)
│   └── test_peripheral_types.py        # Peripheral type definitions
│
├── diagnostics/                         # Logging and diagnostics
│   ├── test_field_errors.py            # Field-level error handling
│   ├── test_field_level_diagnostics.py
│   └── test_logging.py                # General logging functionality
│
├── docs/                                # Documentation tests
│   ├── conftest.py                    # Shared fixtures for docs tests
│   ├── test_docs_code_blocks.py       # Code block validation
│   ├── test_generate_diagrams.py      # Diagram generation tests
│   ├── test_readme_badges.py          # README badge validation
│   ├── test_sidebar_structure.py      # Sidebar structure validation
│   ├── test_source_content.py         # Markdown source validation
│   ├── html/                          # Static HTML validation (BeautifulSoup)
│   │   ├── conftest.py
│   │   ├── test_accessibility_static.py
│   │   ├── test_content_quality_static.py
│   │   └── test_structure_static.py
│   └── playwright_tests/             # Interactive browser tests (Chromium)
│       ├── conftest.py
│       ├── test_accessibility.py
│       ├── test_diataxis_structure.py
│       ├── test_documentation_quality.py
│       ├── test_navigation.py
│       └── test_sidebar_content.py
│
├── gatt/                                # GATT layer tests
│   ├── test_context.py                # GATT context parsing
│   ├── test_exceptions.py            # GATT exceptions
│   ├── test_resolver.py              # UUID resolution
│   ├── test_service_validation.py    # Service validation
│   ├── test_service_validation_extended.py
│   ├── test_special_values_resolver.py       # Special values handling
│   ├── test_special_values_resolver_priority.py
│   ├── test_uuid_registry.py         # UUID registry functionality
│   ├── test_validation.py            # General GATT validation
│   ├── characteristics/               # Individual characteristic tests (194 files)
│   │   ├── conftest.py
│   │   ├── test_base_characteristic.py
│   │   ├── test_characteristic_common.py
│   │   ├── test_characteristic_role.py
│   │   ├── test_characteristic_test_coverage.py
│   │   ├── test_custom_characteristics.py
│   │   ├── test_templates.py
│   │   ├── test_<name>.py            # One file per implemented characteristic
│   │   └── utils/                    # Characteristic utility tests
│   │       ├── test_bit_field_utils.py
│   │       ├── test_data_parser.py
│   │       ├── test_data_validator.py
│   │       └── test_ieee11073_parser.py
│   └── services/                      # Service implementation tests (30 files)
│       ├── test_service_common.py
│       ├── test_service_coverage.py
│       ├── test_custom_services.py
│       └── test_<name>_service.py    # One file per implemented service
│
├── integration/                         # End-to-end and comprehensive scenarios
│   ├── test_auto_registration.py      # Auto-registration tests
│   ├── test_basic_scenarios.py        # Basic integration scenarios
│   ├── test_connection_managers.py    # Connection manager tests
│   ├── test_custom_registration.py    # Custom characteristic/service registration
│   ├── test_end_to_end.py            # Multi-characteristic parsing
│   ├── test_examples.py              # Example usage scenarios
│   └── test_format_types_integration.py  # Format type integration
│
├── registry/                            # YAML registry and UUID resolution
│   ├── core/                          # Core registry type tests
│   │   ├── test_coding_format.py
│   │   ├── test_formattypes.py
│   │   ├── test_namespace_description.py
│   │   └── test_uri_schemes.py
│   ├── test_ad_types.py              # AD type registry
│   ├── test_appearance_values.py     # Appearance value lookups
│   ├── test_class_of_device.py       # Class of Device parsing
│   ├── test_company_identifiers.py   # Company identifier lookups
│   ├── test_permitted_characteristics.py
│   ├── test_profile_lookup.py        # Profile lookups
│   ├── test_protocol_identifiers.py  # Protocol identifier lookups
│   ├── test_registry_accessors.py    # Registry accessor patterns
│   ├── test_registry_validation.py   # Registry validation
│   ├── test_service_discovery_attributes.py
│   ├── test_uri_schemes.py           # URI scheme lookups
│   ├── test_utils.py                 # Registry utilities
│   ├── test_yaml_cross_reference.py  # YAML cross-reference functionality
│   └── test_yaml_units.py            # YAML unit definitions
│
├── static_analysis/                     # Static analysis and completeness checks
│   ├── test_characteristic_registry_completeness.py
│   ├── test_service_registry_completeness.py
│   └── test_yaml_implementation_coverage.py
│
├── stream/                              # Stream processing tests
│   └── test_pairing.py
│
├── types/                               # Type system tests
│   ├── test_company.py               # Company identifier types
│   └── test_gatt_enums.py            # GATT enum validation
│
└── utils/                               # Utility functions and helpers
    └── test_profiling.py              # Profiling utilities
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

- **Core**: Framework-level functionality (translator, async translator, encoding)
- **GATT**: GATT-specific functionality split between characteristics, services, and utilities
- **Advertising**: BLE advertising data parsing, EAD decryption, PDU parsing
- **Descriptors**: GATT descriptor implementations (CCCD, presentation format, valid range, etc.)
- **Device**: Device management, advertising, and peripheral device functionality
- **Registry**: YAML/UUID registry functionality and core registry types
- **Types**: Type system validation (company identifiers, GATT enums)
- **Stream**: Stream processing and pairing tests
- **Utils**: Utility functions that don't fit elsewhere
- **Integration**: End-to-end scenarios and comprehensive tests
- **Diagnostics**: Logging and error handling tests
- **Static Analysis**: Registry completeness and YAML implementation coverage checks
- **Benchmarks**: Performance and comparison benchmarks (run with `--benchmark-only`)
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

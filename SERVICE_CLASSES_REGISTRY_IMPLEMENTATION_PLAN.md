# Service Classes Registry Implementation Plan

## Overview
Implement the Service Classes Registry for Bluetooth SIG service class definitions from `service_classes.yaml`. This registry will provide centralized access to service class UUIDs, names, and identifiers used in Bluetooth service discovery and classification.

## Bluetooth SIG Context
Service classes define the types of services that Bluetooth devices can offer. They are used in:
- Service discovery during device pairing
- GATT service identification
- Profile and protocol classification
- Device capability advertisement

## Implementation Requirements

### Core Components
- **ServiceClassInfo dataclass**: Store service class metadata (uuid, name, id)
- **ServiceClassesRegistry class**: Thread-safe registry with lookup methods
- **YAML loading**: Load from `bluetooth_sig/assigned_numbers/service_classes.yaml`
- **UUID resolution**: Support various UUID input formats (string, int, BluetoothUUID)

### Registry Methods
- `get_service_class_info(uuid)` - Lookup by UUID
- `get_service_class_info_by_name(name)` - Lookup by service class name
- `get_service_class_info_by_id(id)` - Lookup by service class ID
- `is_service_class_uuid(uuid)` - Validation method
- `get_all_service_classes()` - Return all service classes

### Integration Points
- Export through `src/bluetooth_sig/registry/__init__.py`
- Follow established registry pattern from units/object_types
- Use shared utilities (`parse_bluetooth_uuid`, `load_bluetooth_sig_yaml`)

## Testing Strategy
- **10+ test cases** covering all lookup methods
- **Success and failure scenarios** for each method
- **UUID format variations** (string, int, BluetoothUUID)
- **Case insensitive name lookup**
- **Thread safety validation**

## Quality Gates
- ✅ **ruff**: Code formatting and linting
- ✅ **pylint**: Static analysis
- ✅ **mypy**: Type checking
- ✅ **shellcheck**: Shell script validation
- ✅ **pydocstyle**: Documentation style
- ✅ **pytest**: Full test suite (1000+ tests)

## Dependencies
- `bluetooth_sig/assigned_numbers/service_classes.yaml` (from submodule)
- Shared registry utilities in `src/bluetooth_sig/registry/utils.py`
- BluetoothUUID type from `src/bluetooth_sig/types/uuid.py`

## Success Criteria
- [ ] Registry loads service classes from YAML
- [ ] All lookup methods work correctly
- [ ] Comprehensive test coverage (10+ tests)
- [ ] All quality gates pass
- [ ] Exported through registry module
- [ ] Follows established patterns
- [ ] Thread-safe implementation
- [ ] Proper error handling

## Files to Create/Modify
- `src/bluetooth_sig/registry/service_classes.py` (new)
- `tests/test_service_classes_registry.py` (new)
- `src/bluetooth_sig/registry/__init__.py` (update exports)

## Implementation Order
1. Create `service_classes.py` with registry implementation
2. Create comprehensive test suite
3. Update registry exports
4. Run quality gates
5. Commit changes
# Mesh Profiles Registry Implementation Plan

## Overview
Implement the Mesh Profiles Registry for Bluetooth SIG mesh profile definitions from `mesh_profiles.yaml`. This registry will provide centralized access to mesh profile UUIDs, names, and identifiers used in Bluetooth mesh networking.

## Bluetooth SIG Context
Mesh profiles define the application profiles and behaviors for Bluetooth mesh networks. They specify:
- Mesh model behaviors and interactions
- Profile-specific functionality (lighting, sensors, etc.)
- Foundation models for mesh management
- Generic models for common device types

## Implementation Requirements

### Core Components
- **MeshProfileInfo dataclass**: Store mesh profile metadata (uuid, name, id)
- **MeshProfilesRegistry class**: Thread-safe registry with lookup methods
- **YAML loading**: Load from `bluetooth_sig/assigned_numbers/mesh_profiles.yaml`
- **UUID resolution**: Support various UUID input formats (string, int, BluetoothUUID)

### Registry Methods
- `get_mesh_profile_info(uuid)` - Lookup by UUID
- `get_mesh_profile_info_by_name(name)` - Lookup by mesh profile name
- `get_mesh_profile_info_by_id(id)` - Lookup by mesh profile ID
- `is_mesh_profile_uuid(uuid)` - Validation method
- `get_all_mesh_profiles()` - Return all mesh profiles

### Integration Points
- Export through `src/bluetooth_sig/registry/__init__.py`
- Follow established registry pattern from units/object_types/service_classes
- Use shared utilities (`parse_bluetooth_uuid`, `find_bluetooth_sig_path`, `load_yaml_uuids`)

## Testing Strategy
- **10+ test cases** covering all lookup methods
- **Success and failure scenarios** for each method
- **UUID format variations** (string, int, BluetoothUUID)
- **Case insensitive name lookup**
- **Thread safety validation**

## Quality Gates
- ✅ **ruff**: Code formatting and linting
- ✅ **pylint**: Static analysis
- ✅ **shellcheck**: Shell script validation
- ✅ **pydocstyle**: Documentation style
- ✅ **pytest**: Full test suite (1000+ tests)

## Dependencies
- `bluetooth_sig/assigned_numbers/mesh_profiles.yaml` (from submodule)
- Shared registry utilities in `src/bluetooth_sig/registry/utils.py`
- BluetoothUUID type from `src/bluetooth_sig/types/uuid.py`

## Success Criteria
- [ ] Registry loads mesh profiles from YAML
- [ ] All lookup methods work correctly
- [ ] Comprehensive test coverage (10+ tests)
- [ ] All quality gates pass
- [ ] Exported through registry module
- [ ] Follows established patterns
- [ ] Thread-safe implementation
- [ ] Proper error handling

## Files to Create/Modify
- `src/bluetooth_sig/registry/mesh_profiles.py` (new)
- `tests/test_mesh_profiles_registry.py` (new)
- `src/bluetooth_sig/registry/__init__.py` (update exports)

## Implementation Order
1. Create `mesh_profiles.py` with registry implementation
2. Create comprehensive test suite
3. Update registry exports
4. Run quality gates
5. Commit changes
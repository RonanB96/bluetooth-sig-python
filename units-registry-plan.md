## Plan: Implement Units Registry

Create a centralized Units Registry module to parse and expose Bluetooth SIG-defined units from `units.yaml`, following the existing `MembersRegistry` pattern. This enables consistent unit validation, lookup by UUID/name/ID, and thread-safe access, improving standards compliance and centralizing unit management currently scattered across characteristics.

**Steps:**
1. Create `src/bluetooth_sig/registry/units.py` with `UnitInfo` dataclass, `UnitsRegistry` class, and lookup methods.
2. Implement YAML loading using `load_yaml_uuids` from `utils.py`, storing by UUID, name, and ID.
3. Add thread-safety with `RLock` and error handling for missing YAML.
4. Create `tests/test_units_registry.py` with tests for initialization, lookups, and structure validation.
5. Update any relevant documentation or integration points to use the new registry.

**Open Questions:**
1. Should the registry integrate with existing `uuid_registry` unit conversion methods?
2. How to handle unit formatting (e.g., "°C" vs "degree Celsius") in lookups?
3. Any specific error handling for invalid unit UUIDs in characteristics?
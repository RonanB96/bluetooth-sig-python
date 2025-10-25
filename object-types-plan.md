## Plan: Implement Object Types Registry

Create a registry system for Bluetooth Object Transfer Service (OTS) object types, following the same pattern as the units registry in `uuid_registry.py`. This medium-priority feature will enable proper handling of OTS object type UUIDs with their descriptive names and identifiers.

**Steps:**

1. Analyze existing registry patterns in `src/bluetooth_sig/registry/` and `uuid_registry.py` to understand data structures and loading mechanisms.
2. Create `ObjectTypeInfo` dataclass in `src/bluetooth_sig/registry/object_types.py` with uuid, name, and id fields matching the YAML structure.
3. Implement `ObjectTypesRegistry` class with thread-safe loading from `object_types.yaml`, including lookup methods by UUID, name, and ID.
4. Add object type mappings storage and loading logic similar to unit mappings in `uuid_registry.py`.
5. Create global registry instance and expose it through the registry module's `__init__.py`.
6. Add tests for the new registry in `tests/` with success and failure cases.
7. Update documentation to reference the new object types registry.

**Open Questions:**

1. Should object types be integrated into `UuidRegistry` class like units, or remain as a separate registry like members?
2. How will object types be used in characteristic implementations - as enums, lookup methods, or direct registry access?
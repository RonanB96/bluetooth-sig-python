## Plan: Implement Declarations Registry

Create a registry system for GATT attribute declarations, following the same pattern as other registries in the codebase. This low-priority feature will enable proper handling of declaration UUIDs like Primary Service (0x2800), Characteristic (0x2803), etc.

**Steps:**

1. Analyze existing registry patterns in `src/bluetooth_sig/registry/` (members.py, uuid_registry.py) to understand data structures and loading mechanisms.
2. Create `DeclarationInfo` dataclass in `src/bluetooth_sig/registry/declarations.py` with uuid, name, and id fields matching the declarations.yaml structure.
3. Implement `DeclarationsRegistry` class with thread-safe loading from `declarations.yaml`, including lookup methods by UUID, name, and ID.
4. Add declaration mappings storage and loading logic similar to other registries.
5. Create global registry instance and expose it through the registry module's `__init__.py`.
6. Add tests for the new registry in `tests/` with success and failure cases.
7. Update documentation to reference the new declarations registry.

**Open Questions:**

1. Should declarations be integrated into the main uuid_registry.py or kept separate like members?
2. Any special handling needed for declaration UUIDs vs other UUIDs?
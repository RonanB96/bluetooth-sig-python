## Plan: Implement Mesh Profiles Registry

Create a registry for Bluetooth Mesh Network Lighting Control (NLC) profiles, following the pattern of existing registries like members and object types. This medium-priority implementation will enable UUID resolution for mesh profile identifiers from `mesh_profile_uuids.yaml`, handling the absence of 'id' fields by generating them from names.

**Steps:**
1. Analyze `members.py` and `object-types-plan.md` for registry patterns, focusing on YAML loading and dataclass structures.
2. Create `MeshProfileInfo` dataclass in `src/bluetooth_sig/registry/mesh_profiles.py` with uuid, name, and optional id fields.
3. Implement `MeshProfilesRegistry` class with thread-safe loading from `mesh_profile_uuids.yaml`, generating ids from names when missing.
4. Add lookup methods for profiles by UUID, name, and id, with global registry instance in `registry/__init__.py`.
5. Create tests in `tests/` covering loading, lookups, and edge cases like missing ids.
6. Update `SIG_YAML_COVERAGE_AUDIT.md` to mark mesh profiles as implemented.

**Open Questions:**
1. Should mesh profiles integrate into `UuidRegistry` like characteristics, or remain separate like members?
2. How to generate 'id' fields for profiles without them - use name-based format or skip entirely?
3. Any special handling needed for 16-bit UUIDs vs full UUIDs in mesh context?
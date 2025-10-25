## Plan: Implement Service Classes Registry

Create a registry system for Bluetooth SIG service class IDs and profile identifiers, loading from service_class.yaml with uuid, name, and id fields, following the MembersRegistry pattern in `src/bluetooth_sig/registry/members.py`.

**Steps:**
1. Create `src/bluetooth_sig/registry/service_classes.py` with ServiceClassInfo dataclass and ServiceClassesRegistry class, loading service_class.yaml using load_yaml_uuids.
2. Add lookup methods: get_by_uuid(), get_by_name(), get_by_id(), is_service_class_uuid(), get_all_service_classes().
3. Create global instance `service_classes_registry` in the module.
4. Update `src/bluetooth_sig/registry/__init__.py` to export the registry instance.
5. Add unit tests in `tests/test_registry_service_classes.py` with success cases (valid lookups) and failure cases (invalid UUIDs, missing entries).
6. Run quality gates: `./scripts/format.sh --fix`, `./scripts/lint.sh --all`, `python -m pytest tests/ -v`.

**Open Questions:**
1. Should service classes include an enum for names like characteristics do?
2. How to handle the distinction between service_class.* and profile.* ids in API design?
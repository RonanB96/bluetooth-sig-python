# AI Coding Agent Instructions (concise)

## Purpose

Clear, actionable checklist for AI agents working on Bluetooth SIG standards translation.

## References

- [Bluetooth SIG assigned numbers](https://www.bluetooth.com/specifications/assigned-numbers/)
- [Python documentation](https://docs.python.org/)

## Checklist for Every Agent Action

1. **Documentation First:** Always consult official SIG specs and Python docs before coding or refactoring.
2. **Quality Gates:** Run these before every commit:
    - `source .venv/bin/activate` Only needs to be done once per session.
    - `./scripts/format.sh --fix` Autofixes formatting issues.
    - `./scripts/format.sh --check` Checks formatting without fixing.
    - `./scripts/lint.sh --all` Lints all code.
    - `python -m pytest tests/ -v`
3. **Submodule:** Ensure `bluetooth_sig/` submodule is initialised and up to date.
4. **Registry Usage:** Never hardcode UUIDs. Use registry-driven name resolution for services and characteristics. Use `_service_name` or `_characteristic_name` only for non-standard names.
5. **Type Safety:** Use modern Python type hints and dataclasses. Prefer union syntax (`Class | None`).
6. **Validation:** Always validate input length, type, and value ranges per SIG spec. Use declarative validation attributes where possible.
7. **Error Handling:** Raise specific errors with clear messages referencing the characteristic/service. Handle SIG special values (infinity, NaN) as documented.
8. **Testing:** Add/maintain registry resolution and parsing tests for all new/changed characteristics/services. All tests must pass.
9. **Import Order:** Always use: future imports, stdlib, third-party, local imports (in that order). format --fix will enforce this.
10. **Integration:** Library must work with any BLE connection library. Use the documented three-step integration pattern.
11. **Legacy Support:** Ignore legacy code support until we have an official release, before this, we are still in the development phase.

---

## Human Implementation Patterns & Examples

See `docs/AGENT_GUIDE.md` for full implementation patterns, templates, rationale, and examples.

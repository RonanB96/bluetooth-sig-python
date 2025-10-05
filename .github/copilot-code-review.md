# AI Code Review Checklist (Pointer File)

This file intentionally contains only the live, minimal checklist. Full authoritative rules are in `.github/copilot-instructions.md` – that document is the single source of truth. Do not duplicate rules here.

## Minimal Review Checklist
Synchronised with Section 14 of `copilot-instructions.md`.

- [ ] Architecture: No forbidden framework imports in GATT/SIG layer.
- [ ] Registry: All UUIDs resolved via registry; none hardcoded.
- [ ] Parsing: Length/type/range validations per spec; sentinel handling.
- [ ] Timeouts: Explicit `timeout=10.0` in BLE connection logic.
- [ ] Types: Full type hints + dataclasses; no dynamic dict payloads.
- [ ] Tests: Success + ≥2 failure mode tests + registry resolution.
- [ ] Documentation: Docstrings, examples if new feature, CHANGELOG_NEW updated.
- [ ] Performance: No redundant discovery/connect; resources released.
- [ ] Security/Safety: No secrets; robust binary validation.
- [ ] Formatting/Linting: format, lint, static typing all clean.
- [ ] Spec References: Non-trivial logic cites spec section/table.

If any item cannot be ticked, the PR must not be approved.

## Reference
See `.github/copilot-instructions.md` for full rationale, workflow, prohibitions, and escalation process.

# AI Agent Operating & Review Guidelines

Unified rules for all automated and human AI assistant actions in this repository. This document REPLACES the previous separate "coding" and "code review" instruction files; the review file now only links back here to avoid drift.

---

## 1. Purpose & Scope
Provide a single, authoritative, non‑ambiguous operational standard for:
* Code generation & refactoring
* Parsing & validation of Bluetooth SIG data
* Pull request (PR) review and acceptance criteria
* Enforcement of architectural and safety boundaries

Applies to ALL contributions (automated or manual) within this repository.

---

## 2. Core Principles
1. Documentation before implementation (Bluetooth SIG + Python standard library).
2. Deterministic, spec‑driven parsing – never guess, never infer magically.
3. Strong typing & dataclasses – reject untyped, dict-centric patterns.
4. Registry over hardcoding – UUIDs resolved centrally; overrides explicit and justified.
5. Validation first, transformation second – length, type, range, special sentinel handling.
6. Single source of truth – no duplicated logic across characteristics/services.
7. Tests prove behaviour; no untested public behaviour admitted.
8. Architectural isolation – GATT layer MUST NOT import Home Assistant modules.
9. Security & safety – no silent truncation; fail loudly with explicit error types.
10. Idempotent formatting & linting – always pass quality gates before proposing completion.

---

## 3. Authoritative References
Mandatory sources to consult (cite when non-trivial logic added/changed):
* Bluetooth SIG Assigned Numbers: https://www.bluetooth.com/specifications/assigned-numbers/
* Relevant SIG specification PDFs for services/characteristics being implemented.
* Python Standard Library: https://docs.python.org/
* Project internal guides: `docs/AGENT_GUIDE.md`, `BLUETOOTH_SIG_ARCHITECTURE.md`, `UNIT_PROPERTY_REFACTOR_GUIDE.md`, `BASE_CLASS_REFACTORING_GUIDE.md`.

If an official spec segment is unavailable: explicitly state unavailability, list fallback source, and mark logic for later verification.

---

## 4. Mandatory Workflow (Every Change)
1. Research: Gather spec excerpts (length, units, encoding, special cases, valid ranges).
2. Design: Define dataclass fields, validation attributes, and error modes (include edge cases: empty payload, too short, too long, out-of-range, reserved value, NaN/infinity markers).
3. Implement: Pure functions / dataclasses; no side effects in parsing beyond raising errors.
4. Register: Use registry APIs for UUID name resolution – never embed raw UUID strings inline.
5. Test: Add/extend tests – success path + minimum 2 failure modes (length + range) + registry resolution.
6. Quality Gates (must all pass locally before PR / completion):
   * `./scripts/format.sh --fix`
   * `./scripts/format.sh --check`
   * `./scripts/lint.sh --all`
   * `python -m pytest tests/ -v`
7. Review Self‑Checklist (Section 14) – confirm all boxes can be ticked truthfully.

---

## 5. Architecture Boundaries
Forbidden: Any import from Home Assistant or other integration frameworks inside core GATT / SIG translation modules. The translation layer must remain framework‑agnostic to support multiple backends. Shared utility code must not leak framework abstractions.

---

## 6. Registry & UUID Usage
* No hardcoded UUID string literals in logic modules.
* Use registry resolution functions; supply `_service_name` / `_characteristic_name` ONLY for non‑standard or provisional names.
* Adding a new characteristic requires: registry entry, dataclass, tests validating name resolution, and parsing.
* Removing or renaming entries requires deprecation note in `CHANGELOG_NEW.md`.

---

## 7. Parsing & Validation Rules
For each characteristic:
* Validate payload length exactly (or declared variable length constraints) before decoding.
* Enforce numeric domain (min/max) per spec; replace ad‑hoc `if value < 0:` with declarative constraints.
* Handle special sentinel values (e.g. 0xFFFF meaning "unknown") mapping to `None` or documented sentinel object.
* Multi‑field bit parsing must use named bit field abstractions; avoid manual magic masks inline.
* Endianness explicit (`little` vs `big`). Never rely on default assumptions.
* Raise precise custom exception referencing the characteristic name & offending condition.

---

## 8. Types & Data Modelling
* Use `@dataclass(slots=True, frozen=True)` where immutability fits; mutable only if justified.
* Use `int`, `float`, `Decimal`, `Enum`, or purpose-specific tiny dataclasses – NO raw `dict` returns.
* Optional fields: `Type | None` not `Optional[Type]` unless generics demand.
* Provide docstrings with physical units where applicable (e.g. "Temperature in °C * 0.01 scaling").

---

## 9. Timeouts & Performance
* All BLE connection routines MUST specify `timeout=10.0` (or centrally configured constant if introduced later).
* Avoid redundant service discovery; cache structured discovery results where safe.
* Release/close BLE resources deterministically (context managers or explicit close calls).

---

## 10. Error Handling & Security
* Never swallow exceptions silently – rewrap with context if necessary.
* No hardcoded secrets or auth tokens.
* Bounds/length checks precede buffer slicing to avoid index errors.
* Reject malformed binary inputs early and clearly.

---

## 11. Testing Requirements
Each new / modified characteristic or service MUST include:
* Parsing success test (canonical example from spec table).
* Length violation test.
* Range violation or reserved value test.
* Registry name resolution test.
* (Where applicable) multi-packet / variable length handling test.

All tests must run via `pytest -v` and be deterministic (no reliance on live devices unless explicitly marked and skipped by default).

---

## 12. Documentation Requirements
* Public APIs: docstring first line = concise summary; subsequent lines detail parameters, returns, units, error conditions.
* Add usage examples to `examples/` where introducing new capability.
* Update `CHANGELOG_NEW.md` for user‑visible changes (additions, behaviour modifications, deprecations).

---

## 13. Prohibited Practices
* Hardcoded UUIDs
* Conditional imports for core logic
* Untyped public function signatures
* Silent exception pass / bare `except:`
* Returning unstructured `dict` / tuple when a dataclass or typed object fits
* Magic numbers without an inline named constant or spec citation
* Parsing without pre-validating length

---

## 14. Pull Request & Pre-Merge Review Checklist
Tick ALL before approval (automated agents must self‑verify):
[] Architecture: No forbidden framework imports in GATT/SIG layer.
[] Registry: All UUIDs resolved via registry; no hardcoded literals.
[] Parsing: Length/type/range validations implemented per spec.
[] Timeouts: Explicit `timeout=10.0` used where connections occur.
[] Types: Full type hints + dataclasses; no stray dynamic dict payloads.
[] Tests: Added/updated (success + at least 2 failure modes + registry resolution).
[] Documentation: Docstrings + examples (if new feature) + CHANGELOG_NEW.md updated.
[] Performance: No redundant discovery/connect cycles; resources released.
[] Security/Safety: No secrets; robust binary validation; clear failure modes.
[] Formatting/Linting: format, lint, mypy/pyright (if configured) all pass.
[] Spec References: Non-trivial logic cites spec section or assigned number table.

PRs failing any item must be revised; partial acceptance is not permitted.

---

## 15. Quick Reference Command Sequence
```
./scripts/format.sh --fix
./scripts/format.sh --check
./scripts/lint.sh --all
python -m pytest tests/ -v
```

---

## 16. Change Control & Drift Prevention
* This file is the single canonical AI guideline. The review checklist file only links here.
* Any modification MUST update date + summary in `CHANGELOG_NEW.md` if externally visible rules changed.
* Avoid duplicating fragments of this document elsewhere.

---

## 17. References (Repeat for Convenience)
* Bluetooth SIG Assigned Numbers – https://www.bluetooth.com/specifications/assigned-numbers/
* Python Standard Library – https://docs.python.org/
* Internal Guides – `docs/AGENT_GUIDE.md`, `BLUETOOTH_SIG_ARCHITECTURE.md`

---

## 18. Escalation Notes
If a spec ambiguity is encountered: document it inline (comment), add TODO with spec link placeholder, create issue referencing required clarification, proceed with safest conservative parsing (reject over guess).

---

Following these rules is mandatory; deviations must be justified explicitly in the PR description.

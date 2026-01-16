# Bluetooth SIG Standards Library - AI Agent Guidelines

**TL;DR**: Check docs → Run tests → Fix → Lint → Done

---

## Quick Start Checklist (Characteristic Implementation)

Before implementing a new characteristic:
- [ ] **SIG spec consulted**: Check Bluetooth SIG assigned numbers + GSS YAML
- [ ] **Think first**: Plan approach, edge cases, special values
- [ ] **Tests created**: Success + 2 failure cases minimum
- [ ] **Quality gates pass**: See validation commands below

---

## Prerequisites (BLOCKING)

**The Bluetooth SIG submodule MUST be initialized before any work can begin.**

```bash
git submodule init && git submodule update
python -c "import bluetooth_sig; print('✅ Ready')"
```

**Why this matters**: The registry system (`src/bluetooth_sig/registry/yaml_cross_reference.py`) loads UUID mappings from `bluetooth_sig/assigned_numbers/uuids/*.yaml`. Without the submodule, characteristic parsing and UUID resolution will fail at runtime. The code searches:
1. Development: `bluetooth_sig/assigned_numbers/uuids/`
2. Installed: `site-packages/bluetooth_sig/assigned_numbers/uuids/`

## Core Principles (Non-Negotiable)

### 1. Research First
**Document consultation is MANDATORY, not optional.**
- ALWAYS check official Bluetooth SIG specifications before implementing
- ALWAYS check Python stdlib docs for language features
- State explicitly: "Based on [specific documentation], the approach is..."
- If docs unavailable: state so explicitly and note verification needed

### 2. Think Before Acting
**Always use available thinking tools before making changes.**
- Before implementing: Think through approach, edge cases, and implications
- Before testing: Think through what could go wrong
- Before completing: Think through what might have been missed
- Use structured thinking for complex changes

### 3. Architecture Boundaries (ABSOLUTE)
<architecture>
**Forbidden imports in `src/bluetooth_sig/` modules:**
- `from homeassistant` or any HA framework code
- Integration-specific frameworks in core translation layer (`src/bluetooth_sig/gatt/`, `src/bluetooth_sig/registry/`)
- Any dependency that couples GATT parsing to a specific backend

**Violating this breaks the entire architecture. No exceptions.**

The translation layer must remain framework-agnostic to support multiple backends (bleak, simplepyble, etc.).
</architecture>

### 4. No Untested Code
**Testing is mandatory, not optional.**
- Every new function/method needs tests
- Minimum: success case + 2 failure cases
- Run full test suite before completion: `python -m pytest tests/ -v`
- Claiming "it works" without running tests is unacceptable

### 5. No Hardcoded UUIDs
**NEVER hardcode UUID strings in implementation code.**
- Use registry resolution: `CharacteristicName.BATTERY_LEVEL`
- Custom characteristics need `_info` attribute with proper `CharacteristicInfo`
- See: `.github/instructions/bluetooth-gatt.instructions.md` for details

### 6. Type Safety Required
**Every public function MUST have complete, explicit type hints.**
- Use modern union syntax: `Type | None` not `Optional[Type]`
- Use dataclasses for structured data - NEVER return raw `dict` or `tuple`
- See: `.github/instructions/python-implementation.instructions.md` for details

### 7. API Consistency
**Custom and SIG characteristics MUST have identical usage patterns.**
- Users should NOT need to know if characteristic is SIG-defined or custom
- Both must support same methods: `parse_value()`, `build_value()`
- **Primary API**: Direct characteristic/service classes (type-safe, IDE autocomplete)
- **Secondary API**: `BluetoothSIGTranslator` for unknown/scanned UUIDs (returns `Any`)
- See: `.github/instructions/bluetooth-gatt.instructions.md` for patterns

### 8. Quality Gates Must Pass
**All linting must pass before claiming completion.**
- Run `./scripts/lint.sh --all` before every completion, docs don't need this linter script to be ran
- Fix issues, don't suppress them unless documented
- The linter script is slow, so grepping or tailing the output is banned, pipe it to a file and read the file instead
- Never hide real problems with disables
- If fixing linting errors, rerun only that linting tool to speed up iteration, i.e. `./scripts/lint.sh --mypy`. Then rerun all at the end.

### 9. Documentation Policy
**Do NOT generate or update summary documentation unless explicitly requested.**
- ❌ **FORBIDDEN**: Updating README.md automatically
- ✅ **ALLOWED**: Inline code comments and docstrings (mandatory for new code)
- Focus on self-documenting code through clear naming and type hints

### 10. Problem-Solving Philosophy
**Fix root causes, don't hide symptoms.**
- Understand linting errors before suppressing
- Document reasoning with NOTE/TODO comments when suppressing
- If adding same disable to many files, **stop and reconsider approach
```

---

## Mandatory Workflow (Every Change)

<workflow>
1. **Research**: Gather spec excerpts (length, units, encoding, special cases, valid ranges)
2. **Think**: Use thinking tools to plan approach, consider edge cases
3. **Design**: Define dataclass fields, validation attributes, and error modes
4. **Implement**: Pure functions / dataclasses; no side effects in parsing beyond raising errors
5. **Register**: Use registry APIs for UUID name resolution
6. **Test**: Add/extend tests – success path + minimum 2 failure modes + registry resolution
7. **Quality Gates**: Run all validation commands (see below)
8. **Review**: Confirm all boxes in checklist can be ticked

</workflow>

---

## Quality Gates (Must ALL Pass)

<validation>
Run these commands before claiming completion:

```bash
./scripts/format.sh --fix
./scripts/format.sh --check
./scripts/lint.sh --all
python -m pytest tests/ -v
```

ALL must pass with zero errors. No exceptions.
</validation>

---

## Codebase Patterns (Concrete Examples)

### Three-Layer Architecture
```
src/bluetooth_sig/
├── core/              # BluetoothSIGTranslator, AsyncParsingSession
├── device/            # Device class (high-level abstraction)
├── gatt/              # GATT parsing - NO framework imports allowed
│   ├── characteristics/   # 200+ SIG characteristic implementations
│   └── services/          # Service definitions
└── registry/          # UUID resolution from YAML (bluetooth_sig/ submodule)
```

---

## Path-Specific Instructions

Additional guidelines apply based on file type. See `.github/instructions/` for detailed requirements:

- **Python Code**: `python-implementation.instructions.md` - Type hints, data modeling, error handling
- **Testing**: `testing.instructions.md` - Test structure, fixtures, coverage requirements
- **GATT Layer**: `bluetooth-gatt.instructions.md` - UUID registry, characteristic patterns, API consistency

These path-specific instructions are automatically loaded when working with matching files.

---

## Authoritative References

Mandatory sources to consult (cite when non-trivial logic added/changed):
- Bluetooth SIG Assigned Numbers: https://www.bluetooth.com/specifications/assigned-numbers/
- Relevant SIG specification PDFs for services/characteristics being implemented
- Python Standard Library: https://docs.python.org/
- Project internal guides: `docs/AGENT_GUIDE.md`, `docs/BLUETOOTH_SIG_ARCHITECTURE.md`

If an official spec segment is unavailable: explicitly state unavailability, list fallback source, and mark logic for later verification.

---

## Success Criteria

A task is considered complete when ALL of these are true:

□ Submodule initialized and verified
□ Official documentation consulted and cited
□ Type hints complete on all public functions
□ Tests created (success + 2 failure modes minimum)
□ All quality gates pass: format + lint + tests
□ No forbidden imports in `src/bluetooth_sig/`
□ UUIDs resolved through registry (no hardcoded strings)
□ API consistency maintained (SIG and custom characteristics identical usage)

---

## Escalation Notes

If a spec ambiguity is encountered: document it inline (comment), add TODO with spec link placeholder, create issue referencing required clarification, proceed with safest conservative parsing (reject over guess).

---

Following these rules is mandatory; deviations must be justified explicitly.


# Bluetooth SIG Standards Library - AI Agent Guidelines

**TL;DR**: Check docs → Run tests → Fix → Lint → Done

---

## ABSOLUTE PROHIBITIONS (Read This First)

**The following practices are FORBIDDEN. No exceptions. Violating these breaks the architecture:**

### ❌ NEVER Use:
- `TYPE_CHECKING` blocks or lazy imports in core logic
- Hardcoded UUID strings (use the lib to resolve from registry)
- `from typing import Optional` (use `Type | None`)
- Bare `except:` or silent `pass`
- Raw `dict`/`tuple` returns (use `msgspec.Struct`)
- Untyped public function signatures

**If you catch yourself typing any of the above, STOP. They are architectural violations.**

---

## Core Principles (Non-Negotiable)

### 1. Research First (MANDATORY)
Consult official Bluetooth SIG specs and Python stdlib docs before implementing. State source explicitly: "Per [X documentation]..." or note if unavailable.

### 2. Think Before Acting
Use available thinking tools before making changes—plan approach, edge cases, and implications.

### 3. Architecture Boundaries (ABSOLUTE)
`src/bluetooth_sig/` must remain framework-agnostic. NO imports from `homeassistant`, `bleak`, `simplepyble`, or any backend. Translation layer supports multiple backends.

### 4. No Untested Code
Every new function needs tests: success + 2 failure cases minimum. Run `python -m pytest tests/ -v` before claiming completion.

### 5. Quality Gates Must Pass
Run `./scripts/lint.sh --all` before completion (pipe to file, don't grep output). Fix issues, don't suppress them. For iteration, rerun only failing linter (`./scripts/lint.sh --mypy`), then rerun all at end.

### 6. Documentation Policy
**FORBIDDEN**: Updating README.md automatically
**ALLOWED**: Inline comments and docstrings (mandatory for new code)

---

## Workflow (Every Change)

1. **Research** → Consult specs, verify requirements, cite sources
2. **Think** → Plan approach, edge cases, implications
3. **Implement** → Pure functions/dataclasses following patterns (see path-specific instructions)
4. **Test** → Success + 2 failure cases minimum
5. **Validate** → Run quality gates (below)

---

## Quality Gates (Must ALL Pass)

```bash
./scripts/format.sh --fix
./scripts/format.sh --check
./scripts/lint.sh --all
python -m pytest tests/ -v
```

ALL must pass with zero errors. No exceptions.

---

## Architecture Overview

**Two-Tier API Design:**

1. **Direct Classes** (Type-Safe, Recommended):
   ```python
   from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
   char = BatteryLevelCharacteristic()
   level: int = char.parse_value(bytearray([85]))  # IDE knows return type
   ```

2. **Translator** (Dynamic, For Unknown UUIDs):
   ```python
   from bluetooth_sig import BluetoothSIGTranslator
   translator = BluetoothSIGTranslator()
   result = translator.parse_characteristic("2A19", bytearray([85]))  # Returns Any
   ```

Path-specific instructions (python-implementation, testing, bluetooth-gatt) load automatically based on file type.

---

## Authoritative References

Must consult and cite when adding non-trivial logic:
- Bluetooth SIG Assigned Numbers: https://www.bluetooth.com/specifications/assigned-numbers/
- Python Standard Library: https://docs.python.org/
- Project guides: `docs/AGENT_GUIDE.md`, `docs/BLUETOOTH_SIG_ARCHITECTURE.md`

If spec unavailable: state explicitly, note verification needed.

---

## Completion Checklist

Task complete when ALL true:
□ Submodule initialized, documentation cited
□ Tests pass (success + 2 failures), quality gates pass
□ No ABSOLUTE PROHIBITIONS violated (TYPE_CHECKING, lazy imports, hardcoded UUIDs, framework imports)
□ Type hints complete on all public functions

---

Following these rules is mandatory. Deviations require explicit justification.


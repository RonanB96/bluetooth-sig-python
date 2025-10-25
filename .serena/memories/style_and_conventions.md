______________________________________________________________________

## applyTo: '\*\*'

# Style and Conventions

- Use modern Python typing (`Type | None`, `list[str]`), every public function fully typed; justify any `Any` inline.
- Data returned via `@dataclass(slots=True, frozen=True)` where practical; avoid raw dict/tuple public returns.
- Import order: `from __future__ import annotations`, stdlib, third-party, then local modules.
- Never hardcode UUID strings; always resolve via registry helpers.
- Duplicate-code suppressions must be scoped with NOTE/TODO rationale per `.github/instructions/python-implementation.instructions.md`.
- Validate payload lengths, value ranges, and sentinel values per Bluetooth SIG specs; raise specific custom exceptions.
- Keep code framework-agnostic (no BLE library imports in core parsing layers).

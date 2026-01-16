---
applyTo: "**/*.py,**/pyproject.toml,**/requirements*.txt,**/setup.py"
---

# Python Implementation Guidelines

## Prohibited Practices (ABSOLUTE)

- Hardcoded UUIDs (use registry resolution)
- `from typing import Optional` (use `Type | None`)
- `TYPE_CHECKING` blocks
- Lazy/conditional imports in core logic
- Untyped public function signatures
- `hasattr`/`getattr` when direct access is possible
- Bare `except:` or silent `pass`
- Returning raw `dict` or `tuple` (use `msgspec.Struct`)
- Magic numbers without named constants
- Parsing without pre-validating length

## Type Safety (MANDATORY)

- All public functions MUST have complete type hints
- Use `Type | None` not `Optional[Type]`
- Use `from __future__ import annotations` for forward refs
- `Any` requires inline justification comment
- Return types are mandatory, no implicit returns

## Data Modelling

- Use `msgspec.Struct` for structured data (frozen, kw_only)
- Include docstrings with physical units
- Optional fields: `Type | None = None`

## Error Handling

- Raise precise custom exceptions from `bluetooth_sig.gatt.exceptions`
- Validate length before slicing: `if len(data) < N: raise InsufficientDataError(...)`
- Include characteristic name and offending value in error messages
- Never swallow exceptions silently

## Parsing Rules

- Validate payload length first
- Enforce numeric domain per spec
- Handle sentinel values (0xFFFF → `None`)
- Use named bit field abstractions, not magic masks
- Explicit endianness (`"little"` or `"big"`)

## Import Order

```python
from __future__ import annotations

# stdlib
import struct

# third-party
import msgspec

# local
from bluetooth_sig.gatt.exceptions import InsufficientDataError
```

## Docstrings

- Google style (Args, Returns, Raises)
- Focus on semantics, units, ranges - not type annotations
- Include spec references for non-obvious logic

## Code Duplication

- Never disable `duplicate-code` at module level
- If disabling at function level, include NOTE explaining why

## Quality Gates

```bash
./scripts/format.sh --fix
./scripts/format.sh --check
./scripts/lint.sh --all
python -m pytest tests/ -v
```

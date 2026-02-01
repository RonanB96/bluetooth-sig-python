---
applyTo: "**/*.py,**/pyproject.toml,**/requirements*.txt"
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

## Type Safety (MANDATORY)

- All public functions MUST have complete type hints
- Use `Type | None` not `Optional[Type]`
- `Any` requires inline justification

## Data Modelling

- Use `msgspec.Struct` (frozen, kw_only)

## Docstrings

- Google style (Args, Returns, Raises)
- Include spec references for non-obvious logic

## Quality Gates

```bash
./scripts/format.sh --fix
./scripts/format.sh --check
./scripts/lint.sh --all
python -m pytest tests/ -v
```

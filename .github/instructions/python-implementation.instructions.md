---
applyTo: "**/*.py,**/pyproject.toml,**/requirements*.txt"
---

# Python Implementation Guidelines

## Type Safety

- All public functions must have complete type hints
- `Type | None` not `Optional[Type]`
- `Any` requires inline justification comment
- Use `msgspec.Struct` (frozen, kw_only) for data containers — never raw `dict`/`tuple`

## Imports

- No `TYPE_CHECKING` blocks in core logic
- No lazy/conditional imports except cycle-breaking with a `# NOTE:` comment
- No magic numbers without named constants

## Docstrings

Google style (Args, Returns, Raises). Include spec references for non-obvious logic.

## Quality Gates

```bash
./scripts/format.sh --fix
./scripts/lint.sh --all
python -m pytest tests/ -v
```

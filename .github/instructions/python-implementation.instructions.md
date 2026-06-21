---
description: Python coding standards, type safety, and data modelling
globs: "**/*.py,**/pyproject.toml,**/requirements*.txt"
alwaysApply: false
applyTo: "**/*.py,**/pyproject.toml,**/requirements*.txt"
---

# Python Implementation Guidelines

## Type Safety

- All public functions must have complete type hints
- `Type | None` not `Optional[Type]`
- `Any` requires inline justification comment
- Use `msgspec.Struct` (frozen, kw_only) for data containers — never raw `dict`/`tuple`

## Imports

**Default: top-of-module imports.** Put `import` / `from … import` at module scope so
dependencies are visible, import errors fail early, and static analysis works.

**Avoid ad-hoc deferred imports** — do not hide imports inside functions, methods, or
`if` blocks in business logic. That pattern obscures dependencies, makes failures
runtime-only, and is hard to audit. Prefer restructuring modules or breaking import cycles
instead.

**Approved exceptions** (narrow, documented, centralized — not scattered):

1. **Import-cycle breaking** — defer one side of a cycle with a local import and a
   `# NOTE: deferred import breaks cycle with …` comment. Use only when module layout
   cannot remove the cycle.
2. **PEP 562 GATT package barrels** — see `bluetooth-gatt.instructions.md` (Lazy export
   maps). Do not add manual lazy imports elsewhere.

**Not allowed in core logic:**

- `TYPE_CHECKING` blocks (use `from __future__ import annotations` and direct imports)
- New barrel files that eagerly re-export large module trees
- Function-scoped imports for convenience or micro-optimisation

## Constants

- No magic numbers without named constants

## Docstrings

Google style (Args, Returns, Raises). Include spec references for non-obvious logic.

## Quality Gates

```bash
./scripts/format.sh --fix
./scripts/lint.sh --all
python -m pytest tests/ -v
```

---
applyTo: "**/*.py,**/pyproject.toml,**/requirements*.txt"
---

# Python Implementation Guidelines

## Prohibited Practices (ABSOLUTE)

- Hardcoded UUIDs (use registry resolution)
- `from typing import Optional` (use `Type | None`)
- `TYPE_CHECKING` blocks
- Lazy/conditional imports in core logic (deferred imports to break cycles are acceptable with a valid `# NOTE:` comment)
- Untyped public function signatures
- `hasattr`/`getattr` when direct access is possible
- Bare `except:` or silent `pass`
- Returning raw `dict` or `tuple` (use `msgspec.Struct`)
- Setting `_python_type` on new characteristics (`BaseCharacteristic[T]` generic param auto-resolves)
- Magic numbers without named constants

## Type Safety (MANDATORY)

- All public functions MUST have complete type hints
- Use `Type | None` not `Optional[Type]`
- `Any` requires inline justification

## Data Modelling

- Use `msgspec.Struct` (frozen, kw_only)

## Characteristic Implementation Patterns

- **Simple scalars:** Use a template from `templates/` package (`Uint8Template`, `ScaledUint16Template`, etc.)
- **Multi-field composites:** Override `_decode_value()`, use `DataParser` for field extraction, return `msgspec.Struct`
- **Parsing pipeline:** Use `pipeline/parse_pipeline.py` for multi-stage decode with validation
- **Core modules:** `core/encoder.py` for Python→bytes, `core/parser.py` for bytes→Python, `core/query.py` for lookups

## Peripheral Device Patterns

- `PeripheralDevice` (in `device/peripheral_device.py`) for server-side BLE
- `PeripheralManagerProtocol` (in `device/peripheral.py`) for adapter abstraction
- Fluent configuration: `device.with_name(...).with_service(...)`

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

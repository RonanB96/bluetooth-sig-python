---
description: GATT layer, templates, pipeline, and characteristic implementation patterns
globs: src/bluetooth_sig/gatt/**/*.py,src/bluetooth_sig/registry/**/*.py
alwaysApply: false
applyTo: "src/bluetooth_sig/gatt/**/*.py,src/bluetooth_sig/registry/**/*.py"
---

# Bluetooth GATT Layer Guidelines

**CRITICAL** Hardcoding UUIDs in the code is strictly prohibited.

## Characteristic Implementation

**Responsibility split:**
- `BaseCharacteristic` handles length/range/special-value validation automatically
- `_decode_value()` only: parse bytes, apply scaling, return typed result
- `_encode_value()` only: reverse of decode

**Choosing a pattern:**
- Simple scalar → pick a template from `templates/` (numeric, scaled, string, enum, flag, ieee_float, domain, etc.)
- Multi-field composite → override `_decode_value()`, return `msgspec.Struct`
- Enum/bitfield → `IntFlag` + `EnumTemplate` or `FlagTemplate`
- Multi-stage decode → use `pipeline/`

**SIG vs custom:** SIG characteristics auto-resolve UUID from registry. Custom characteristics require `_info = CharacteristicInfo(...)`.

## Lazy export maps (ADR-011)

GATT barrels (`characteristics`, `services`, `descriptors`) use PEP 562 via
`gatt/lazy_exports.py`. Do not add eager re-exports to `__init__.py`. After adding a
module, regenerate:

```bash
python scripts/generate_lazy_exports.py
```

Do not import sibling characteristic modules from `base.py` or templates.

## Decision-Critical Rules

- **Multi-byte values: little-endian.** SIG spec mandates this universally.
- **Never set `_python_type`** — `BaseCharacteristic[T]` auto-resolves it from the generic parameter.
- **`dict` is banned as a return type.** Use `msgspec.Struct` (frozen, kw_only).

## Reference Exemplars

Study existing characteristic modules and templates before implementing new characteristics.

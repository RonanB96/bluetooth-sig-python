---
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

## Decision-Critical Rules

- **Multi-byte values: little-endian.** SIG spec mandates this universally.
- **Never set `_python_type`** — `BaseCharacteristic[T]` auto-resolves it from the generic parameter.
- **`dict` is banned as a return type.** Use `msgspec.Struct` (frozen, kw_only).

## Reference Exemplars

Study existing characteristic modules and templates before implementing new characteristics.

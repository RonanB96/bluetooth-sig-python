---
applyTo: "src/bluetooth_sig/gatt/**/*.py,src/bluetooth_sig/registry/**/*.py"
---

# Bluetooth GATT Layer Guidelines

## Architecture Boundaries (ABSOLUTE)

**Forbidden imports in `src/bluetooth_sig/`:**
- `from homeassistant` or any framework code
- `from bleak` / `from simplepyble` or any BLE backend

## UUID Policy (ABSOLUTE)

**NEVER hardcode UUID strings.**

UUIDs only in: YAML submodule, test fixtures, custom `_info` definitions.

## API Consistency

SIG characteristics auto-resolve UUID. Custom require `_info = CharacteristicInfo(...)`

## Implementation

**BaseCharacteristic handles:** Length/range/special value validation

**Your `_decode_value()` only:** Parse bytes using templates, apply scaling, return typed result

**Patterns:**
- Simple value → Use template (`Uint8Template`, etc.)
- Multi-field → Override `_decode_value()`, return `msgspec.Struct`
- Enum/bitfield → Use `IntFlag`

**Standards:**
- Multi-byte: little-endian

**Reference:** See `battery_level.py`, `heart_rate_measurement.py`, `templates.py`

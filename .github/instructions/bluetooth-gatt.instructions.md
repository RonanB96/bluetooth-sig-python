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

**`_python_type` is auto-resolved** from `BaseCharacteristic[T]` generic parameter. Never set `_python_type` on new characteristics — the generic param and template already provide the type. `dict` is banned.

**Patterns:**
- Simple value → Use template from `templates/` package (`Uint8Template`, `ScaledUint16Template`, etc.)
- Multi-field → Override `_decode_value()`, return `msgspec.Struct`
- Enum/bitfield → Use `IntFlag`
- Parsing pipeline → `pipeline/parse_pipeline.py` for multi-stage decode, `pipeline/encode_pipeline.py` for encode, `pipeline/validation.py` for range/type/length checks

**Templates package** (`gatt/characteristics/templates/`):
- `numeric.py` — `Uint8Template`, `Uint16Template`, `Sint8Template`, etc.
- `scaled.py` — `ScaledUint8Template(d=N, b=N)`, `ScaledSint16Template`, etc.
- `string.py` — `Utf8StringTemplate`
- `enum.py` — `EnumTemplate`
- `ieee_float.py` — `IEEE11073FloatTemplate`, `IEEE11073SFloatTemplate`
- `composite.py` — `CompositeTemplate`
- `domain.py` — domain-specific templates
- `data_structures.py` — structured data templates
- `base.py` — `CodingTemplate` base class

**Core decomposition** (`core/`):
- `query.py` — characteristic/service lookup
- `parser.py` — raw bytes → Python values
- `encoder.py` — Python values → raw bytes
- `registration.py` — custom characteristic/service registration
- `service_manager.py` — service lifecycle management
- `translator.py` — public facade (`BluetoothSIGTranslator`)

**Standards:**
- Multi-byte: little-endian

**Reference:** See `battery_level.py`, `heart_rate_measurement.py`, `templates/`

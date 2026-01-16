---
applyTo: "src/bluetooth_sig/gatt/**/*.py,src/bluetooth_sig/registry/**/*.py"
---

# Bluetooth GATT Layer Guidelines

## Architecture Boundaries (ABSOLUTE)

**Allowed imports:**
- `gatt/` → can import from: `types`, `utils`, `registry`
- `registry/` → can import from: `types`, `utils`
- `types/` → pure types, no internal imports
- `utils/` → can import from: `types`

**Forbidden imports in `src/bluetooth_sig/`:**
- `from homeassistant` or any HA framework code
- `from bleak` / `from simplepyble` or any BLE backend
- Any framework coupling the translation layer to a specific backend

## UUID Policy (ABSOLUTE)

**NEVER hardcode UUID strings in implementation code.**

UUIDs appear ONLY in:
1. YAML files in `bluetooth_sig/` submodule (source of truth)
2. Test fixtures (for validation)
3. Custom characteristic `_info` definitions

Use `uuid_registry.get_characteristic_info(CharacteristicName.X)` for lookups.

## API Consistency (CRITICAL)

**Custom and SIG characteristics MUST have identical usage patterns:**
- Public methods: `parse_value()`, `build_value()`
- SIG characteristics auto-resolve UUID from class name
- Custom characteristics require `_info = CharacteristicInfo(uuid=..., name=...)`

**Primary API**: Direct characteristic/service classes (type-safe)
**Secondary API**: `BluetoothSIGTranslator` for unknown UUIDs (returns `Any`)

## Characteristic Implementation Rules

**BaseCharacteristic handles (DO NOT duplicate):**
- Length validation via `min_length`, `max_length`, `allow_variable_length`
- Special/sentinel values via GSS spec or `_special_values`
- Range validation via `min_value`, `max_value`

**Your `_decode_value()` should ONLY:**
1. Parse raw bytes using templates or `DataParser`
2. Apply scaling/conversions per spec
3. Return typed result

**Method signature:**
```python
def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> T:
```

**Pattern selection:**
- Simple single-value → Use template (`Uint8Template`, `ScaledSint16Template`, etc.)
- Structured multi-field → Override `_decode_value()`, return `msgspec.Struct`
- Enum/bitfield → Use `IntFlag` enum

**Reference implementations:** See `battery_level.py`, `heart_rate_measurement.py`, `temperature.py`

## Parsing Standards

Per Bluetooth SIG specifications:
- All multi-byte values: **little-endian**
- Temperature: sint16, 0.01°C resolution
- Humidity: uint16, 0.01% resolution
- Pressure: uint32, 0.1 Pa resolution
- Special values: 0x8000/0xFFFF typically mean "unknown"

## Implementation Checklist

Before implementing a new characteristic:
1. Is it in SIG assigned numbers? → Class name auto-resolves, no `_info` needed
2. Is it vendor-specific? → Set `_info` with UUID and name
3. Can a template handle it? → Check `templates.py`
4. What validation attributes? → Set `min_length`, `max_length`, `expected_length`
5. Any special values? → Check GSS spec, framework handles automatically
6. What's the spec say? → Cite Bluetooth SIG documentation

## References

- Existing characteristics: `src/bluetooth_sig/gatt/characteristics/`
- Templates: `src/bluetooth_sig/gatt/characteristics/templates.py`
- Base class: `src/bluetooth_sig/gatt/characteristics/base.py`
- Services: `src/bluetooth_sig/gatt/services/`

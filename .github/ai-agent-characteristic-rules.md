# AI Agent Rules — GATT Characteristic Implementations

Purpose

Provide a concise, enforceable checklist for automated agents or contributors implementing files under `src/bluetooth_sig/gatt/characteristics/`.

Core principle

- Characteristics implement ONLY field-specific parsing, sentinel mapping, scaling and construction of typed return values.
- All generic validation (length, type, range) MUST be declared as class attributes and is enforced by `BaseCharacteristic.parse_value()`.

Templates & reuse

- Reuse `templates` helpers when a characteristic matches an existing template. Do not copy template parsing into concrete characteristics.
- Extend templates by composition/wrapping rather than duplicating parsing code.

Registry (GSS/YAML) guidance

- YAML registry entries are authoritative for field sizes, data types and encoding. Consult the YAML entry before implementing parsing.
- Use these helpers where available:
  - `get_yaml_data_type()` — select DataParser primitive
  - `get_yaml_field_size()` — set `expected_length` / `min_length`
  - `is_signed_from_yaml()` — determine signed vs unsigned

Data parsing rules

- Use `DataParser` and `ieee11073` helpers for primitive reads/writes (e.g. `parse_int16`, `parse_int32`).
- Use a `pos` offset for multi-field parsing and let helpers raise `InsufficientDataError` when bytes are insufficient.
- Map sentinel/special values to `None` only after parsing the raw field.

Constants & magic numbers

- Replace inline magic numbers with named constants and a one-line comment (lengths, sentinel values, scales, masks, shifts).
- Constants placement:
  - Shared across characteristics → `src/bluetooth_sig/gatt/constants.py` or `src/bluetooth_sig/types/constants.py`.
  - Characteristic-local → class-level constant inside the characteristic file.

Encode/decode symmetry

- Implement `encode_value` as the logical inverse of `decode_value` using `DataParser.encode_*` helpers. Ensure field sizes, endianness and scales match the YAML spec.

Bitfields & flags

- Define masks/shifts and prefer `enum.IntFlag` when reusable. Return typed booleans or flags in outputs and document bit meanings in the docstring.
- Do NOT use plain `int` for enumerated values — use `enum.Enum` or `enum.IntFlag` for type safety and readability.
- For bit fields representing presence flags or other bit masks, use `enum.IntFlag` for type safety.

Forbidden patterns (MUST NOT)

- Do NOT perform length, range, or type validation inside `decode_value`/`encode_value` — `BaseCharacteristic` handles these.
- Do NOT reimplement endianness/signed parsing or use manual `int.from_bytes` where `DataParser` exists.
- Do NOT hardcode SIG UUIDs in parsing logic; use registry resolution or `_info = CharacteristicInfo(...)` only for vendor metadata.
- Do NOT return sentinel integers or raw bytes as "unknown" — map to `None` explicitly.

Docs & metadata

- Docstring must include: UUID/name, format/length, endianness, units, scale factor, sentinel values and mapping, bitfield layout, raised exceptions, and an example hex payload.

Testing requirements

- Each characteristic must include tests: one success case and at least two failure cases (insufficient data + invalid/out-of-range). Tests must assert exception types and `CharacteristicData` semantics.

CI / machine checks (suggested)

- Fail if `int.from_bytes` appears in `gatt/characteristics/`.
- Fail if `len(data)` checks or `raise InsufficientDataError` occur inside `decode_value`/`encode_value` for checks that class attributes cover.
- Fail if inline magic numeric literals appear near parsing code.

Example automation regexes (adjust before use)

- `\bint\.from_bytes\b`
- `if\s+len\(data\)\s*[!=<]`
- `raise\s+InsufficientDataError\(`
- `\b0x[0-9A-Fa-f]+\b` (for hex literals near parsing)

Quick DO / DO NOT

- DO: declare `expected_length = 4` then `raw = DataParser.parse_int32(data, 0, signed=True); return None if raw == VALUE_NOT_KNOWN else raw * SCALE`
- DO NOT: `if len(data) != 4: raise InsufficientDataError(...); raw = int.from_bytes(data[:4], 'little', signed=True)`

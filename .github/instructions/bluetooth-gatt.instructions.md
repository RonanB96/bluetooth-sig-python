---
description: GATT layer, templates, pipeline, and characteristic implementation patterns
globs: src/bluetooth_sig/gatt/**/*.py,src/bluetooth_sig/registry/**/*.py
alwaysApply: false
applyTo: "src/bluetooth_sig/gatt/**/*.py,src/bluetooth_sig/registry/**/*.py"
---

# Bluetooth GATT Layer Guidelines

Global rules (no hardcoded UUIDs, no `dict`/`tuple` returns, no `Optional`, never set
`_python_type`, etc.) live in `copilot-instructions.md` — they are not repeated here.
The GSS YAML in `bluetooth_sig/gss/` plus the SIG spec are the source of truth; read
them before writing code.

## What a characteristic module contains

A characteristic class maps bytes ⇄ one typed value. It contains ONLY:

- Class-level validation declarations: `expected_length`, `min_length`, `max_length`,
  `allow_variable_length`, `min_value`, `max_value`.
- Either a `_template` (scalars) OR `_decode_value()`/`_encode_value()` (composites).
- The `IntEnum` / `IntFlag` / `msgspec.Struct` that defines its typed value.

It must NOT contain:

- Redundant total-length/range checks — declare the class attributes and let the
  pipeline enforce the overall envelope (see "Where validation lives"). A
  `len(data) != expected_length` / out-of-range guard that just repeats a declared
  constraint is redundant; delete it.
- Pass-through helpers that just forward to another call — call the real API directly.
- Soft types where the spec defines structure. Model enumerations as `IntEnum`,
  bitfields as `IntFlag`, UUIDs as `BluetoothUUID`, multi-field values as
  `msgspec.Struct`. Absent optional fields are `None`, never `b""`/`0`.

## Choosing a pattern (study these exemplars)

| Wire shape | Approach | Exemplar |
| --- | --- | --- |
| Scaled scalar | a `templates/` template via factory | `electric_current.py` (`ScaledUint16Template.from_letter_method`) |
| Enum value | `EnumTemplate.uint8(MyEnum)` | `alert_level.py` |
| Bitfield | `FlagTemplate.uint16(MyFlags)` | `device_time_feature.py` |
| UTF-8 string | `Utf8StringTemplate()` | `emergency_text.py` |
| Fixed multi-field struct | override `_decode_value`/`_encode_value`, return a `msgspec.Struct` | `average_current.py` |
| Opcode + optional params (variable length) | `IntEnum` opcode + struct, `_manual_role = CharacteristicRole.CONTROL` | `audio_input_control_point.py` |

Use the template factory constructors (`EnumTemplate.uint8`, `FlagTemplate.uint16`,
…). Don't hand-assemble a template with `cast(...)` and raw extractors.

## Where validation lives

`BaseCharacteristic` + the parse/encode pipeline (`pipeline/`) validate the
**top-level value**: byte length, numeric range, type, and GSS special values. You
declare the constraints as class attributes — see `expected_length`/`min_length` in
`average_current.py` and `min_length`/`max_length`/`allow_variable_length` in
`plx_features.py`. Do not re-implement these checks by hand.

Special values (e.g. "value is not known") come from the GSS YAML and raise
`SpecialValueDetectedError` automatically for templated scalars. Never catch one and
return it as a normal value.

For variable-length composites the pipeline only validates the outer envelope
(`min_length`/`max_length`/`allow_variable_length`). It does NOT know your internal
layout, so before slicing each optional/conditional segment you must check enough
bytes remain — e.g. `audio_input_control_point.py` gates the `gain_setting` byte on
both the opcode and `len(data) >= _MIN_LENGTH_WITH_GAIN`. These per-field bounds
checks are required, not redundant.

What the pipeline cannot reach, you must validate explicitly inside `_decode_value`
(raising `ValueError`):

- Enum/flag membership — constructing `MyEnum(raw)`/`MyFlags(raw)` rejects undefined
  values; reserved (RFU) bits in a bitfield are documented and rejected
  (`device_time_feature.py`, `plx_features.py`).
- Cross-field rules the YAML can't express (mutual exclusion, presence flags gating
  optional fields — see `audio_input_control_point.py`).

## Context is additive, not required

`_decode_value`'s `ctx` (descriptors, other characteristics) defaults to `None` and
is **enrichment**. A characteristic must decode from its own bytes alone; declared
descriptor/characteristic dependencies are additive. Do NOT raise just because `ctx`
is missing.

The only exception is when the spec defines a field's format/size/meaning *through*
that context — then it is genuinely required and you raise when it is absent. Proven
example: `cookware_sensor_data.py`, where CWS v1.0 §3.8.1.2 + Table 3.17 make the
Cooking Sensor Info descriptor mandatory and define the variable Sensor Data field's
type and size by that descriptor's UUID. Cite the spec section when you require
context; otherwise treat it as optional.

## Constants

- Generic byte sizes: reuse `SIZE_UINT8`, `SIZE_UINT16`, `SIZE_UUID16`, … from
  `gatt/constants.py`. Don't write literal `2`/`16`.
- Constants shared across a characteristic family go in that family's `*_common.py`,
  not duplicated per module.

## Decision-critical reminders

- Multi-byte values are little-endian (SIG-wide).
- SIG characteristics auto-resolve their UUID from the registry; custom ones need
  `_info = CharacteristicInfo(...)`.

## Lazy export maps (ADR-011)

GATT barrels (`characteristics`, `services`, `descriptors`) use PEP 562 via
`gatt/lazy_exports.py`. Don't add eager re-exports to `__init__.py`, and don't import
sibling characteristic modules from `base.py` or templates. After adding a module:

```bash
python scripts/generate_lazy_exports.py
```

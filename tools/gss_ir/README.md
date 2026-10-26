# GSS IR v1 Contract

This package defines the supported build-time contract between Bluetooth SIG GSS normalisation,
C table generation, and the desktop `RuntimeIrBackend`. It is tooling and is not imported by the
Python runtime package.

## Authority and boundaries

- Read-only SIG YAML is the build-time source of truth. Only `tools/gss_ir/sources/` reads it.
- `schema_version` remains 1 until this development line is released. `v1.py` rejects every other version.
- The normaliser joins layout data with assigned numbers. The emitter reads IR only and writes C.
- Runtime code does not import this package.

## Version and canonical JSON

`schema_version` stays the integer `1` until this development line is released.
A decoder must reject every other value with `unsupported_version`. Fields added
while this line is in development stay on version 1.

Canonical JSON is compact UTF-8 emitted in `msgspec.Struct` declaration order, uses JSON integers for all
numeric contract values, omits fields at their declared defaults, and has no trailing whitespace. Transforms
avoid binary floating ambiguity:

```text
decoded = raw * coefficient * 10^decimal_exponent * 2^binary_exponent
```

`decode_ir(..., require_canonical=True)` rejects semantically valid but differently formatted JSON.
`encode_json_schema()` provides a generated interoperability schema; typed decode plus semantic
validation remains authoritative for cross-field invariants.

## Document

A document has `schema_version`, `identifier`, a 16-bit `uuid`, `provenance` (`source_path`,
`source_identifier`), and one or more scalar `fields`. Each field has a `snake_case` `name`, an integer
`wire_type` (`uint8`, `uint16`, `uint24`, `uint32`, `uint48`, `uint64`, `sint8`, `sint16`, `sint24`,
`sint32`, `boolean8`, `boolean16`, `boolean24`, `boolean32`, `medfloat16`, `medfloat32`, `float32`),
raw `minimum` and `maximum`, an optional `transform`, an optional `unit`, and `sentinels`.
GSS `boolean[N]` and `int16` are stored as those enumerator names. `medfloat16`, `medfloat32`, and
`float32` keep the little-endian bit pattern in `minimum`/`maximum`; the generated member is the
decoded `double`. A boolean or real field with no numeric range uses every bit pattern of its width.
`utf8s` and `utf8s{N}` are wire type `utf8`. `utf8_capacity` stores the octet maximum: `N` for `utf8s{N}`, or the high end of a size range starting at 0. A `variable` size with no maximum omits it, and the generated array bound is the 512-octet ATT value limit (Core Specification v5.4, Vol 3, Part F, 3.2.9). The wire image is the text octets, from 0 through that maximum. The field is the whole characteristic value. The generated member is one counted value: `size` plus `data[capacity]`. Sub-byte `uint1` and `uint2` are packed from bit 0 of the first octet, least significant bit first. A GSS value table of discrete codes sets `value_set` to `enumeration` and stores each code in `enumerators`. A table of named bits sets `value_set` to `flags`; each enumerator is the mask `1 << bit`, and a reserved or RFU bit is omitted. The generated member is a C `enum`. A flags member is unsigned and wide enough for every named bit. A closed code set stays a signed enumeration when every code fits in `int`. The enumeration is wider than the wire field. C11 gives an `enum` no underlying type. The generated source `_Static_assert`s that `sizeof` the enumeration is 4, and the build does not pass `-fshort-enums`. The descriptor still records the wire width. A code outside the enumerators, or a flags value with a bit outside the mask, is out of range. A packed multi-bit group inside a flags word stays an integer. `gatt_uuid` and repeated fields stay unsupported.
An absent transform means coefficient 1, decimal exponent 0, and binary exponent 0. A sentinel meaning
is `not_known` or `not_valid`. A referenced characteristic is copied into the field; the document has
no cross-document reference.

`v1.schema.json` is the frozen JSON Schema. Typed decode plus `validate_ir` remains authoritative for
cross-field invariants. Contract tests use neutral schema objects. Source-backed golden IR is produced
by the normaliser from SIG YAML.

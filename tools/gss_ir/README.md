# GSS IR v1 Contract

This package defines the supported build-time contract between Bluetooth SIG GSS normalisation,
C++ table generation, and the desktop `RuntimeIrBackend`. It is tooling and is not imported by the
Python runtime package.

## Authority and boundaries

- Read-only SIG YAML is the build-time source of truth. Only `tools/gss_ir/sources/` reads it.
- Schema version 1 is the fixed-field document in ADR-0003. `v1.py` decodes that document and rejects
  any other shape, including the prototype field kinds.
- The normaliser joins layout data with assigned numbers. The C++ emitter reads IR only.
- Runtime code does not import this package.

## Version and canonical JSON

`schema_version` is the integer `1`. A decoder must reject every other value with
`unsupported_version`. Adding or changing a field kind, predicate kind, primitive meaning, or transform
meaning requires a new major schema version.

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
`sint32`), raw `minimum` and `maximum`, an optional `transform`, an optional `unit`, and `sentinels`.
An absent transform means coefficient 1, decimal exponent 0, and binary exponent 0. A sentinel meaning
is `not_known` or `not_valid`. A referenced characteristic is copied into the field; the document has
no cross-document reference.

`v1.schema.json` is the frozen JSON Schema. Typed decode plus `validate_ir` remains authoritative for
cross-field invariants. Contract tests use neutral schema objects. Source-backed golden IR is produced
by the normaliser from SIG YAML.

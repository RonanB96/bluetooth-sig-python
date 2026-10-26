# Architectural Decision Records

These records describe the characteristic codec as it is built. The library is a C11 codec for Bluetooth SIG characteristics. A decode and encode path for every characteristic is the goal of the library.

ADR-001 to ADR-011 described the former Python runtime. That package is under `archived/python-lib/`. Those records are superseded by ADR-012.

## ADR-012: C11 core and libm

**Accepted** | Proposed | Rejected | Superseded | Deprecated

**Date**: 2026-10-26

**Supersedes**: ADR-001, ADR-002, ADR-003, ADR-004, ADR-007, ADR-008, ADR-009, ADR-010, ADR-011

### Context

The codec has to stay small, express each characteristic value as a concrete C type, and perform IEEE-11073 and decimal scaling without a C++ runtime.

### Decision

The core is C11. `btsig_types`, `btsig_schema`, `btsig_wire`, `btsig_codec`, and `btsig_characteristics` are C targets (`btsig/modules/CMakeLists.txt`). `btsig_wire` and `btsig_codec` link libm. IEEE-11073 conversion uses `double` and calls `isnan`, `isinf`, and `fabs` (`btsig/modules/wire/src/medfloat.c`). The scale `raw * coefficient * 10^decimal_exponent * 2^binary_exponent` is `double` arithmetic in `btsig_codec_decode` and `btsig_codec_encode` (`btsig/modules/codec/src/codec.c`).

A call returns `btsig_error`. `btsig_status` names the outcome, including insufficient data, length mismatch, unknown UUID, out of range, buffer too small, invalid argument, not known, and not valid (`btsig/modules/types/include/btsig/types/status.h`). Public headers keep an `extern "C"` block so a C++ translation unit can call the C API (`btsig/modules/codec/include/btsig/codec/codec.h`).

### Consequences

#### Positive

- **POS-001**: One C11 dialect for the core. Callers link C objects and libm.
- **POS-002**: Each failure is a status value with the field name and the bytes involved.
- **POS-003**: A C++ caller can include the C headers. The core does not require the C++ standard library.

#### Negative

- **NEG-001**: `double` is the scaled and real value type. Integer wire values that are not scaled stay integers.
- **NEG-002**: libm is a link dependency of `btsig_wire` and `btsig_codec`.
- **NEG-003**: Status codes replace exceptions. Callers check `btsig_error.status`.

### Alternatives Considered

#### C++ core

- **ALT-001**: **Description**: Characteristic types, `std::expected`, and spans in C++ headers.
- **ALT-002**: **Rejection Reason**: The core is C11 and libm. Those C++ headers are removed.

#### Python objects as the codec result

- **ALT-003**: **Description**: Parse into Python structs at the centre of the library.
- **ALT-004**: **Rejection Reason**: The codec result is a C struct and a `btsig_error`. A Python API is deferred (ADR-015).

### Implementation Notes

- **IMP-001**: C standard 11, extensions off, for the wire, codec, and characteristic targets.
- **IMP-002**: Compile with `-Wall -Wextra -Wpedantic -Werror -Wshadow -Wundef` through `btsig::warnings`.

### References

- **REF-001**: ADR-013 for the descriptor and generated struct.
- **REF-002**: ADR-015 for what this library includes.

## ADR-013: One descriptor-driven codec

**Accepted** | Proposed | Rejected | Superseded | Deprecated

**Date**: 2026-10-26

**Supersedes**: ADR-003, ADR-004

### Context

Characteristics share wire widths, ranges, sentinels, units, and the same scale formula. A separate parser class per characteristic duplicates that logic.

### Decision

One codec interprets a `btsig_characteristic_descriptor`. A field descriptor holds ranges, a flag mask, offsets, the wire type, the value kind, and the scale integers. It holds no pointers. Names, units, sentinels, and allowed values are addressed from the characteristic descriptor that owns the field, so the field table can stay in flash (`btsig/modules/schema/include/btsig/schema/descriptor.h`, `BTSIG_SCHEMA_VERSION` 1).

The emitter writes a typed struct, a `const` descriptor, and `btsig_decode_<name>` / `btsig_encode_<name>`. Those functions call `btsig_codec_decode` and `btsig_codec_encode` with `sizeof` the struct (`tools/gss_ir/emit_cpp.py`). An integer member stores the raw value. A scaled member, and `medfloat16`, `medfloat32`, and `float32`, store a `double`. A UTF-8 member is `uint16_t size` plus `uint8_t data[capacity]`. A closed code set or a named flag word is a C enum. The generated translation unit static-asserts the schema version, the struct size, each member offset, and each enumeration width.

### Consequences

#### Positive

- **POS-004**: Wire rules live in one codec. A generated characteristic adds data and a typed struct.
- **POS-005**: Field tables do not embed pointers.
- **POS-006**: The C type of each member is fixed when the source is generated. The static asserts check size and offset.

#### Negative

- **NEG-004**: A layout the descriptor cannot express needs a handwritten codec (ADR-014).
- **NEG-005**: The emitter module is still named `tools.gss_ir.emit_cpp`. It writes C and deletes a stale `.hpp` or `.cpp` for that characteristic.

### Alternatives Considered

#### One hand-written parser per characteristic

- **ALT-005**: **Description**: Each characteristic implements its own decode and encode.
- **ALT-006**: **Rejection Reason**: Shared wire, range, sentinel, and scale behaviour would be copied into every characteristic.

#### C++ templates as the shared parser

- **ALT-007**: **Description**: A template per wire type, composed into each characteristic.
- **ALT-008**: **Rejection Reason**: The shared parser is the C codec and a descriptor table (ADR-012).

### Implementation Notes

- **IMP-003**: `btsig_value_kind` selects the member width the codec reads and writes: `uint8`, `uint16`, `uint32`, `uint64`, `sint8`, `sint16`, `sint32`, `double`, or UTF-8.
- **IMP-004**: Sub-byte `uint1` and `uint2` fields are packed from bit 0 of the first octet. A UTF-8 field is the tail of the value.

### References

- **REF-003**: `tools/gss_ir/README.md` for the IR fields the emitter stores in the descriptor.
- **REF-004**: ADR-014 for generation and overrides.

## ADR-014: SIG YAML, IR, then C

**Accepted** | Proposed | Rejected | Superseded | Deprecated

**Date**: 2026-10-26

**Supersedes**: ADR-006, ADR-009

### Context

Assigned numbers and GATT Specification Supplement YAML are the source for characteristic layout. The codec must not parse YAML when it decodes a value.

### Decision

`tools/gss_ir/sources/` is the only reader of the `bluetooth_sig` submodule. The normaliser writes canonical IR at schema version 1. `python -m tools.gss_ir.generate` writes that IR for every characteristic that is not listed in `tools/gss_ir/characteristics.json`. That file is the blacklist. A characteristic the normaliser cannot express is recorded in `generated/errors.json`, and generation continues (`tools/gss_ir/generate.py`).

`python -m tools.gss_ir.emit_cpp` reads the IR only and writes `btsig/generated/<name>/`. CMake builds `btsig_characteristics` from those sources. A directory of the same name under `btsig/override/` replaces the generated codec (`btsig/modules/CMakeLists.txt`). The configure step stops when `btsig/generated/` has no characteristic sources.

### Consequences

#### Positive

- **POS-007**: Specification YAML stays in the submodule. The codec sees C tables.
- **POS-008**: The blacklist is an explicit list of identifiers. An empty list attempts every characteristic.
- **POS-009**: A characteristic that cannot be normalised does not stop generation of the others. The error file names it.

#### Negative

- **NEG-006**: Full characteristic coverage is unfinished while `generated/errors.json` lists characteristics and while identifiers remain on the blacklist without an override.
- **NEG-007**: An override for a characteristic that also has GSS YAML is reported when generation runs (`tools/gss_ir/sources/overrides.py`). The override still replaces the generated codec.

### Alternatives Considered

#### Interpret YAML in the codec

- **ALT-009**: **Description**: Load GSS YAML on first use and interpret it at decode time.
- **ALT-010**: **Rejection Reason**: The running codec is C and reads a descriptor compiled into the library.

#### Generate C++ classes from the IR

- **ALT-011**: **Description**: Emit a class per characteristic with a C++ value type.
- **ALT-012**: **Rejection Reason**: The emitter writes a C struct, a C descriptor, and C functions (ADR-012, ADR-013).

### Implementation Notes

- **IMP-005**: Regenerate with `python -m tools.gss_ir.generate tools/gss_ir/characteristics.json` and `python -m tools.gss_ir.emit_cpp tools/gss_ir/characteristics.json`.
- **IMP-006**: Generated sources are formatted with `clang-format-18` and `btsig/.clang-format`.
- **IMP-007**: IR schema version stays 1 until this development line is released. The emitter rejects any other version.

### References

- **REF-005**: `tools/gss_ir/README.md` for the IR contract.
- **REF-006**: ADR-015 for the coverage goal.

## ADR-015: Characteristic coverage is the library boundary

**Accepted** | Proposed | Rejected | Superseded | Deprecated

**Date**: 2026-10-26

**Supersedes**: ADR-005, ADR-008

### Context

The repository used to expose characteristics, services, and advertising through a Python API. The codec work is the library that replaces that centre.

### Decision

The library is the C characteristic codec. Its goal is a decode and encode path for every SIG characteristic, either generated from IR or supplied as an override.

A Python API, service definitions, profiles, and an advertising serialiser are deferred. They are not part of this library. The former Python package remains in `archived/python-lib/`.

The codec accepts bytes and returns a filled struct. It does not open a BLE connection.

### Consequences

#### Positive

- **POS-010**: Work on the library is characteristic coverage: shrink the blacklist and `generated/errors.json` until every characteristic has a codec.
- **POS-011**: The public surface is the generated and override C APIs plus `btsig_codec_decode` and `btsig_codec_encode`.

#### Negative

- **NEG-008**: Callers that need services, profiles, advertising, or Python wrap this library themselves, or wait until a later library exists.
- **NEG-009**: Documentation outside this page still describes the archived Python package. Those pages are not the codec contract.

### Alternatives Considered

#### Grow the C core to services, profiles, and advertising now

- **ALT-013**: **Description**: Add those serialisers beside the characteristic codec before characteristic coverage is complete.
- **ALT-014**: **Rejection Reason**: Characteristic coverage is the goal of this library. Those serialisers are deferred.

#### Make the Python package the supported API now

- **ALT-015**: **Description**: Restore `bluetooth_sig` as the interface and keep the C codec internal.
- **ALT-016**: **Rejection Reason**: The supported library is the C codec. A Python API is deferred.

### Implementation Notes

- **IMP-012**: Coverage is complete for a characteristic when `btsig_characteristics` contains its generated codec or an override of the same directory name.
- **IMP-013**: `generated/errors.json` and `tools/gss_ir/characteristics.json` are the lists of characteristics still outside that set.

### References

- **REF-007**: ADR-012, ADR-013, and ADR-014 for the codec those characteristics use.
- **REF-008**: `archived/python-lib/` for the former Python package.

## Superseded records

ADR-001 to ADR-011 are **Superseded** by ADR-012. They described the Python runtime and are not the codec contract.

| Record | Subject | Continued by |
| --- | --- | --- |
| ADR-001 | Registry discovery of Python characteristic classes | ADR-014 |
| ADR-002 | Double-checked locking for that registry | ADR-012 |
| ADR-003 | Python template composition | ADR-013 |
| ADR-004 | Declarative validation on Python characteristic classes | ADR-013 |
| ADR-005 | No BLE stack inside the Python package | ADR-015 |
| ADR-006 | `bluetooth_sig` git submodule as the specification source | ADR-014 |
| ADR-007 | `msgspec` structs for parse results | ADR-012 |
| ADR-008 | Four progressive Python API levels | ADR-015 |
| ADR-009 | Lazy YAML load in the Python process | ADR-014 |
| ADR-010 | Singleton translator and registries | ADR-012 |
| ADR-011 | Lazy Python module exports | ADR-015 |

"""Emit C characteristic sources from IR.

Generated decode and encode functions call ``btsig_codec_decode`` and ``btsig_codec_encode``.
Those handwritten functions own the shared formula
``raw * coefficient * 10^decimal_exponent * 2^binary_exponent``
(GSS ``M``, ``d``, and ``b``). This module stores the three integers in the
descriptor and does not evaluate them.

The handwritten headers this output includes, which this task does not create:

- ``btsig/types/status.h``: ``btsig_bytes``, ``btsig_error``, ``btsig_context``, ``btsig_status``.
- ``btsig/schema/descriptor.h``: ``BTSIG_SCHEMA_VERSION``, wire and sentinel enumerators,
  ``btsig_sentinel``, ``btsig_field_descriptor``, and ``btsig_characteristic_descriptor``.
- ``btsig/codec/codec.h``: ``btsig_codec_decode`` and ``btsig_codec_encode``. The scalar ``M``, ``d``, ``b``
  transform stays in the codec.

``btsig_value_kind`` enumerators used here are ``BTSIG_VALUE_UINT8``, ``BTSIG_VALUE_UINT16``,
``BTSIG_VALUE_UINT32``, ``BTSIG_VALUE_UINT64``, ``BTSIG_VALUE_SINT8``, ``BTSIG_VALUE_SINT16``,
``BTSIG_VALUE_SINT32``, ``BTSIG_VALUE_DOUBLE``, and ``BTSIG_VALUE_UTF8``. A ``double`` member is
the scaled quantity. An integer member is the raw value. A UTF-8 member is one counted value,
``uint16_t size`` followed by ``uint8_t data[capacity]``. The codec chooses which one from the value kind.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from tools.gss_ir.normalise.utf8 import ATT_MAX_VALUE_OCTETS
from tools.gss_ir.v1 import (
    IR_VERSION,
    Enumerator,
    IrContractError,
    IrDocument,
    ScalarField,
    Sentinel,
    UnitRef,
    ValueSet,
    WireType,
    decode_ir,
)

_INTEGER_LAYOUT: dict[WireType, tuple[str, int, int, str]] = {
    WireType.UINT8: ("uint8_t", 1, 1, "BTSIG_VALUE_UINT8"),
    WireType.UINT16: ("uint16_t", 2, 2, "BTSIG_VALUE_UINT16"),
    WireType.UINT24: ("uint32_t", 4, 4, "BTSIG_VALUE_UINT32"),
    WireType.UINT32: ("uint32_t", 4, 4, "BTSIG_VALUE_UINT32"),
    WireType.UINT48: ("uint64_t", 8, 8, "BTSIG_VALUE_UINT64"),
    WireType.UINT64: ("uint64_t", 8, 8, "BTSIG_VALUE_UINT64"),
    WireType.SINT8: ("int8_t", 1, 1, "BTSIG_VALUE_SINT8"),
    WireType.SINT16: ("int16_t", 2, 2, "BTSIG_VALUE_SINT16"),
    WireType.SINT24: ("int32_t", 4, 4, "BTSIG_VALUE_SINT32"),
    WireType.SINT32: ("int32_t", 4, 4, "BTSIG_VALUE_SINT32"),
    WireType.BOOLEAN8: ("uint8_t", 1, 1, "BTSIG_VALUE_UINT8"),
    WireType.BOOLEAN16: ("uint16_t", 2, 2, "BTSIG_VALUE_UINT16"),
    WireType.BOOLEAN24: ("uint32_t", 4, 4, "BTSIG_VALUE_UINT32"),
    WireType.BOOLEAN32: ("uint32_t", 4, 4, "BTSIG_VALUE_UINT32"),
    WireType.UINT1: ("uint8_t", 1, 1, "BTSIG_VALUE_UINT8"),
    WireType.UINT2: ("uint8_t", 1, 1, "BTSIG_VALUE_UINT8"),
}
_REAL_WIRE = frozenset({WireType.MEDFLOAT16, WireType.MEDFLOAT32, WireType.FLOAT32})
_SCALED_LAYOUT = ("double", 8, 8, "BTSIG_VALUE_DOUBLE")
_INT32_MIN = -(2**31)
_INT32_MAX = 2**31 - 1
_UINT32_MAX = 2**32 - 1
_UNSIGNED_INT_BITS = 32


class EmitError(RuntimeError):
    """IR could not be emitted."""

    def __init__(self, detail: str) -> None:
        """Initialise the error with a diagnostic detail."""
        super().__init__(detail)
        self.detail = detail


@dataclass(frozen=True, kw_only=True)
class _Member:
    name: str
    c_type: str
    size: int
    align: int
    value_kind: str
    offset: int
    wire: WireType
    coefficient: int
    decimal_exponent: int
    binary_exponent: int
    minimum: int
    maximum: int
    unit: UnitRef | None
    sentinels: tuple[Sentinel, ...]
    utf8_capacity: int = 0
    cpp_type: str = ""
    c_enum_type: str = ""
    c_enum_is_typedef: bool = False
    enumerators: tuple[Enumerator, ...] = ()
    value_set: ValueSet | None = None


@dataclass(frozen=True, kw_only=True)
class _Characteristic:
    name: str
    pascal_name: str
    identifier: str
    uuid: int
    c_struct: str
    size: int
    unit: str | None
    members: tuple[_Member, ...]


def _format_sources(paths: list[Path], style_file: Path) -> None:
    """Format generated sources with the btsig clang-format configuration.

    Raises:
        EmitError: If ``clang-format-18`` is missing or exits with an error.
    """
    formatter = shutil.which("clang-format-18")
    if formatter is None:
        raise EmitError("clang-format-18 is required to format generated sources")
    if not style_file.is_file():
        raise EmitError(f"clang-format style is missing: {style_file}")
    try:
        subprocess.run(
            [formatter, f"--style=file:{style_file}", "-i", *[str(path) for path in paths]],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = str(error)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            detail = error.stderr.strip()
        raise EmitError(f"clang-format failed: {detail}") from error


def repository_root() -> Path:
    """Return the repository root that contains this file.

    Returns:
        Absolute repository path.
    """
    return Path(__file__).resolve().parents[2]


def _load_blacklist(path: Path) -> frozenset[str]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EmitError(f"blacklist is not readable JSON: {error}") from error
    if not isinstance(loaded, list) or not all(isinstance(item, str) for item in loaded):
        raise EmitError("blacklist must be a JSON array of identifiers")
    return frozenset(loaded)


def _pascal(name: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in name.split("_") if part)


def _c_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _stored_utf8_bytes(capacity: int) -> int:
    raw = 2 + capacity
    return (raw + 1) // 2 * 2


def _c_member(member: _Member) -> str:
    if member.utf8_capacity:
        return (
            "    struct {\n"
            "        uint16_t size;\n"
            f"        uint8_t data[{member.utf8_capacity}];\n"
            f"    }} {member.name};"
        )
    return f"    {member.c_type} {member.name};"


def _snake_pascal(name: str) -> str:
    characters: list[str] = []
    for index, character in enumerate(name):
        if character.isupper() and index:
            characters.append("_")
        characters.append(character.lower())
    return "".join(characters)


def _enum_type(field_name: str, class_name: str) -> str:
    # The characteristic class already uses this PascalCase name.
    type_name = _pascal(field_name)
    if type_name == class_name:
        return f"{type_name}Value"
    return type_name


def _enumerator_expr(member: _Member, enumerator: Enumerator) -> str:
    if member.value_set is ValueSet.FLAGS:
        bit = enumerator.value.bit_length() - 1
        # `1U << 32` is undefined when unsigned int is 32 bits.
        if bit >= _UNSIGNED_INT_BITS:
            return f"1ULL << {bit}"
        return f"1U << {bit}"
    if enumerator.value >= 2**31:
        return f"{enumerator.value}U"
    return str(enumerator.value)


def _enum_storage(field: ScalarField) -> tuple[int, int, str]:
    """Member size, alignment, and codec value kind.

    A flags mask is unsigned so bit 31 stays a positive value. A closed code
    set stays signed when every code fits in int. The C enumeration is wider
    than the wire field. C11 gives an enum no underlying type, so the generated
    source asserts that sizeof the enum is 4. A mask that does not fit in int
    is a uint32_t or uint64_t typedef.
    """
    values = [item.value for item in field.enumerators]
    low = min(values)
    high = max(values)
    if field.value_set is ValueSet.FLAGS or low < _INT32_MIN or high > _INT32_MAX:
        if low < 0:
            raise EmitError(f"{field.name}: signed enumerators do not fit in int32")
        if high > _UINT32_MAX:
            return (8, 8, "BTSIG_VALUE_UINT64")
        return (4, 4, "BTSIG_VALUE_UINT32")
    return (4, 4, "BTSIG_VALUE_SINT32")


def _layout(document: IrDocument) -> _Characteristic:
    short = document.identifier.removeprefix("org.bluetooth.characteristic.")
    pascal_name = _pascal(short)
    offset = 0
    max_align = 1
    members: list[_Member] = []
    for field in document.fields:
        if field.wire_type is WireType.UTF8:
            # A characteristic that states no maximum still cannot exceed one attribute value.
            capacity = ATT_MAX_VALUE_OCTETS if field.utf8_capacity is None else field.utf8_capacity
            stored = _stored_utf8_bytes(capacity)
            offset = (offset + 1) // 2 * 2
            members.append(
                _Member(
                    name=field.name,
                    c_type="uint16_t",
                    size=stored,
                    align=2,
                    value_kind="BTSIG_VALUE_UTF8",
                    offset=offset,
                    wire=field.wire_type,
                    coefficient=1,
                    decimal_exponent=0,
                    binary_exponent=0,
                    minimum=0,
                    maximum=0,
                    unit=field.unit,
                    sentinels=field.sentinels,
                    utf8_capacity=capacity,
                    cpp_type="uint16_t",
                )
            )
            offset += stored
            max_align = max(max_align, 2)
            continue
        transform = field.transform
        scaled = field.wire_type in _REAL_WIRE or (
            transform is not None
            and not (transform.coefficient == 1 and transform.decimal_exponent == 0 and transform.binary_exponent == 0)
        )
        c_type, size, align, kind = _SCALED_LAYOUT if scaled else _INTEGER_LAYOUT[field.wire_type]
        cpp_type = c_type if field.value_set is None else _enum_type(field.name, pascal_name)
        c_enum_type = "" if field.value_set is None else f"btsig_{_snake_pascal(cpp_type)}"
        c_enum_is_typedef = False
        # The enumeration is wider than the wire field. Flags use an unsigned width.
        if field.value_set is not None:
            size, align, kind = _enum_storage(field)
            # ISO C restricts enumerator values to int. A wider mask is a typedef.
            c_enum_is_typedef = any(item.value > _INT32_MAX for item in field.enumerators)
        offset = (offset + align - 1) // align * align
        coefficient = 1 if transform is None else transform.coefficient
        decimal_exponent = 0 if transform is None else transform.decimal_exponent
        binary_exponent = 0 if transform is None else transform.binary_exponent
        members.append(
            _Member(
                name=field.name,
                c_type=c_type,
                size=size,
                align=align,
                value_kind=kind,
                offset=offset,
                wire=field.wire_type,
                coefficient=coefficient,
                decimal_exponent=decimal_exponent,
                binary_exponent=binary_exponent,
                minimum=field.minimum,
                maximum=field.maximum,
                unit=field.unit,
                sentinels=field.sentinels,
                utf8_capacity=0,
                cpp_type=cpp_type,
                c_enum_type=c_enum_type,
                c_enum_is_typedef=c_enum_is_typedef,
                enumerators=field.enumerators,
                value_set=field.value_set,
            )
        )
        offset += size
        max_align = max(max_align, align)
    total = (offset + max_align - 1) // max_align * max_align
    unit_ids = {member.unit.identifier if member.unit is not None else None for member in members}
    unit = unit_ids.pop() if len(unit_ids) == 1 else None
    return _Characteristic(
        name=short,
        pascal_name=pascal_name,
        identifier=document.identifier,
        uuid=document.uuid,
        c_struct=f"btsig_{short}",
        size=total,
        unit=unit,
        members=tuple(members),
    )


def _banner(command: str) -> str:
    return f"// Generated by `{command}`. Do not edit.\n"


def _guard(name: str, suffix: str) -> str:
    return f"BTSIG_{name.upper()}_{suffix}"


def _c_struct_member(member: _Member) -> str:
    if member.utf8_capacity:
        return _c_member(member)
    if member.c_enum_type:
        if member.c_enum_is_typedef:
            return f"    {member.c_enum_type} {member.name};"
        return f"    enum {member.c_enum_type} {member.name};"
    return f"    {member.c_type} {member.name};"


def _c_constant(member: _Member, enumerator: Enumerator) -> str:
    name = f"{member.c_enum_type.upper()}_{enumerator.name.upper()}"
    if member.c_enum_is_typedef:
        return f"static const {member.c_enum_type} {name} = {_enumerator_expr(member, enumerator)};"
    return f"    {name} = {_enumerator_expr(member, enumerator)},"


def _c_enumerations(item: _Characteristic) -> str:
    blocks: list[str] = []
    for member in item.members:
        if not member.c_enum_type:
            continue
        if member.c_enum_is_typedef:
            width = "uint64_t" if member.value_kind == "BTSIG_VALUE_UINT64" else "uint32_t"
            constants = "\n".join(_c_constant(member, enumerator) for enumerator in member.enumerators)
            blocks.append(f"typedef {width} {member.c_enum_type};\n{constants}\n")
            continue
        constants = "\n".join(_c_constant(member, enumerator) for enumerator in member.enumerators)
        blocks.append(f"enum {member.c_enum_type} {{\n{constants}\n}};\n")
    if not blocks:
        return ""
    return "\n".join(blocks) + "\n"


def _c_header(item: _Characteristic, command: str) -> str:
    decode = f"btsig_decode_{item.name}"
    encode = f"btsig_encode_{item.name}"
    guard = _guard(item.name, "H")
    members = "\n".join(_c_struct_member(member) for member in item.members)
    return (
        f"{_banner(command)}"
        f"#ifndef {guard}\n"
        f"#define {guard}\n\n"
        '#include "btsig/types/status.h"\n\n'
        "#include <stddef.h>\n"
        "#include <stdint.h>\n\n"
        f"{_c_enumerations(item)}"
        "#ifdef __cplusplus\n"
        'extern "C" {\n'
        "#endif\n\n"
        f"typedef struct {item.c_struct} {{\n"
        f"{members}\n"
        f"}} {item.c_struct};\n\n"
        f"btsig_error {decode}(\n"
        f"    btsig_bytes input, const btsig_context* context, {item.c_struct}* value);\n\n"
        f"btsig_error {encode}(\n"
        f"    const {item.c_struct}* value, uint8_t* out, size_t out_size, size_t* written);\n\n"
        "#ifdef __cplusplus\n"
        "}\n"
        "#endif\n\n"
        f"#endif // {guard}\n"
    )


@dataclass(frozen=True)
class _TableLayout:
    text_lines: tuple[str, ...]
    sentinel_lines: tuple[str, ...]
    allowed_lines: tuple[str, ...]
    name_offset: int
    id_offset: int
    unit_offset: int
    field_name_offsets: tuple[int, ...]
    field_unit_offsets: tuple[int, ...]
    sentinel_spans: tuple[tuple[int, int], ...]
    allowed_spans: tuple[tuple[int, int], ...]
    has_sentinels: bool
    has_allowed: bool


def _text_piece(value: str) -> str:
    return "    " + _c_string(value)[:-1] + '\\0"'


_NO_TEXT = 0xFFFF
_MAX_TEXT_OFFSET = 0xFFFE


def _offset_token(offset: int) -> str:
    return "BTSIG_NO_TEXT" if offset == _NO_TEXT else str(offset)


def _append_text(chunks: list[str], value: str | None) -> int:
    if value is None:
        return _NO_TEXT
    offset = sum(len(chunk) + 1 for chunk in chunks)
    if offset > _MAX_TEXT_OFFSET:
        raise EmitError(f"characteristic text exceeds {_MAX_TEXT_OFFSET} bytes")
    chunks.append(value)
    return offset


def _table_layout(item: _Characteristic) -> _TableLayout:
    chunks: list[str] = []
    name_offset = _append_text(chunks, item.name)
    id_offset = _append_text(chunks, item.identifier)
    unit_offset = _append_text(chunks, item.unit)
    field_name_offsets: list[int] = []
    field_unit_offsets: list[int] = []
    for member in item.members:
        field_name_offsets.append(_append_text(chunks, member.name))
        unit = None if member.unit is None else member.unit.identifier
        field_unit_offsets.append(_append_text(chunks, unit))
    text_lines = (
        f"static const char {item.name}_text[] =",
        *(_text_piece(chunk) for chunk in chunks),
        ";",
        "",
    )

    sentinel_entries: list[str] = []
    sentinel_spans: list[tuple[int, int]] = []
    for member in item.members:
        if member.sentinels:
            sentinel_spans.append((len(sentinel_entries), len(member.sentinels)))
            sentinel_entries.extend(
                f"    {{{sentinel.raw_value}, BTSIG_SENTINEL_{sentinel.meaning.value.upper()}}},"
                for sentinel in member.sentinels
            )
        else:
            sentinel_spans.append((0, 0))
    if sentinel_entries:
        sentinel_lines: tuple[str, ...] = (
            f"static const btsig_sentinel {item.name}_sentinels[] = {{",
            *sentinel_entries,
            "};",
            "",
        )
    else:
        sentinel_lines = ()

    allowed_entries: list[str] = []
    allowed_spans: list[tuple[int, int]] = []
    for member in item.members:
        if member.value_set is ValueSet.ENUMERATION:
            allowed_spans.append((len(allowed_entries), len(member.enumerators)))
            allowed_entries.extend(f"    {enumerator.value}," for enumerator in member.enumerators)
        else:
            allowed_spans.append((0, 0))
    if allowed_entries:
        allowed_lines: tuple[str, ...] = (
            f"static const int64_t {item.name}_allowed[] = {{",
            *allowed_entries,
            "};",
            "",
        )
    else:
        allowed_lines = ()

    return _TableLayout(
        text_lines=text_lines,
        sentinel_lines=sentinel_lines,
        allowed_lines=allowed_lines,
        name_offset=name_offset,
        id_offset=id_offset,
        unit_offset=unit_offset,
        field_name_offsets=tuple(field_name_offsets),
        field_unit_offsets=tuple(field_unit_offsets),
        sentinel_spans=tuple(sentinel_spans),
        allowed_spans=tuple(allowed_spans),
        has_sentinels=bool(sentinel_entries),
        has_allowed=bool(allowed_entries),
    )


def _field_lines(item: _Characteristic, layout: _TableLayout) -> list[str]:
    lines = [f"static const btsig_field_descriptor {item.name}_fields[] = {{"]
    for index, member in enumerate(item.members):
        unit_uuid = "0" if member.unit is None else f"0x{member.unit.uuid:04X}"
        sentinel_offset, sentinel_count = layout.sentinel_spans[index]
        if member.value_set is ValueSet.FLAGS:
            mask = 0
            for enumerator in member.enumerators:
                mask |= enumerator.value
            flag_mask = f"0x{mask:X}"
        else:
            flag_mask = "0"
        allowed_offset, allowed_count = layout.allowed_spans[index]
        lines.extend(
            [
                "    {",
                f"        {member.minimum},",
                f"        {member.maximum},",
                f"        {flag_mask},",
                f"        {_offset_token(layout.field_name_offsets[index])},",
                f"        {_offset_token(layout.field_unit_offsets[index])},",
                f"        offsetof({item.c_struct}, {member.name}),",
                f"        {sentinel_offset},",
                f"        {sentinel_count},",
                f"        {allowed_offset},",
                f"        {allowed_count},",
                f"        {member.utf8_capacity},",
                f"        {unit_uuid},",
                f"        {member.value_kind},",
                f"        BTSIG_WIRE_{member.wire.value.upper()},",
                f"        {member.coefficient},",
                f"        {member.decimal_exponent},",
                f"        {member.binary_exponent},",
                "    },",
            ]
        )
    lines.append("};")
    lines.append("")
    return lines


def _descriptor_lines(item: _Characteristic, layout: _TableLayout) -> list[str]:
    flags_only = bool(item.members) and all(member.value_set is ValueSet.FLAGS for member in item.members)
    bitfield = "1" if flags_only else "0"
    sentinels = f"{item.name}_sentinels" if layout.has_sentinels else "NULL"
    allowed = f"{item.name}_allowed" if layout.has_allowed else "NULL"
    unit_offset = _offset_token(layout.unit_offset)
    return [
        f"static const btsig_characteristic_descriptor {item.name}_descriptor = {{",
        f"    {item.name}_text,",
        f"    {sentinels},",
        f"    {allowed},",
        f"    {item.name}_fields,",
        f"    {layout.name_offset},",
        f"    {layout.id_offset},",
        f"    {unit_offset},",
        f"    0x{item.uuid:04X},",
        f"    sizeof({item.c_struct}),",
        f"    {len(item.members)},",
        f"    {bitfield},",
        "};",
        "",
    ]


def _assert_lines(item: _Characteristic) -> list[str]:
    lines = [
        f'_Static_assert(BTSIG_SCHEMA_VERSION == {IR_VERSION}, "schema version");',
        f'_Static_assert(sizeof({item.c_struct}) == {item.size}, "characteristic size");',
    ]
    for member in item.members:
        lines.append(f'_Static_assert(offsetof({item.c_struct}, {member.name}) == {member.offset}, "member offset");')
        if member.c_enum_type:
            stored = member.c_enum_type if member.c_enum_is_typedef else f"enum {member.c_enum_type}"
            lines.append(f'_Static_assert(sizeof({stored}) == {member.size}, "enumeration width");')
    return lines


def _wrapper_lines(item: _Characteristic) -> list[str]:
    struct_name = item.c_struct
    decode = f"btsig_decode_{item.name}"
    encode = f"btsig_encode_{item.name}"
    return [
        f"btsig_error {decode}(",
        "    btsig_bytes input,",
        "    const btsig_context* context,",
        f"    {struct_name}* value) {{",
        "    if (value == NULL) {",
        "        btsig_error invalid = {0};",
        "        invalid.status = BTSIG_INVALID_ARGUMENT;",
        "        invalid.bytes = input;",
        "        return invalid;",
        "    }",
        f"    return btsig_codec_decode(&{item.name}_descriptor, input, context, value, sizeof(*value));",
        "}",
        "",
        f"btsig_error {encode}(",
        f"    const {struct_name}* value,",
        "    uint8_t* out,",
        "    size_t out_size,",
        "    size_t* written) {",
        "    btsig_bytes empty = {0};",
        "    if (value == NULL || written == NULL || (out == NULL && out_size != 0)) {",
        "        btsig_error invalid = {0};",
        "        invalid.status = BTSIG_INVALID_ARGUMENT;",
        "        invalid.bytes = empty;",
        "        return invalid;",
        "    }",
        f"    return btsig_codec_encode(&{item.name}_descriptor, value, sizeof(*value), out, out_size, written);",
        "}",
        "",
    ]


def _translation_unit(item: _Characteristic, command: str) -> str:
    body = [
        _banner(command).rstrip("\n"),
        "",
        f'#include "btsig/{item.name}.h"',
        "",
        '#include "btsig/codec/codec.h"',
        "",
        "#include <stddef.h>",
        "",
    ]
    layout = _table_layout(item)
    body.extend(layout.text_lines)
    body.extend(layout.sentinel_lines)
    body.extend(layout.allowed_lines)
    body.extend(_field_lines(item, layout))
    body.extend(_descriptor_lines(item, layout))
    body.extend(_wrapper_lines(item))
    body.extend(_assert_lines(item))
    body.append("")
    return "\n".join(body)


def _read_documents(destination: Path, blocked: frozenset[str]) -> tuple[IrDocument, ...]:
    directory = destination / f"generated/ir/{IR_VERSION}"
    documents: list[IrDocument] = []
    for path in sorted(directory.glob("*.json")):
        if path.stem in blocked:
            continue
        try:
            data = path.read_bytes()
        except OSError as error:
            raise EmitError(f"missing IR for {path.stem}: {error}") from error
        try:
            document = decode_ir(data, require_canonical=True)
        except IrContractError as error:
            raise EmitError(f"IR for {path.stem} is not canonical schema version {IR_VERSION}: {error}") from error
        if document.identifier in blocked:
            continue
        documents.append(document)
    if not documents:
        raise EmitError("no generated IR to emit")
    versions = {document.schema_version for document in documents}
    if versions != {IR_VERSION}:
        raise EmitError("IR schema version does not match this emitter")
    return tuple(documents)


def emit_characteristics(
    characteristics_path: Path,
    *,
    root: Path | None = None,
    output_root: Path | None = None,
) -> dict[str, bytes]:
    """Emit one C characteristic API per generated IR document.

    Args:
        characteristics_path: JSON array of characteristic identifiers to skip.
        root: Repository root used to form the generator command.
        output_root: Directory that contains ``generated/ir`` and receives ``btsig/generated``.

    Returns:
        Output path relative to ``output_root`` mapped to file bytes.
        Each source is formatted with ``clang-format-18`` and ``btsig/.clang-format``.

    Raises:
        EmitError: If IR is missing, two characteristics share a UUID, or formatting fails.
    """
    repo = repository_root() if root is None else root
    destination = repo if output_root is None else output_root
    documents = _read_documents(destination, _load_blacklist(characteristics_path))
    layouts = tuple(_layout(document) for document in documents)
    seen: set[int] = set()
    for item in layouts:
        if item.uuid in seen:
            raise EmitError(f"duplicate UUID 0x{item.uuid:04X}")
        seen.add(item.uuid)
    relative_list = characteristics_path.resolve().relative_to(repo.resolve()).as_posix()
    command = f"python -m tools.gss_ir.emit_cpp {relative_list}"
    files: dict[str, str] = {}
    for item in layouts:
        root_dir = f"btsig/generated/{item.name}"
        files[f"{root_dir}/include/btsig/{item.name}.h"] = _c_header(item, command)
        files[f"{root_dir}/src/{item.name}.c"] = _translation_unit(item, command)
    encoded = {path: text.encode("utf-8") for path, text in files.items()}
    written: list[Path] = []
    for relative, payload in encoded.items():
        output = destination / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
        written.append(output)
    for item in layouts:
        generated = destination / "btsig" / "generated" / item.name
        for stale in (
            generated / "include" / "btsig" / f"{item.name}.hpp",
            generated / "src" / f"{item.name}.cpp",
        ):
            stale.unlink(missing_ok=True)
    _format_sources(written, repo / "btsig" / ".clang-format")
    return {relative: path.read_bytes() for relative, path in zip(encoded, written, strict=True)}


def main(argv: list[str] | None = None) -> int:
    """Emit every generated characteristic outside the blacklist.

    Args:
        argv: Command arguments, excluding the program name.

    Returns:
        Process status, ``0`` on success and ``1`` on an emit error.
    """
    parser = argparse.ArgumentParser(
        description="Emit C sources for every generated characteristic outside the blacklist."
    )
    parser.add_argument("characteristics", type=Path, help="JSON array of identifiers to skip")
    args = parser.parse_args(argv)
    try:
        emit_characteristics(args.characteristics)
    except EmitError as error:
        print(error.detail)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

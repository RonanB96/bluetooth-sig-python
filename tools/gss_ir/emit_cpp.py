"""Emit C and C++ characteristic headers from IR.

Generated decode and encode functions call ``btsig::decode`` and ``btsig::encode``.
Those handwritten functions own the shared formula
``raw * coefficient * 10^decimal_exponent * 2^binary_exponent``
(GSS ``M``, ``d``, and ``b``). This module stores the three integers in the
descriptor and does not evaluate them.

The handwritten headers this output includes, which this task does not create:

- ``btsig/types/status.h``: ``btsig_bytes``, ``btsig_error``, ``btsig_context``, ``btsig_status``.
- ``btsig/types/expected.hpp``: ``btsig::expected<T>`` and ``btsig::unexpected<T>``.
  ``expected`` is true on success, ``value()`` returns ``T``, and ``error()`` returns ``btsig_error``.
- ``btsig/types/span.hpp``: ``btsig::span<T>`` with ``data()`` and ``size()``.
- ``btsig/schema/descriptor.hpp``: ``kSchemaVersion``, ``wire_type``, ``sentinel_meaning``,
  ``Sentinel``, ``FieldDescriptor``, and ``CharacteristicDescriptor``.
- ``btsig/wire/word.hpp``: little-endian words, IEEE 11073 medfloat, and IEEE-754 binary32.
- ``btsig/codec/codec.hpp``: ``btsig::decode`` and ``btsig::encode``. The scalar ``M``, ``d``, ``b``
  transform stays in the codec.

``btsig_value_kind`` enumerators used here are ``BTSIG_VALUE_UINT8``, ``BTSIG_VALUE_UINT16``,
``BTSIG_VALUE_UINT32``, ``BTSIG_VALUE_UINT64``, ``BTSIG_VALUE_SINT8``, ``BTSIG_VALUE_SINT16``,
``BTSIG_VALUE_SINT32``, ``BTSIG_VALUE_DOUBLE``, and ``BTSIG_VALUE_UTF8``. A ``double`` member is
the scaled quantity. An integer member is the raw value. A UTF-8 member is ``uint16_t name_length``
followed by ``uint8_t name[capacity]``. The codec chooses which one from the value kind.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from tools.gss_ir.v1 import (
    IR_VERSION,
    Enumerator,
    IrContractError,
    IrDocument,
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
# Unsized ``utf8s`` names no octet maximum. The array bound matches
# ``Utf8StringTemplate`` in src/bluetooth_sig/gatt/characteristics/templates/string.py.
_VARIABLE_UTF8_OCTETS = 256


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


def _c_member(member: _Member) -> str:
    if member.utf8_capacity:
        return f"    uint16_t {member.name}_length;\n    uint8_t {member.name}[{member.utf8_capacity}];"
    return f"    {member.c_type} {member.name};"


def _cpp_member(member: _Member) -> str:
    if member.utf8_capacity:
        return _c_member(member)
    return f"    {member.cpp_type} {member.name};"


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
        return f"1U << {enumerator.value.bit_length() - 1}"
    if enumerator.value >= 2**31:
        return f"{enumerator.value}U"
    return str(enumerator.value)


def _layout(document: IrDocument) -> _Characteristic:
    short = document.identifier.removeprefix("org.bluetooth.characteristic.")
    pascal_name = _pascal(short)
    offset = 0
    max_align = 1
    members: list[_Member] = []
    for field in document.fields:
        if field.wire_type is WireType.UTF8:
            capacity = _VARIABLE_UTF8_OCTETS if field.utf8_capacity is None else field.utf8_capacity
            offset = (offset + 1) // 2 * 2
            members.append(
                _Member(
                    name=field.name,
                    c_type="uint16_t",
                    size=2 + capacity,
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
            offset += 2 + capacity
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
        # A C enum is an int, so the member is wider than the wire field.
        if field.value_set is not None:
            size, align, kind = (4, 4, "BTSIG_VALUE_SINT32")
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
        return f"    enum {member.c_enum_type} {member.name};"
    return f"    {member.c_type} {member.name};"


def _c_enumerations(item: _Characteristic) -> str:
    blocks: list[str] = []
    for member in item.members:
        if not member.c_enum_type:
            continue
        constants = [
            f"    {member.c_enum_type.upper()}_{enumerator.name.upper()} = {_enumerator_expr(member, enumerator)},"
            for enumerator in member.enumerators
        ]
        body = "\n".join(constants)
        blocks.append(f"enum {member.c_enum_type} {{\n{body}\n}};\n")
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


def _enum_blocks(item: _Characteristic) -> str:
    blocks: list[str] = []
    for member in item.members:
        if member.value_set is None:
            continue
        lines = [f"enum class {member.cpp_type} : int {{"]
        for enumerator in member.enumerators:
            lines.append(f"    {enumerator.name} = {_enumerator_expr(member, enumerator)},")
        lines.extend(["};", ""])
        blocks.append("\n".join(lines))
    return "".join(blocks)


def _hpp(item: _Characteristic, command: str) -> str:
    guard = _guard(item.name, "HPP")
    return (
        f"{_banner(command)}"
        f"#ifndef {guard}\n"
        f"#define {guard}\n\n"
        f'#include "btsig/{item.name}.h"\n'
        '#include "btsig/types/expected.hpp"\n'
        '#include "btsig/types/span.hpp"\n\n'
        "#include <cstddef>\n"
        "#include <cstdint>\n\n"
        "namespace btsig {\n\n"
        f"{_enum_blocks(item)}"
        f"class {item.pascal_name} {{\n"
        "public:\n" + "".join(f"{_cpp_member(member)}\n" for member in item.members) + "\n"
        f"    [[nodiscard]] static btsig::expected<{item.pascal_name}> decode(\n"
        "        btsig_bytes input, const btsig_context* context);\n\n"
        f"    [[nodiscard]] static btsig::expected<std::size_t> encode(\n"
        f"        const {item.pascal_name}& value, btsig::span<std::uint8_t> out);\n"
        "};\n\n"
        "} // namespace btsig\n\n"
        f"#endif // {guard}\n"
    )


def _sentinel_lines(item: _Characteristic) -> list[str]:
    lines: list[str] = []
    for member in item.members:
        if not member.sentinels:
            continue
        lines.append(f"constexpr btsig::Sentinel {item.name}_{member.name}_sentinels[] = {{")
        for sentinel in member.sentinels:
            lines.append(f"    {{{sentinel.raw_value}, btsig::sentinel_meaning::{sentinel.meaning.value}}},")
        lines.append("};")
        lines.append("")
    return lines


def _allowed_lines(item: _Characteristic) -> list[str]:
    lines: list[str] = []
    for member in item.members:
        if member.value_set is not ValueSet.ENUMERATION:
            continue
        lines.append(f"constexpr std::int64_t {item.name}_{member.name}_allowed[] = {{")
        lines.extend(f"    {enumerator.value}," for enumerator in member.enumerators)
        lines.extend(["};", ""])
    return lines


def _field_lines(item: _Characteristic) -> list[str]:
    lines = [f"constexpr btsig::FieldDescriptor {item.name}_fields[] = {{"]
    for member in item.members:
        unit = "nullptr" if member.unit is None else _c_string(member.unit.identifier)
        unit_uuid = "0" if member.unit is None else f"0x{member.unit.uuid:04X}"
        if member.sentinels:
            sentinels = f"{item.name}_{member.name}_sentinels"
            count = str(len(member.sentinels))
        else:
            sentinels = "nullptr"
            count = "0"
        if member.value_set is ValueSet.ENUMERATION:
            allowed = f"{item.name}_{member.name}_allowed"
            allowed_count = str(len(member.enumerators))
            flag_mask = "0"
        elif member.value_set is ValueSet.FLAGS:
            allowed = "nullptr"
            allowed_count = "0"
            mask = 0
            for enumerator in member.enumerators:
                mask |= enumerator.value
            flag_mask = f"0x{mask:X}"
        else:
            allowed = "nullptr"
            allowed_count = "0"
            flag_mask = "0"
        lines.extend(
            [
                "    {",
                f"        {_c_string(member.name)},",
                f"        {unit},",
                f"        offsetof({item.c_struct}, {member.name}),",
                f"        {member.minimum},",
                f"        {member.maximum},",
                f"        {sentinels},",
                f"        {count},",
                f"        {member.value_kind},",
                f"        {unit_uuid},",
                f"        btsig::wire_type::{member.wire.value},",
                f"        {member.coefficient},",
                f"        {member.decimal_exponent},",
                f"        {member.binary_exponent},",
                f"        {member.utf8_capacity},",
                f"        {allowed},",
                f"        {allowed_count},",
                f"        {flag_mask},",
                "    },",
            ]
        )
    lines.append("};")
    lines.append("")
    return lines


def _descriptor_lines(item: _Characteristic) -> list[str]:
    unit = "nullptr" if item.unit is None else _c_string(item.unit)
    flags_only = bool(item.members) and all(member.value_set is ValueSet.FLAGS for member in item.members)
    bitfield = "true" if flags_only else "false"
    return [
        f"constexpr btsig::CharacteristicDescriptor {item.name}_descriptor{{",
        f"    {_c_string(item.name)},",
        f"    {_c_string(item.identifier)},",
        f"    0x{item.uuid:04X},",
        f"    {unit},",
        f"    {bitfield},",
        f"    sizeof({item.c_struct}),",
        f"    {item.name}_fields,",
        f"    {len(item.members)},",
        "};",
        "",
    ]


def _assert_lines(item: _Characteristic) -> list[str]:
    qualified = f"btsig::{item.pascal_name}"
    lines = [
        f"static_assert(std::is_standard_layout_v<{qualified}>);",
        f"static_assert(std::is_trivially_copyable_v<{qualified}>);",
        f"static_assert(sizeof({item.c_struct}) == {item.size});",
        f"static_assert(sizeof({qualified}) ==",
        f"              sizeof({item.c_struct}));",
    ]
    for member in item.members:
        length_name = f"{member.name}_length" if member.utf8_capacity else member.name
        lines.append(f"static_assert(offsetof({item.c_struct}, {length_name}) == {member.offset});")
        lines.append(f"static_assert(offsetof({qualified}, {length_name}) == {member.offset});")
        if member.utf8_capacity:
            lines.append(f"static_assert(offsetof({item.c_struct}, {member.name}) == {member.offset + 2});")
            lines.append(f"static_assert(offsetof({qualified}, {member.name}) == {member.offset + 2});")
        elif member.c_enum_type:
            lines.append(f"static_assert(sizeof({member.c_enum_type}) == sizeof(int));")
            lines.append(f"static_assert(sizeof(btsig::{member.cpp_type}) == sizeof(int));")
    return lines


def _method_lines(item: _Characteristic) -> list[str]:
    pascal = item.pascal_name
    descriptor = f"{item.name}_descriptor"
    return [
        f"btsig::expected<{pascal}>",
        f"{pascal}::decode(btsig_bytes input, const btsig_context* context) {{",
        f"    {pascal} value{{}};",
        "    const btsig_error error =",
        f"        btsig::decode({descriptor}, input, context, &value, sizeof value);",
        "    if (error.status != BTSIG_OK) {",
        f"        return btsig::unexpected<{pascal}>(error);",
        "    }",
        f"    return btsig::expected<{pascal}>(value);",
        "}",
        "",
        f"btsig::expected<std::size_t> {pascal}::encode(",
        f"    const {pascal}& value, btsig::span<std::uint8_t> out) {{",
        "    std::size_t written = 0;",
        "    const btsig_error error = btsig::encode(",
        f"        {descriptor},",
        "        &value,",
        "        sizeof value,",
        "        out.data(),",
        "        out.size(),",
        "        &written);",
        "    if (error.status != BTSIG_OK) {",
        "        return btsig::unexpected<std::size_t>(error);",
        "    }",
        "    return btsig::expected<std::size_t>(written);",
        "}",
        "",
    ]


def _wrapper_lines(item: _Characteristic) -> list[str]:
    struct_name = item.c_struct
    pascal = f"btsig::{item.pascal_name}"
    decode = f"btsig_decode_{item.name}"
    encode = f"btsig_encode_{item.name}"
    return [
        f'extern "C" btsig_error {decode}(',
        "    btsig_bytes input,",
        "    const btsig_context* context,",
        f"    {struct_name}* value) {{",
        "    if (value == nullptr) {",
        "        btsig_error invalid{};",
        "        invalid.status = BTSIG_INVALID_ARGUMENT;",
        "        invalid.bytes = input;",
        "        return invalid;",
        "    }",
        f"    const btsig::expected<{pascal}> decoded =",
        f"        {pascal}::decode(input, context);",
        "    if (!decoded) {",
        "        return decoded.error();",
        "    }",
        f"    const {pascal} decoded_value = decoded.value();",
        "    std::memcpy(value, &decoded_value, sizeof(*value));",
        "    btsig_error ok{};",
        "    ok.status = BTSIG_OK;",
        "    ok.bytes = input;",
        "    return ok;",
        "}",
        "",
        f'extern "C" btsig_error {encode}(',
        f"    const {struct_name}* value,",
        "    uint8_t* out,",
        "    size_t out_size,",
        "    size_t* written) {",
        "    btsig_bytes empty{nullptr, 0};",
        "    if (value == nullptr || written == nullptr || (out == nullptr && out_size != 0)) {",
        "        btsig_error invalid{};",
        "        invalid.status = BTSIG_INVALID_ARGUMENT;",
        "        invalid.bytes = empty;",
        "        return invalid;",
        "    }",
        f"    {pascal} typed{{}};",
        "    std::memcpy(&typed, value, sizeof typed);",
        "    const btsig::expected<std::size_t> encoded =",
        f"        {pascal}::encode(typed, btsig::span<std::uint8_t>(out, out_size));",
        "    if (!encoded) {",
        "        return encoded.error();",
        "    }",
        "    *written = encoded.value();",
        "    btsig_error ok{};",
        "    ok.status = BTSIG_OK;",
        "    return ok;",
        "}",
        "",
    ]


def _translation_unit(item: _Characteristic, command: str) -> str:
    includes = [
        f'#include "btsig/{item.name}.hpp"',
        '#include "btsig/codec/codec.hpp"',
        '#include "btsig/schema/descriptor.hpp"',
    ]
    body = [
        _banner(command).rstrip("\n"),
        "",
        *includes,
        "",
        "#include <cstddef>",
        "#include <cstdint>",
        "#include <cstring>",
        "#include <type_traits>",
        "",
        "namespace {",
        "",
    ]
    body.extend(_sentinel_lines(item))
    body.extend(_allowed_lines(item))
    body.extend(_field_lines(item))
    body.extend(_descriptor_lines(item))
    body.extend(
        [
            "} // namespace",
            "",
            "namespace btsig {",
            "",
        ]
    )
    body.extend(_method_lines(item))
    body.extend(["} // namespace btsig", ""])
    body.extend(_wrapper_lines(item))
    body.append(f"static_assert(btsig::kSchemaVersion == {IR_VERSION});")
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
    """Emit one C and C++ characteristic API per generated IR document.

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
        files[f"{root_dir}/include/btsig/{item.name}.hpp"] = _hpp(item, command)
        files[f"{root_dir}/src/{item.name}.cpp"] = _translation_unit(item, command)
    encoded = {path: text.encode("utf-8") for path, text in files.items()}
    written: list[Path] = []
    for relative, payload in encoded.items():
        output = destination / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
        written.append(output)
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
        description="Emit C and C++ sources for every generated characteristic outside the blacklist."
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

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
- ``btsig/codec/codec.hpp``: ``btsig::decode`` and ``btsig::encode``.

``btsig_value_kind`` enumerators used here are ``BTSIG_VALUE_UINT8``, ``BTSIG_VALUE_UINT16``,
``BTSIG_VALUE_UINT32``, ``BTSIG_VALUE_UINT64``, ``BTSIG_VALUE_SINT8``, ``BTSIG_VALUE_SINT16``,
``BTSIG_VALUE_SINT32``, and ``BTSIG_VALUE_DOUBLE``. A ``double`` member is the scaled quantity.
An integer member is the raw value. The codec chooses which one from the value kind.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from tools.gss_ir.v1 import IR_VERSION, IrContractError, IrDocument, Sentinel, UnitRef, WireType, decode_ir

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
}
_SCALED_LAYOUT = ("double", 8, 8, "BTSIG_VALUE_DOUBLE")


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


def repository_root() -> Path:
    """Return the repository root that contains this file.

    Returns:
        Absolute repository path.
    """
    return Path(__file__).resolve().parents[2]


def _load_characteristics(path: Path) -> tuple[str, ...]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EmitError(f"characteristic list is not readable JSON: {error}") from error
    if not isinstance(loaded, list) or not loaded or not all(isinstance(item, str) for item in loaded):
        raise EmitError("characteristic list must be a non-empty JSON array of identifiers")
    return tuple(loaded)


def _pascal(name: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in name.split("_") if part)


def _c_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _layout(document: IrDocument) -> _Characteristic:
    short = document.identifier.removeprefix("org.bluetooth.characteristic.")
    offset = 0
    max_align = 1
    members: list[_Member] = []
    for field in document.fields:
        transform = field.transform
        scaled = transform is not None and not (
            transform.coefficient == 1 and transform.decimal_exponent == 0 and transform.binary_exponent == 0
        )
        c_type, size, align, kind = _SCALED_LAYOUT if scaled else _INTEGER_LAYOUT[field.wire_type]
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
            )
        )
        offset += size
        max_align = max(max_align, align)
    total = (offset + max_align - 1) // max_align * max_align
    unit_ids = {member.unit.identifier if member.unit is not None else None for member in members}
    unit = unit_ids.pop() if len(unit_ids) == 1 else None
    return _Characteristic(
        name=short,
        pascal_name=_pascal(short),
        identifier=document.identifier,
        uuid=document.uuid,
        c_struct=f"btsig_{short}",
        size=total,
        unit=unit,
        members=tuple(members),
    )


def _banner(command: str) -> str:
    return f"// Generated by `{command}`. Do not edit.\n"


def _c_header(item: _Characteristic, command: str) -> str:
    decode = f"btsig_decode_{item.name}"
    encode = f"btsig_encode_{item.name}"
    members = "\n".join(f"    {member.c_type} {member.name};" for member in item.members)
    return (
        f"{_banner(command)}"
        "#pragma once\n\n"
        '#include "btsig/types/status.h"\n\n'
        "#include <stddef.h>\n"
        "#include <stdint.h>\n\n"
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
        "#endif\n"
    )


def _hpp(item: _Characteristic, command: str) -> str:
    return (
        f"{_banner(command)}"
        "#pragma once\n\n"
        f'#include "btsig/{item.name}.h"\n'
        '#include "btsig/types/expected.hpp"\n'
        '#include "btsig/types/span.hpp"\n\n'
        "#include <cstddef>\n"
        "#include <cstdint>\n\n"
        "namespace btsig {\n\n"
        f"class {item.pascal_name} {{\n"
        "public:\n" + "".join(f"    {member.c_type} {member.name};\n" for member in item.members) + "\n"
        f"    [[nodiscard]] static btsig::expected<{item.pascal_name}> decode(\n"
        "        btsig_bytes input, const btsig_context* context);\n\n"
        f"    [[nodiscard]] static btsig::expected<std::size_t> encode(\n"
        f"        const {item.pascal_name}& value, btsig::span<std::uint8_t> out);\n"
        "};\n\n"
        "} // namespace btsig\n"
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
        lines.extend(
            [
                "    {",
                f"        {_c_string(member.name)},",
                f"        {member.value_kind},",
                f"        {unit},",
                f"        {unit_uuid},",
                f"        offsetof({item.c_struct}, {member.name}),",
                f"        btsig::wire_type::{member.wire.value},",
                f"        {member.coefficient},",
                f"        {member.decimal_exponent},",
                f"        {member.binary_exponent},",
                f"        {member.minimum},",
                f"        {member.maximum},",
                f"        {sentinels},",
                f"        {count},",
                "    },",
            ]
        )
    lines.append("};")
    lines.append("")
    return lines


def _descriptor_lines(item: _Characteristic) -> list[str]:
    unit = "nullptr" if item.unit is None else _c_string(item.unit)
    return [
        f"constexpr btsig::CharacteristicDescriptor {item.name}_descriptor{{",
        f"    {_c_string(item.name)},",
        f"    {_c_string(item.identifier)},",
        f"    0x{item.uuid:04X},",
        f"    {unit},",
        "    false,",
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
        lines.append(f"static_assert(offsetof({item.c_struct}, {member.name}) == {member.offset});")
        lines.append(f"static_assert(offsetof({qualified}, {member.name}) == {member.offset});")
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


def _read_documents(identifiers: tuple[str, ...], destination: Path) -> tuple[IrDocument, ...]:
    documents: list[IrDocument] = []
    for identifier in identifiers:
        path = destination / f"generated/ir/{IR_VERSION}/{identifier}.json"
        try:
            data = path.read_bytes()
        except OSError as error:
            raise EmitError(f"missing IR for {identifier}: {error}") from error
        try:
            documents.append(decode_ir(data, require_canonical=True))
        except IrContractError as error:
            raise EmitError(f"IR for {identifier} is not canonical schema version {IR_VERSION}: {error}") from error
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
    """Emit one C and C++ characteristic API per IR document.

    Args:
        characteristics_path: JSON array of characteristic identifiers.
        root: Repository root used to form the generator command.
        output_root: Directory that contains ``generated/ir`` and receives ``btsig/generated``.

    Returns:
        Output path relative to ``output_root`` mapped to file bytes.

    Raises:
        EmitError: If IR is missing, or two characteristics share a UUID.
    """
    repo = repository_root() if root is None else root
    destination = repo if output_root is None else output_root
    identifiers = _load_characteristics(characteristics_path)
    documents = _read_documents(identifiers, destination)
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
    for relative, payload in encoded.items():
        output = destination / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
    return encoded


def main(argv: list[str] | None = None) -> int:
    """Emit the listed characteristics.

    Args:
        argv: Command arguments, excluding the program name.

    Returns:
        Process status, ``0`` on success and ``1`` on an emit error.
    """
    parser = argparse.ArgumentParser(description="Emit C and C++ sources for selected GSS characteristics.")
    parser.add_argument("characteristics", type=Path)
    args = parser.parse_args(argv)
    try:
        emit_characteristics(args.characteristics)
    except EmitError as error:
        print(error.detail)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""GSS value tables become enumerations or single-bit flags."""

from __future__ import annotations

import re

from tools.gss_ir.sources.gss import GssNamedValue, GssValueTable
from tools.gss_ir.v1 import BITS_PER_OCTET, WIRE_SIZE_BYTES, Enumerator, ScalarField, ValueSet, WireType

from .field_name import parse_field_name
from .result import Unsupported

_RULE = "named_values"
_NUMBER = r"(?:0x[0-9A-Fa-f]+|-?\d+)"
_RANGE = re.compile(rf"{_NUMBER}\s*[\u2013\u2014-]\s*{_NUMBER}")
_EXACT_INTEGER = re.compile(_NUMBER)
# These names are C++ keywords or alternative tokens, so they cannot be an enumerator identifier.
_CPP_KEYWORDS = frozenset(
    {
        "alignas",
        "alignof",
        "and",
        "and_eq",
        "asm",
        "auto",
        "bitand",
        "bitor",
        "bool",
        "break",
        "case",
        "catch",
        "char",
        "char8_t",
        "char16_t",
        "char32_t",
        "class",
        "compl",
        "concept",
        "const",
        "consteval",
        "constexpr",
        "constinit",
        "const_cast",
        "continue",
        "co_await",
        "co_return",
        "co_yield",
        "decltype",
        "default",
        "delete",
        "do",
        "double",
        "dynamic_cast",
        "else",
        "enum",
        "explicit",
        "export",
        "extern",
        "false",
        "float",
        "for",
        "friend",
        "goto",
        "if",
        "inline",
        "int",
        "long",
        "mutable",
        "namespace",
        "new",
        "noexcept",
        "not",
        "not_eq",
        "nullptr",
        "operator",
        "or",
        "or_eq",
        "private",
        "protected",
        "public",
        "register",
        "reinterpret_cast",
        "requires",
        "return",
        "short",
        "signed",
        "sizeof",
        "static",
        "static_assert",
        "static_cast",
        "struct",
        "switch",
        "template",
        "this",
        "thread_local",
        "throw",
        "true",
        "try",
        "typedef",
        "typeid",
        "typename",
        "union",
        "unsigned",
        "using",
        "virtual",
        "void",
        "volatile",
        "wchar_t",
        "while",
        "xor",
        "xor_eq",
    }
)
_FLAG_WIRE = frozenset(
    {
        WireType.UINT1,
        WireType.UINT2,
        WireType.UINT8,
        WireType.UINT16,
        WireType.UINT24,
        WireType.UINT32,
        WireType.UINT48,
        WireType.UINT64,
        WireType.BOOLEAN8,
        WireType.BOOLEAN16,
        WireType.BOOLEAN24,
        WireType.BOOLEAN32,
    }
)
_REAL_WIRE = frozenset({WireType.MEDFLOAT16, WireType.MEDFLOAT32, WireType.FLOAT32})
# load_integer stores a uint64 member in int64 and rejects the high bit.
_MAX_FLAG_BIT = 62


def _wire_bits(wire: WireType) -> int | None:
    if wire is WireType.UINT1:
        return 1
    if wire is WireType.UINT2:
        return 2
    width = WIRE_SIZE_BYTES.get(wire)
    if width is None:
        return None
    return width * BITS_PER_OCTET


def _reserved(description: str) -> bool:
    first = description.splitlines()[0].strip().rstrip(":").casefold()
    return first in {"rfu", "reserved"} or first.startswith("reserved") or first.startswith("prohibited")


def _label(description: str, *, flags: bool) -> str:
    first = description.splitlines()[0].strip()
    if flags:
        lowered = first.casefold()
        suffix = " support bit:"
        if lowered.endswith(suffix):
            first = first[: -len(suffix)]
        elif lowered.endswith(" support bit"):
            first = first[: -len(" support bit")]
    return first.rstrip(":").strip()


def _identifier(label: str) -> str | Unsupported:
    name = parse_field_name(label)
    if isinstance(name, Unsupported):
        return Unsupported(rule=_RULE, detail=name.detail)
    if name in _CPP_KEYWORDS:
        name = f"{name}_value"
    return name


def _integer(raw: str) -> int | None:
    if _EXACT_INTEGER.fullmatch(raw) is None:
        return None
    if raw.startswith(("0x", "0X")):
        return int(raw, 16)
    return int(raw, 10)


def _enumerator(
    field: ScalarField,
    entry: GssNamedValue,
    *,
    flags: bool,
    width: int,
    used_names: set[str],
) -> Enumerator | Unsupported | None:
    number = _integer(entry.raw)
    if number is None:
        if _reserved(entry.description):
            return None
        return Unsupported(rule=_RULE, detail=f"{field.name} value {entry.raw!r} is not an integer")
    if flags and _reserved(entry.description):
        return None
    if flags:
        if number < 0 or number >= width or number > _MAX_FLAG_BIT:
            return Unsupported(rule=_RULE, detail=f"{field.name} bit {number} does not fit")
        number = 1 << number
    label = _label(entry.description, flags=flags)
    name = _identifier(label)
    if isinstance(name, Unsupported):
        return name
    if name in used_names:
        name = f"{name}_{number}"
    if name in used_names:
        return Unsupported(rule=_RULE, detail=f"duplicate enumerator name '{name}'")
    used_names.add(name)
    if number < field.minimum or number > field.maximum:
        return Unsupported(rule=_RULE, detail=f"{field.name} value {number} is outside the field range")
    return Enumerator(name=name, value=number)


def closed_value_table(table: GssValueTable) -> bool:
    """Return whether every non-reserved entry is one discrete code.

    Args:
        table: Raw GSS value table.

    Returns:
        True when the table is an enumeration. A reserved span may sit beside the codes.
    """
    saw_code = False
    for entry in table.entries:
        if entry.kind != "value":
            return False
        if _integer(entry.raw) is not None:
            saw_code = True
            continue
        if not _reserved(entry.description):
            return False
    return saw_code


def apply_named_values(field: ScalarField, table: GssValueTable) -> ScalarField | Unsupported:
    """Attach enumerators from one GSS value table.

    Args:
        field: Field already parsed from the structure entry.
        table: Raw codes or bits for that field.

    Returns:
        The field with ``enumeration`` or ``flags`` enumerators, the same field
        when the table names no usable constant, or an unsupported result.

    A reserved or prohibited span is not an enumerator. A reserved bit is omitted
    from a flags set. A discrete reserved code stays an enumeration constant.
    """
    kinds = {entry.kind for entry in table.entries}
    if len(kinds) != 1:
        return Unsupported(rule=_RULE, detail=f"{field.name} mixes bit and value entries")
    flags = "bit" in kinds
    if not flags and not closed_value_table(table):
        return field
    if field.wire_type is WireType.UTF8 or field.wire_type in _REAL_WIRE or field.transform is not None:
        return Unsupported(rule=_RULE, detail=f"{field.name} cannot carry named constants")
    if flags and field.wire_type not in _FLAG_WIRE:
        return Unsupported(rule=_RULE, detail=f"{field.name} flags require an unsigned wire")
    # A span such as bits 3-6 is its own packed code, not one flag bit.
    if flags and any(_RANGE.fullmatch(entry.raw) and not _reserved(entry.description) for entry in table.entries):
        return field
    width = _wire_bits(field.wire_type)
    if width is None:
        return Unsupported(rule=_RULE, detail=f"{field.name} has no integer width")

    enumerators: list[Enumerator] = []
    used_names: set[str] = set()
    for entry in table.entries:
        built = _enumerator(field, entry, flags=flags, width=width, used_names=used_names)
        if isinstance(built, Unsupported):
            return built
        if built is not None:
            enumerators.append(built)
    if not enumerators:
        return field
    return ScalarField(
        name=field.name,
        wire_type=field.wire_type,
        minimum=field.minimum,
        maximum=field.maximum,
        transform=field.transform,
        unit=field.unit,
        sentinels=field.sentinels,
        utf8_capacity=field.utf8_capacity,
        enumerators=tuple(enumerators),
        value_set=ValueSet.FLAGS if flags else ValueSet.ENUMERATION,
    )

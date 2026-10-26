"""IR schema version 1: the fixed-field document in ADR-0003."""

from __future__ import annotations

import re
from enum import Enum

import msgspec

IR_VERSION = 1
IDENTIFIER_PREFIX = "org.bluetooth.characteristic."
UNIT_PREFIX = "org.bluetooth.unit."
UUID16_MAX = 0xFFFF
BITS_PER_OCTET = 8

_SNAKE_CASE = re.compile(r"[a-z][a-z0-9_]*\Z")


class IrErrorCode(str, Enum):
    """Stable build-time IR contract error codes."""

    INVALID_SCHEMA = "invalid_schema"
    UNSUPPORTED_VERSION = "unsupported_version"
    SEMANTIC_VIOLATION = "semantic_violation"
    NON_CANONICAL = "non_canonical"


class IrContractError(ValueError):
    """An IR document violated the versioned contract."""

    def __init__(self, code: IrErrorCode, detail: str) -> None:
        """Initialise an error with a stable code and diagnostic detail."""
        super().__init__(f"{code.value}: {detail}")
        self.code = code
        self.detail = detail


class ContractStruct(
    msgspec.Struct,
    frozen=True,
    kw_only=True,
    forbid_unknown_fields=True,
    omit_defaults=True,
):
    """Immutable closed-schema representation."""


class WireType(str, Enum):
    """Fixed-width wire types named by ADR-0003.

    Boolean widths are bitfields stored as unsigned integers. ``medfloat16``,
    ``medfloat32``, and ``float32`` store the little-endian bit pattern; the
    generated member is the decoded ``double``.
    """

    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT24 = "uint24"
    UINT32 = "uint32"
    UINT48 = "uint48"
    UINT64 = "uint64"
    SINT8 = "sint8"
    SINT16 = "sint16"
    SINT24 = "sint24"
    SINT32 = "sint32"
    BOOLEAN8 = "boolean8"
    BOOLEAN16 = "boolean16"
    BOOLEAN24 = "boolean24"
    BOOLEAN32 = "boolean32"
    MEDFLOAT16 = "medfloat16"
    MEDFLOAT32 = "medfloat32"
    FLOAT32 = "float32"
    UTF8 = "utf8"
    UINT1 = "uint1"
    UINT2 = "uint2"


WIRE_SIZE_BYTES: dict[WireType, int] = {
    WireType.UINT8: 1,
    WireType.UINT16: 2,
    WireType.UINT24: 3,
    WireType.UINT32: 4,
    WireType.UINT48: 6,
    WireType.UINT64: 8,
    WireType.SINT8: 1,
    WireType.SINT16: 2,
    WireType.SINT24: 3,
    WireType.SINT32: 4,
    WireType.BOOLEAN8: 1,
    WireType.BOOLEAN16: 2,
    WireType.BOOLEAN24: 3,
    WireType.BOOLEAN32: 4,
    WireType.MEDFLOAT16: 2,
    WireType.MEDFLOAT32: 4,
    WireType.FLOAT32: 4,
}


class SentinelMeaning(str, Enum):
    """Sentinel meanings defined for this schema version."""

    NOT_KNOWN = "not_known"
    NOT_VALID = "not_valid"


class Transform(ContractStruct, frozen=True):
    """Exact transform: decoded = raw * coefficient * 10^decimal_exponent * 2^binary_exponent."""

    coefficient: int = 1
    decimal_exponent: int = 0
    binary_exponent: int = 0


class UnitRef(ContractStruct, frozen=True):
    """Assigned unit joined onto a field."""

    identifier: str
    uuid: int


class Sentinel(ContractStruct, frozen=True):
    """One raw sentinel and its meaning."""

    raw_value: int
    meaning: SentinelMeaning


class ValueSet(str, Enum):
    """How a field's named constants combine.

    ``enumeration`` is one code. ``flags`` is a set of independent bits.
    """

    ENUMERATION = "enumeration"
    FLAGS = "flags"


class Enumerator(ContractStruct, frozen=True):
    """One named constant stored in a field.

    An enumeration stores the raw code. A flags set stores the single-bit mask.
    """

    name: str
    value: int


class ScalarField(ContractStruct, frozen=True):
    """One resolved field in wire order.

    Integer, boolean, and real fields store a raw ``minimum`` and ``maximum``.
    A UTF-8 field stores ``0`` for both. ``utf8_capacity`` is the ``utf8s{N}``
    octet maximum; a variable ``utf8s`` omits it. ``enumerators`` is empty unless
    ``value_set`` is ``enumeration`` or ``flags``.
    """

    name: str
    wire_type: WireType
    minimum: int
    maximum: int
    transform: Transform | None = None
    unit: UnitRef | None = None
    sentinels: tuple[Sentinel, ...] = ()
    utf8_capacity: int | None = None
    enumerators: tuple[Enumerator, ...] = ()
    value_set: ValueSet | None = None


class Provenance(ContractStruct, frozen=True):
    """Trace from the document back to the SIG YAML file."""

    source_path: str
    source_identifier: str


class IrDocument(ContractStruct, frozen=True):
    """One self-contained characteristic document."""

    schema_version: int
    identifier: str
    uuid: int
    provenance: Provenance
    fields: tuple[ScalarField, ...]


_DECODER = msgspec.json.Decoder(IrDocument, strict=True)


def _semantic_error(detail: str) -> IrContractError:
    return IrContractError(IrErrorCode.SEMANTIC_VIOLATION, detail)


def _check_uuid16(value: int, location: str) -> None:
    if value < 0 or value > UUID16_MAX:
        raise _semantic_error(f"{location} must be a 16-bit UUID")


def _validate_field(field: ScalarField, names: set[str]) -> None:
    if field.name in names:
        raise _semantic_error(f"duplicate field name '{field.name}'")
    names.add(field.name)
    if _SNAKE_CASE.fullmatch(field.name) is None:
        raise _semantic_error(f"field name '{field.name}' must be snake_case")
    if field.minimum > field.maximum:
        raise _semantic_error(f"{field.name}: minimum exceeds maximum")
    if field.wire_type is WireType.UTF8:
        if field.minimum != 0 or field.maximum != 0:
            raise _semantic_error(f"{field.name}: utf8 has no integer range")
        if field.utf8_capacity is not None and field.utf8_capacity <= 0:
            raise _semantic_error(f"{field.name}: utf8 capacity must be positive")
    elif field.utf8_capacity is not None:
        raise _semantic_error(f"{field.name}: utf8 capacity is only valid for utf8")
    if field.transform is not None and field.transform.coefficient == 0:
        raise _semantic_error(f"{field.name}: transform coefficient must not be zero")
    if field.unit is not None:
        if not field.unit.identifier.startswith(UNIT_PREFIX):
            raise _semantic_error(f"{field.name}: unit identifier must use the unit prefix")
        _check_uuid16(field.unit.uuid, f"{field.name} unit uuid")
    seen_raw: set[int] = set()
    for sentinel in field.sentinels:
        if sentinel.raw_value in seen_raw:
            raise _semantic_error(f"{field.name}: duplicate sentinel raw value {sentinel.raw_value}")
        seen_raw.add(sentinel.raw_value)
    _validate_enumerators(field)


def _validate_enumerators(field: ScalarField) -> None:
    if field.value_set is None:
        if field.enumerators:
            raise _semantic_error(f"{field.name}: enumerators require a value set")
        return
    if field.wire_type is WireType.UTF8:
        raise _semantic_error(f"{field.name}: utf8 has no enumerators")
    if not field.enumerators:
        raise _semantic_error(f"{field.name}: value set has no enumerators")
    names: set[str] = set()
    values: set[int] = set()
    for enumerator in field.enumerators:
        if _SNAKE_CASE.fullmatch(enumerator.name) is None:
            raise _semantic_error(f"{field.name}: enumerator '{enumerator.name}' must be snake_case")
        if enumerator.name in names:
            raise _semantic_error(f"{field.name}: duplicate enumerator name '{enumerator.name}'")
        names.add(enumerator.name)
        if enumerator.value in values:
            raise _semantic_error(f"{field.name}: duplicate enumerator value {enumerator.value}")
        values.add(enumerator.value)
        if enumerator.value < field.minimum or enumerator.value > field.maximum:
            raise _semantic_error(f"{field.name}: enumerator {enumerator.value} is outside the field range")
        if field.value_set is ValueSet.FLAGS and (enumerator.value <= 0 or enumerator.value & (enumerator.value - 1)):
            raise _semantic_error(f"{field.name}: flag {enumerator.value} is not one bit")


def validate_ir(document: IrDocument) -> None:
    """Validate cross-field invariants that the closed schema does not express.

    Args:
        document: Document already decoded into the schema version 1 types.

    Raises:
        IrContractError: If the version or a semantic rule fails.
    """
    if document.schema_version != IR_VERSION:
        raise IrContractError(
            IrErrorCode.UNSUPPORTED_VERSION,
            f"expected schema_version {IR_VERSION}, got {document.schema_version}",
        )
    if not document.identifier.startswith(IDENTIFIER_PREFIX):
        raise _semantic_error("identifier must use the Bluetooth SIG characteristic prefix")
    _check_uuid16(document.uuid, "uuid")
    if not document.provenance.source_path:
        raise _semantic_error("provenance source_path must not be empty")
    if document.provenance.source_identifier != document.identifier:
        raise _semantic_error("provenance source_identifier must match document identifier")
    if not document.fields:
        raise _semantic_error("fields must not be empty")
    names: set[str] = set()
    for field in document.fields:
        _validate_field(field, names)


def encode_ir(document: IrDocument) -> bytes:
    """Encode one validated document as canonical compact UTF-8 JSON.

    Args:
        document: Schema version 1 document.

    Returns:
        Canonical JSON bytes with defaults omitted and no trailing whitespace.

    Raises:
        IrContractError: If semantic validation fails.
    """
    validate_ir(document)
    return msgspec.json.encode(document)


def decode_ir(data: bytes, *, require_canonical: bool = False) -> IrDocument:
    """Decode and validate one schema version 1 document.

    Args:
        data: UTF-8 JSON document.
        require_canonical: Reject a valid document that is not in canonical byte form.

    Returns:
        Validated document.

    Raises:
        IrContractError: If the schema, version, semantics, or canonical form is invalid.
    """
    try:
        document = _DECODER.decode(data)
    except msgspec.ValidationError as error:
        raise IrContractError(IrErrorCode.INVALID_SCHEMA, str(error)) from error
    validate_ir(document)
    if require_canonical and encode_ir(document) != data:
        raise IrContractError(IrErrorCode.NON_CANONICAL, "document is not canonical JSON")
    return document


def encode_json_schema() -> bytes:
    """Return the generated JSON Schema for this frozen document.

    Returns:
        UTF-8 JSON Schema bytes, indented, with one trailing newline.
    """
    schema = msgspec.json.schema(IrDocument)
    _order_nullable_unions(schema)
    return msgspec.json.format(msgspec.json.encode(schema), indent=2) + b"\n"


def _order_nullable_unions(node: object) -> None:
    """Put a null schema first inside each ``anyOf``.

    msgspec 0.19 emits ``null`` then ``$ref``. msgspec 0.22 emits ``$ref`` then ``null``.
    The checked-in schema keeps the null-first order.
    """
    if isinstance(node, dict):
        for value in node.values():
            _order_nullable_unions(value)
        options = node.get("anyOf")
        if isinstance(options, list):
            options.sort(key=_nullable_union_rank)
    elif isinstance(node, list):
        for item in node:
            _order_nullable_unions(item)


def _nullable_union_rank(option: object) -> int:
    return 0 if isinstance(option, dict) and len(option) == 1 and option.get("type") == "null" else 1

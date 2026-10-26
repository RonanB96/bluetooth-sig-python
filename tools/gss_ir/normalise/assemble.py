"""Assemble a self-contained IR document from phrase-rule results."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from tools.gss_ir.sources import (
    STRUCT_TYPE,
    GssField,
    GssSourceError,
    GssValueTable,
    read_characteristic,
    read_characteristic_uuids,
    read_unit_uuids,
)
from tools.gss_ir.v1 import (
    IR_VERSION,
    IrContractError,
    IrDocument,
    Provenance,
    ScalarField,
    Transform,
    WireType,
    validate_ir,
)

from .field_name import parse_field_name
from .fixed_size import parse_fixed_size
from .named_values import apply_named_values, closed_value_table
from .prohibited import parse_prohibited
from .result import Unsupported
from .sentinel import parse_sentinels
from .struct_ref import copied_field_name, parse_struct_reference
from .subbyte import parse_subbyte_size, parse_subbyte_type, subbyte_domain
from .transform import parse_transform
from .unit import parse_unit
from .utf8 import Utf8Type, parse_utf8_size, parse_utf8_type
from .value_range import parse_range
from .wire_type import implicit_raw_domain, integer_domain, outside_wire_detail, parse_wire_type

CHARACTERISTIC_UUID_RULE = "characteristic_uuid"
_GSS_DIRECTORY = Path("bluetooth_sig/gss")
_CHARACTERISTIC_UUIDS = Path("bluetooth_sig/assigned_numbers/uuids/characteristic_uuids.yaml")
_UNIT_UUIDS = Path("bluetooth_sig/assigned_numbers/uuids/units.yaml")


def repository_root() -> Path:
    """Return the repository root that contains this package.

    Returns:
        Absolute repository path.
    """
    return Path(__file__).resolve().parents[3]


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


@lru_cache(maxsize=4)
def _paths_by_identifier(root: str) -> dict[str, str]:
    base = Path(root)
    found: dict[str, str] = {}
    for path in iter_characteristic_paths(base):
        try:
            characteristic = read_characteristic(path, source_path=_relative(path, base))
        except (GssSourceError, OSError):
            continue
        found.setdefault(characteristic.identifier, str(path))
    return found


@lru_cache(maxsize=4)
def _assigned_numbers(root: str) -> tuple[dict[str, int], dict[str, int]]:
    base = Path(root)
    return (
        read_characteristic_uuids(base / _CHARACTERISTIC_UUIDS),
        read_unit_uuids(base / _UNIT_UUIDS),
    )


def _factors(transform: Transform | None) -> tuple[int, int, int]:
    if transform is None:
        return (1, 0, 0)
    return (transform.coefficient, transform.decimal_exponent, transform.binary_exponent)


def _utf8_field(raw: GssField, utf8: Utf8Type, units: dict[str, int]) -> ScalarField | Unsupported:
    name = parse_field_name(raw.field)
    if isinstance(name, Unsupported):
        return name
    sized = parse_utf8_size(raw.size, utf8.capacity)
    if isinstance(sized, Unsupported):
        return sized
    transform = parse_transform(raw.description)
    if isinstance(transform, Unsupported):
        return transform
    if transform is not None:
        return Unsupported(rule="utf8", detail="utf8 field has a transform")
    unit = parse_unit(raw.description, units)
    if isinstance(unit, Unsupported):
        return unit
    sentinels = parse_sentinels(raw.description, WireType.UTF8)
    if isinstance(sentinels, Unsupported):
        return sentinels
    prohibited = parse_prohibited(raw.description)
    if isinstance(prohibited, Unsupported):
        return prohibited
    return ScalarField(
        name=name,
        wire_type=WireType.UTF8,
        minimum=0,
        maximum=0,
        unit=unit,
        sentinels=sentinels,
        utf8_capacity=utf8.capacity,
    )


def _subbyte_field(raw: GssField, wire: WireType, units: dict[str, int]) -> ScalarField | Unsupported:
    name = parse_field_name(raw.field)
    if isinstance(name, Unsupported):
        return name
    sized = parse_subbyte_size(raw.size, wire)
    if isinstance(sized, Unsupported):
        return sized
    transform = parse_transform(raw.description)
    if isinstance(transform, Unsupported):
        return transform
    coefficient, decimal_exponent, binary_exponent = _factors(transform)
    if coefficient == 0:
        return Unsupported(rule="transform", detail="coefficient must not be zero")
    unit = parse_unit(raw.description, units)
    if isinstance(unit, Unsupported):
        return unit
    endpoints = parse_range(
        raw.description,
        coefficient=coefficient,
        decimal_exponent=decimal_exponent,
        binary_exponent=binary_exponent,
    )
    if isinstance(endpoints, Unsupported) and endpoints.detail == "range is absent":
        endpoints = subbyte_domain(wire)
    if isinstance(endpoints, Unsupported):
        return endpoints
    sentinels = parse_sentinels(raw.description, wire)
    if isinstance(sentinels, Unsupported):
        return sentinels
    prohibited = parse_prohibited(raw.description)
    if isinstance(prohibited, Unsupported):
        return prohibited
    minimum, maximum = endpoints
    return ScalarField(
        name=name,
        wire_type=wire,
        minimum=minimum,
        maximum=maximum,
        transform=transform,
        unit=unit,
        sentinels=sentinels,
    )


def _scalar(
    raw: GssField,
    units: dict[str, int],
    *,
    absent_domain: tuple[int, int] | None = None,
) -> ScalarField | Unsupported:
    name = parse_field_name(raw.field)
    if isinstance(name, Unsupported):
        return name
    wire = parse_wire_type(raw.type_text)
    if isinstance(wire, Unsupported):
        return wire
    sized = parse_fixed_size(raw.size, wire)
    if isinstance(sized, Unsupported):
        return sized
    transform = parse_transform(raw.description)
    if isinstance(transform, Unsupported):
        return transform
    coefficient, decimal_exponent, binary_exponent = _factors(transform)
    if coefficient == 0:
        return Unsupported(rule="transform", detail="coefficient must not be zero")
    unit = parse_unit(raw.description, units)
    if isinstance(unit, Unsupported):
        return unit
    endpoints = parse_range(
        raw.description,
        coefficient=coefficient,
        decimal_exponent=decimal_exponent,
        binary_exponent=binary_exponent,
    )
    if isinstance(endpoints, Unsupported) and endpoints.detail == "range is absent":
        domain = implicit_raw_domain(wire)
        if domain is None:
            domain = absent_domain
        if domain is not None:
            endpoints = domain
    if isinstance(endpoints, Unsupported):
        return endpoints
    sentinels = parse_sentinels(raw.description, wire)
    if isinstance(sentinels, Unsupported):
        return sentinels
    prohibited = parse_prohibited(raw.description)
    if isinstance(prohibited, Unsupported):
        return prohibited
    minimum, maximum = endpoints
    return ScalarField(
        name=name,
        wire_type=wire,
        minimum=minimum,
        maximum=maximum,
        transform=transform,
        unit=unit,
        sentinels=sentinels,
    )


def _struct_field(
    raw: GssField,
    *,
    root: Path,
    stack: frozenset[str],
) -> ScalarField | Unsupported:
    referenced = parse_struct_reference(raw.description)
    if isinstance(referenced, Unsupported):
        return referenced
    if referenced in stack:
        return Unsupported(rule="struct_ref", detail=f"cycle at {referenced}")
    path = root / _GSS_DIRECTORY / f"{referenced}.yaml"
    if not path.is_file():
        return Unsupported(rule="struct_ref", detail=f"{referenced} does not resolve to one integer scalar")
    resolved = normalise_path(path, root=root, stack=stack)
    if isinstance(resolved, Unsupported) or len(resolved.fields) != 1:
        return Unsupported(rule="struct_ref", detail=f"{referenced} does not resolve to one integer scalar")
    copied = resolved.fields[0]
    sized = parse_fixed_size(raw.size, copied.wire_type)
    if isinstance(sized, Unsupported):
        return sized
    name = copied_field_name(raw.field, referenced)
    if isinstance(name, Unsupported):
        return name
    return ScalarField(
        name=name,
        wire_type=copied.wire_type,
        minimum=copied.minimum,
        maximum=copied.maximum,
        transform=copied.transform,
        unit=copied.unit,
        sentinels=copied.sentinels,
        utf8_capacity=copied.utf8_capacity,
        enumerators=copied.enumerators,
        value_set=copied.value_set,
    )


def _value_tables(tables: tuple[GssValueTable, ...]) -> dict[str, GssValueTable] | Unsupported:
    indexed: dict[str, GssValueTable] = {}
    for table in tables:
        name = parse_field_name(table.name)
        if isinstance(name, Unsupported):
            return Unsupported(rule="named_values", detail=name.detail)
        if name in indexed:
            return Unsupported(rule="named_values", detail=f"duplicate value table '{name}'")
        indexed[name] = table
    return indexed


def _require_wire_fit(field: ScalarField) -> ScalarField | Unsupported:
    span = integer_domain(field.wire_type)
    if span is None:
        return field
    low, high = span
    if field.minimum < low or field.maximum > high:
        return Unsupported(rule="range", detail=outside_wire_detail(field.wire_type))
    return field


def _one_field(
    raw: GssField,
    *,
    root: Path,
    units: dict[str, int],
    stack: frozenset[str],
    absent_domain: tuple[int, int] | None = None,
) -> ScalarField | Unsupported:
    if raw.type_text == STRUCT_TYPE:
        return _struct_field(raw, root=root, stack=stack)
    utf8 = parse_utf8_type(raw.type_text)
    if utf8 is not None:
        return _utf8_field(raw, utf8, units)
    subbyte = parse_subbyte_type(raw.type_text)
    if subbyte is not None:
        return _subbyte_field(raw, subbyte, units)
    return _scalar(raw, units, absent_domain=absent_domain)


def _build_fields(
    raw_fields: tuple[GssField, ...],
    tables: dict[str, GssValueTable],
    *,
    root: Path,
    units: dict[str, int],
    stack: frozenset[str],
) -> tuple[ScalarField, ...] | Unsupported:
    fields: list[ScalarField] = []
    for raw in raw_fields:
        field_name = parse_field_name(raw.field)
        table = None if isinstance(field_name, Unsupported) else tables.get(field_name)
        absent_domain = None
        if table is not None and closed_value_table(table):
            wire = parse_wire_type(raw.type_text)
            if not isinstance(wire, Unsupported):
                absent_domain = integer_domain(wire)
        built = _one_field(raw, root=root, units=units, stack=stack, absent_domain=absent_domain)
        if isinstance(built, Unsupported):
            return built
        table = tables.get(built.name)
        if table is not None:
            built = apply_named_values(built, table)
            if isinstance(built, Unsupported):
                return built
        built = _require_wire_fit(built)
        if isinstance(built, Unsupported):
            return built
        if any(existing.name == built.name for existing in fields):
            return Unsupported(rule="field_name", detail=f"duplicate field name '{built.name}'")
        fields.append(built)
    if any(field.wire_type is WireType.UTF8 for field in fields) and len(fields) != 1:
        return Unsupported(rule="utf8", detail="utf8 length is the whole value")
    return tuple(fields)


def normalise_path(
    path: Path,
    *,
    root: Path | None = None,
    stack: frozenset[str] = frozenset(),
) -> IrDocument | Unsupported:
    """Normalise one characteristic YAML file.

    Args:
        path: Characteristic YAML path.
        root: Repository root. Defaults to the root that contains this file.
        stack: Identifiers currently being resolved, used to stop a cycle.

    Returns:
        A validated IR document, or the first unsupported rule.
    """
    repo = repository_root() if root is None else root
    source_path = _relative(path, repo)
    try:
        characteristic = read_characteristic(path, source_path=source_path)
    except GssSourceError as error:
        return Unsupported(rule="gss_reader", detail=error.detail)
    except OSError as error:
        return Unsupported(rule="gss_reader", detail=str(error))
    if characteristic.identifier in stack:
        return Unsupported(rule="struct_ref", detail=f"cycle at {characteristic.identifier}")
    characteristic_uuids, units = _assigned_numbers(str(repo.resolve()))
    uuid = characteristic_uuids.get(characteristic.identifier)
    if uuid is None:
        return Unsupported(
            rule=CHARACTERISTIC_UUID_RULE,
            detail=f"missing UUID for {characteristic.identifier}",
        )
    tables = _value_tables(characteristic.value_tables)
    if isinstance(tables, Unsupported):
        return tables
    fields = _build_fields(
        characteristic.fields,
        tables,
        root=repo,
        units=units,
        stack=stack | {characteristic.identifier},
    )
    if isinstance(fields, Unsupported):
        return fields
    document = IrDocument(
        schema_version=IR_VERSION,
        identifier=characteristic.identifier,
        uuid=uuid,
        provenance=Provenance(source_path=source_path, source_identifier=characteristic.identifier),
        fields=tuple(fields),
    )
    try:
        validate_ir(document)
    except IrContractError as error:
        return Unsupported(rule="ir", detail=error.detail)
    return document


def normalise_identifier(identifier: str, *, root: Path | None = None) -> IrDocument | Unsupported:
    """Normalise one characteristic by its SIG identifier.

    Args:
        identifier: ``org.bluetooth.characteristic.*`` identifier.
        root: Repository root.

    Returns:
        A validated IR document, or the first unsupported rule.
    """
    repo = repository_root() if root is None else root
    path = repo / _GSS_DIRECTORY / f"{identifier}.yaml"
    if not path.is_file():
        indexed = _paths_by_identifier(str(repo.resolve())).get(identifier)
        if indexed is None:
            return Unsupported(rule="gss_reader", detail=f"missing {identifier}")
        path = Path(indexed)
    return normalise_path(path, root=repo)


def iter_characteristic_paths(root: Path | None = None) -> tuple[Path, ...]:
    """Return characteristic YAML paths in path order.

    Args:
        root: Repository root.

    Returns:
        Sorted paths of ``org.bluetooth.characteristic.*.yaml``.
    """
    repo = repository_root() if root is None else root
    return tuple(sorted((repo / _GSS_DIRECTORY).glob("org.bluetooth.characteristic.*.yaml")))

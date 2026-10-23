"""Tests for the schema version 1 document."""

from __future__ import annotations

from pathlib import Path

import msgspec
import pytest

from tools.gss_ir import IrContractError, IrErrorCode, decode_ir, encode_ir, encode_json_schema
from tools.gss_ir.v1 import IrDocument, Provenance, ScalarField, Sentinel, SentinelMeaning, Transform, UnitRef, WireType

IDENTIFIER = "org.bluetooth.characteristic.contract_fixture"
SCHEMA_PATH = Path(__file__).resolve().parents[3] / "tools" / "gss_ir" / "v1.schema.json"


def _document() -> IrDocument:
    return IrDocument(
        schema_version=1,
        identifier=IDENTIFIER,
        uuid=1,
        provenance=Provenance(source_path="contract-test", source_identifier=IDENTIFIER),
        fields=(ScalarField(name="sample_value", wire_type=WireType.UINT8, minimum=0, maximum=10),),
    )


def test_document_round_trip_is_canonical() -> None:
    encoded = encode_ir(_document())
    document = decode_ir(encoded, require_canonical=True)

    assert encode_ir(document) == encoded
    assert document.provenance.source_identifier == document.identifier
    assert b'"transform"' not in encoded
    assert b'"sentinels"' not in encoded


def test_unknown_field_is_rejected() -> None:
    encoded = encode_ir(_document()).replace(b'"uuid":1', b'"uuid":1,"class_name":"Fixture"')

    with pytest.raises(IrContractError) as error:
        decode_ir(encoded)

    assert error.value.code is IrErrorCode.INVALID_SCHEMA


def test_prototype_field_kind_is_rejected() -> None:
    encoded = encode_ir(_document()).replace(b'"wire_type":"uint8"', b'"wire_type":"uint8","kind":"scalar"')

    with pytest.raises(IrContractError) as error:
        decode_ir(encoded)

    assert error.value.code is IrErrorCode.INVALID_SCHEMA


def test_unknown_version_has_stable_error_code() -> None:
    encoded = encode_ir(_document()).replace(b'"schema_version":1', b'"schema_version":2')

    with pytest.raises(IrContractError) as error:
        decode_ir(encoded)

    assert error.value.code is IrErrorCode.UNSUPPORTED_VERSION
    assert error.value.detail == "expected schema_version 1, got 2"


def test_noncanonical_json_is_rejected_on_request() -> None:
    encoded = encode_ir(_document())
    noncanonical = encoded.replace(b'{"schema_version"', b'{\n  "schema_version"', 1)

    with pytest.raises(IrContractError) as error:
        decode_ir(noncanonical, require_canonical=True)

    assert error.value.code is IrErrorCode.NON_CANONICAL


def test_duplicate_field_names_are_rejected() -> None:
    field = ScalarField(name="sample_value", wire_type=WireType.UINT8, minimum=0, maximum=1)
    document = IrDocument(
        schema_version=1,
        identifier=IDENTIFIER,
        uuid=1,
        provenance=Provenance(source_path="contract-test", source_identifier=IDENTIFIER),
        fields=(field, field),
    )

    with pytest.raises(IrContractError) as error:
        encode_ir(document)

    assert error.value.code is IrErrorCode.SEMANTIC_VIOLATION
    assert error.value.detail == "duplicate field name 'sample_value'"


def test_zero_coefficient_fails() -> None:
    document = msgspec.structs.replace(
        _document(),
        fields=(
            ScalarField(
                name="sample_value",
                wire_type=WireType.SINT16,
                minimum=0,
                maximum=1,
                transform=Transform(coefficient=0),
            ),
        ),
    )

    with pytest.raises(IrContractError) as error:
        encode_ir(document)

    assert error.value.detail == "sample_value: transform coefficient must not be zero"


def test_provenance_identifier_must_match_document() -> None:
    document = msgspec.structs.replace(
        _document(),
        provenance=Provenance(
            source_path="contract-test",
            source_identifier="org.bluetooth.characteristic.other_fixture",
        ),
    )

    with pytest.raises(IrContractError) as error:
        encode_ir(document)

    assert error.value.detail == "provenance source_identifier must match document identifier"


def test_minimum_above_maximum_is_rejected() -> None:
    document = msgspec.structs.replace(
        _document(),
        fields=(ScalarField(name="sample_value", wire_type=WireType.UINT8, minimum=2, maximum=1),),
    )

    with pytest.raises(IrContractError) as error:
        encode_ir(document)

    assert error.value.detail == "sample_value: minimum exceeds maximum"


def test_transform_and_sentinel_round_trip() -> None:
    document = msgspec.structs.replace(
        _document(),
        fields=(
            ScalarField(
                name="sample_value",
                wire_type=WireType.SINT16,
                minimum=-10,
                maximum=10,
                transform=Transform(decimal_exponent=-2),
                unit=UnitRef(identifier="org.bluetooth.unit.percentage", uuid=0x27AD),
                sentinels=(Sentinel(raw_value=-32768, meaning=SentinelMeaning.NOT_KNOWN),),
            ),
        ),
    )

    assert decode_ir(encode_ir(document), require_canonical=True) == document


def test_frozen_json_schema_matches_bytes() -> None:
    assert encode_json_schema() == SCHEMA_PATH.read_bytes()

"""Phrase-rule tests using quoted SIG sentences."""

from __future__ import annotations

import pytest

from tools.gss_ir.normalise.field_name import parse_field_name
from tools.gss_ir.normalise.fixed_size import parse_fixed_size
from tools.gss_ir.normalise.prohibited import OutsideRange, parse_prohibited
from tools.gss_ir.normalise.result import Unsupported
from tools.gss_ir.normalise.sentinel import parse_sentinels
from tools.gss_ir.normalise.struct_ref import copied_field_name, parse_struct_reference
from tools.gss_ir.normalise.transform import parse_transform
from tools.gss_ir.normalise.unit import parse_unit
from tools.gss_ir.normalise.value_range import displayed_to_raw, parse_range
from tools.gss_ir.normalise.wire_type import parse_wire_type
from tools.gss_ir.v1 import SentinelMeaning, WireType

TEMPERATURE = "org.bluetooth.characteristic.temperature"
CELSIUS = "org.bluetooth.unit.thermodynamic_temperature.degree_celsius"


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Instantaneous Speed", "instantaneous_speed"),
        ("Location - Latitude", "location_latitude"),
        (
            "Blood Pressure Measurement Compound Value - Systolic (mmHg)",
            "blood_pressure_measurement_compound_value_systolic",
        ),
        ("Minimum Temperature", "minimum_temperature"),
    ],
)
def test_field_name_sentences(label: str, expected: str) -> None:
    assert parse_field_name(label) == expected


def test_field_name_rejects_an_empty_label() -> None:
    result = parse_field_name("(mmHg)")

    assert isinstance(result, Unsupported)
    assert result.rule == "field_name"


@pytest.mark.parametrize("type_text", ["uint8", "sint16", "uint24", "sint32"])
def test_wire_type_accepts_integer_types(type_text: str) -> None:
    assert parse_wire_type(type_text) == WireType(type_text)


@pytest.mark.parametrize(
    "type_text",
    ["boolean[8]", "boolean[16]", "medfloat16", "utf8s", "float32", "gatt_uuid", "uint16[n]"],
)
def test_wire_type_rejects_other_types(type_text: str) -> None:
    result = parse_wire_type(type_text)

    assert isinstance(result, Unsupported)
    assert result.rule == "wire_type"


def test_fixed_size_accepts_the_wire_width() -> None:
    assert parse_fixed_size("2", WireType.SINT16) == 2


@pytest.mark.parametrize("size", ["0 or 4", "variable", "1"])
def test_fixed_size_rejects_variable_and_mismatched_widths(size: str) -> None:
    result = parse_fixed_size(size, WireType.UINT16)

    assert isinstance(result, Unsupported)
    assert result.rule == "fixed_size"


def test_transform_parses_sig_punctuation() -> None:
    plain = parse_transform("Represented values: M = 1, d = -2, b = 0")
    conjunction = parse_transform("M = 1, d = 3, and b = 0")
    spaced = parse_transform("M = 1, d = - 7, b = 0")

    assert plain is not None and not isinstance(plain, Unsupported)
    assert plain.coefficient == 1
    assert plain.decimal_exponent == -2
    assert plain.binary_exponent == 0
    assert conjunction is not None and not isinstance(conjunction, Unsupported)
    assert conjunction.decimal_exponent == 3
    assert spaced is not None and not isinstance(spaced, Unsupported)
    assert spaced.decimal_exponent == -7


def test_absent_transform_uses_identity() -> None:
    assert parse_transform("Base Unit: org.bluetooth.unit.percentage.") is None


def test_transform_rejects_a_partial_sentence() -> None:
    result = parse_transform("M = 1, d = -2")

    assert isinstance(result, Unsupported)
    assert result.rule == "transform"


def test_zero_coefficient_is_a_parsed_transform() -> None:
    parsed = parse_transform("M = 0, d = 0, b = 0")

    assert parsed is not None and not isinstance(parsed, Unsupported)
    assert parsed.coefficient == 0


def test_unit_joins_assigned_numbers() -> None:
    units = {
        CELSIUS: 0x272F,
        "org.bluetooth.unit.percentage": 0x27AD,
    }
    celsius = parse_unit(
        "Base Unit: org.bluetooth.unit.thermodynamic_temperature.degree_celsius",
        units,
    )
    percentage = parse_unit("Base Unit: org.bluetooth.unit.percentage.", units)

    assert celsius is not None and not isinstance(celsius, Unsupported)
    assert celsius.uuid == 0x272F
    assert percentage is not None and not isinstance(percentage, Unsupported)
    assert percentage.identifier == "org.bluetooth.unit.percentage"
    assert percentage.uuid == 0x27AD


def test_unknown_unit_is_unsupported() -> None:
    result = parse_unit("Base Unit: org.bluetooth.unit.not_assigned.", {})

    assert isinstance(result, Unsupported)
    assert result.rule == "unit"


def test_range_sentences_convert_with_integer_arithmetic() -> None:
    temperature = parse_range(
        "Allowed range is: -273.15 to 327.67.",
        coefficient=1,
        decimal_exponent=-2,
        binary_exponent=0,
    )
    battery = parse_range(
        "Allowed range is 0 to 100.",
        coefficient=1,
        decimal_exponent=0,
        binary_exponent=0,
    )
    labelled = parse_range(
        "Range: 1 to 2",
        coefficient=1,
        decimal_exponent=0,
        binary_exponent=0,
    )
    lines = parse_range(
        "Minimum: 0\nMaximum: 65534",
        coefficient=1,
        decimal_exponent=0,
        binary_exponent=0,
    )

    assert temperature == (-27315, 32767)
    assert battery == (0, 100)
    assert labelled == (1, 2)
    assert lines == (0, 65534)


def test_range_rounds_ties_away_from_zero() -> None:
    assert displayed_to_raw("1.5", 1, 0, 0) == 2
    assert displayed_to_raw("-1.5", 1, 0, 0) == -2


def test_range_rejects_missing_text() -> None:
    result = parse_range("No range is declared.", coefficient=1, decimal_exponent=0, binary_exponent=0)

    assert isinstance(result, Unsupported)
    assert result.rule == "range"


def test_temperature_sentinel_is_signed_not_known() -> None:
    parsed = parse_sentinels('A value of 0x8000 represents "value is not known".', WireType.SINT16)

    assert not isinstance(parsed, Unsupported)
    assert parsed[0].raw_value == -32768
    assert parsed[0].meaning is SentinelMeaning.NOT_KNOWN


def test_sentinel_punctuation_variants() -> None:
    curly_single = parse_sentinels(
        "A value of 0xFFFF represents \u2018value is not known\u2019.",
        WireType.UINT16,
    )
    curly_double = parse_sentinels(
        "A value of 127 represents \u201dvalue is not known\u201d.",
        WireType.SINT8,
    )
    ascii_single = parse_sentinels("A value of 0xFF represents 'value is not known'.", WireType.UINT8)
    colon = parse_sentinels("A value of 0xFFFFFF represents: Unknown", WireType.UINT32)
    year = parse_sentinels(
        "In addition to the above range, a special value is defined: 0 = Year is not known",
        WireType.UINT16,
    )

    assert not isinstance(curly_single, Unsupported)
    assert curly_single[0].meaning is SentinelMeaning.NOT_KNOWN
    assert not isinstance(curly_double, Unsupported)
    assert curly_double[0].raw_value == 127
    assert not isinstance(ascii_single, Unsupported)
    assert ascii_single[0].raw_value == 0xFF
    assert not isinstance(colon, Unsupported)
    assert colon[0].raw_value == 0xFFFFFF
    assert colon[0].meaning is SentinelMeaning.NOT_KNOWN
    assert not isinstance(year, Unsupported)
    assert year[0].raw_value == 0
    assert year[0].meaning is SentinelMeaning.NOT_KNOWN


@pytest.mark.parametrize(
    "sentence",
    [
        'The special value of 0xFF for User ID represents "unknown user".',
        "A value of 0xFFFFFE represents: Greater than 0xFFFFFD",
        'A value of 0x007FFFFE represents "NaN".',
    ],
)
def test_sentinel_rejects_meanings_without_a_status(sentence: str) -> None:
    result = parse_sentinels(sentence, WireType.UINT32)

    assert isinstance(result, Unsupported)
    assert result.rule == "sentinel"


def test_prohibited_and_reserved_add_no_ir_kind() -> None:
    prohibited = parse_prohibited("All other values are prohibited.")
    reserved = parse_prohibited("All other values are reserved for future use.")

    assert isinstance(prohibited, OutsideRange)
    assert isinstance(reserved, OutsideRange)


def test_prohibited_rejects_a_hole_inside_the_range() -> None:
    result = parse_prohibited("0x01 is prohibited")

    assert isinstance(result, Unsupported)
    assert result.rule == "prohibited"


def test_struct_reference_names_temperature() -> None:
    sentence = r"Refer to Temperature characteristic in \autoref{sec:org.bluetooth.characteristic.temperature}"

    assert parse_struct_reference(sentence) == TEMPERATURE
    assert copied_field_name("Minimum Temperature", TEMPERATURE) == "minimum"
    assert copied_field_name("Maximum Temperature", TEMPERATURE) == "maximum"


def test_struct_reference_rejects_other_prose() -> None:
    result = parse_struct_reference("See the Temperature characteristic.")

    assert isinstance(result, Unsupported)
    assert result.rule == "struct_ref"

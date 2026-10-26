"""Generator, emitter, and corpus classification."""

from __future__ import annotations

import json
from pathlib import Path

from tools.gss_ir.emit_cpp import emit_characteristics
from tools.gss_ir.generate import generate_characteristics
from tools.gss_ir.normalise import Unsupported, iter_characteristic_paths, normalise_identifier, normalise_path
from tools.gss_ir.normalise.special_cases import special_cases
from tools.gss_ir.normalise.wire_type import integer_domain
from tools.gss_ir.v1 import ValueSet, WireType

ROOT = Path(__file__).resolve().parents[3]
CHARACTERISTICS = ROOT / "tools/gss_ir/characteristics.json"
SPECIAL_CASES = ROOT / "tools/gss_ir/special_cases.json"
_SPECIAL_CASE_RULES = {
    "org.bluetooth.characteristic.cgm_measurement": "struct_ref",
    "org.bluetooth.characteristic.chromaticity_coordinate": "range",
    "org.bluetooth.characteristic.cooking_conditions": "characteristic_uuid",
    "org.bluetooth.characteristic.cooking_zone_perceived_power": "characteristic_uuid",
    "org.bluetooth.characteristic.cosine_of_the_angle": "range",
    "org.bluetooth.characteristic.ieee_11073-20601_regulatory_certification_data_list": "struct_ref",
    "org.bluetooth.characteristic.object_type": "wire_type",
    "org.bluetooth.characteristic.preferred_units": "wire_type",
    "org.bluetooth.characteristic.time_exponential_8": "range",
    "org.bluetooth.characteristic.udi_for_medical_devices": "utf8",
    "org.bluetooth.characteristic.volume_flow": "range",
}


def test_temperature_type_is_an_enumeration() -> None:
    result = normalise_identifier("org.bluetooth.characteristic.temperature_type")

    assert not isinstance(result, Unsupported)
    field = result.fields[0]
    assert field.value_set is ValueSet.ENUMERATION
    assert ("armpit", 1) in {(item.name, item.value) for item in field.enumerators}
    assert all(item.value <= 9 for item in field.enumerators)


def test_glucose_feature_bits_are_single_bit_flags() -> None:
    result = normalise_identifier("org.bluetooth.characteristic.glucose_feature")

    assert not isinstance(result, Unsupported)
    field = result.fields[0]
    assert field.value_set is ValueSet.FLAGS
    assert field.minimum == 0
    assert field.maximum == 0xFFFF
    masks = {item.value for item in field.enumerators}
    assert 1 in masks
    assert all(mask & (mask - 1) == 0 for mask in masks)
    assert all(mask < (1 << 11) for mask in masks)


def test_packed_bit_group_stays_an_integer() -> None:
    result = normalise_identifier("org.bluetooth.characteristic.weight_scale_feature")

    assert not isinstance(result, Unsupported)
    assert result.fields[0].value_set is None


def test_glucose_feature_boolean_uses_the_full_bit_domain() -> None:
    result = normalise_identifier("org.bluetooth.characteristic.glucose_feature")

    assert not isinstance(result, Unsupported)
    assert len(result.fields) == 1
    field = result.fields[0]
    assert field.wire_type is WireType.BOOLEAN16
    assert field.minimum == 0
    assert field.maximum == 0xFFFF


def test_location_and_speed_stops_on_variable_size() -> None:
    result = normalise_identifier("org.bluetooth.characteristic.location_and_speed")

    assert isinstance(result, Unsupported)
    assert result.rule == "fixed_size"


def test_last_name_is_a_variable_utf8_value() -> None:
    result = normalise_identifier("org.bluetooth.characteristic.last_name")

    assert not isinstance(result, Unsupported)
    assert len(result.fields) == 1
    field = result.fields[0]
    assert field.wire_type is WireType.UTF8
    assert field.utf8_capacity is None
    assert field.minimum == 0
    assert field.maximum == 0


def test_fixed_string_capacity_is_the_type_parameter() -> None:
    eight = normalise_identifier("org.bluetooth.characteristic.fixed_string_8")
    sixteen = normalise_identifier("org.bluetooth.characteristic.fixed_string_16")

    assert not isinstance(eight, Unsupported)
    assert eight.fields[0].utf8_capacity == 8
    assert not isinstance(sixteen, Unsupported)
    assert sixteen.fields[0].utf8_capacity == 16


def test_subbyte_status_fields_keep_their_bit_width() -> None:
    contact = normalise_identifier("org.bluetooth.characteristic.contact_status_8")
    button = normalise_identifier("org.bluetooth.characteristic.pushbutton_status_8")

    assert not isinstance(contact, Unsupported)
    assert len(contact.fields) == 8
    assert {field.wire_type for field in contact.fields} == {WireType.UINT1}
    assert contact.fields[0].minimum == 0
    assert contact.fields[0].maximum == 1
    assert not isinstance(button, Unsupported)
    assert len(button.fields) == 4
    assert {field.wire_type for field in button.fields} == {WireType.UINT2}
    assert button.fields[0].maximum == 3


def test_object_name_capacity_is_the_stated_maximum() -> None:
    result = normalise_identifier("org.bluetooth.characteristic.object_name")

    assert not isinstance(result, Unsupported)
    assert result.fields[0].utf8_capacity == 120


def test_one_off_string_size_and_named_gaps_stay_unsupported() -> None:
    object_type = normalise_identifier("org.bluetooth.characteristic.object_type")
    preferred = normalise_identifier("org.bluetooth.characteristic.preferred_units")
    cooking = normalise_identifier("org.bluetooth.characteristic.cooking_conditions")
    zone = normalise_identifier("org.bluetooth.characteristic.cooking_zone_perceived_power")

    assert isinstance(object_type, Unsupported)
    assert object_type.rule == "wire_type"
    assert isinstance(preferred, Unsupported)
    assert preferred.rule == "wire_type"
    assert isinstance(cooking, Unsupported)
    assert cooking.rule == "characteristic_uuid"
    assert isinstance(zone, Unsupported)
    assert zone.rule == "characteristic_uuid"


def test_special_cases_stay_unsupported_and_match_the_list() -> None:
    recorded = json.loads(SPECIAL_CASES.read_text(encoding="utf-8"))

    assert {item["identifier"]: item["rule"] for item in recorded} == _SPECIAL_CASE_RULES
    assert list(special_cases(ROOT)) == recorded
    for identifier, rule in _SPECIAL_CASE_RULES.items():
        result = normalise_identifier(identifier)
        assert isinstance(result, Unsupported)
        assert result.rule == rule


def test_passing_integer_endpoints_fit_the_wire() -> None:
    outside = (
        "org.bluetooth.characteristic.chromaticity_coordinate",
        "org.bluetooth.characteristic.volume_flow",
    )
    for identifier in outside:
        result = normalise_identifier(identifier)
        assert isinstance(result, Unsupported)
        assert result.rule == "range"

    for path in iter_characteristic_paths(ROOT):
        result = normalise_path(path, root=ROOT)
        if isinstance(result, Unsupported):
            continue
        for field in result.fields:
            span = integer_domain(field.wire_type)
            if span is None:
                continue
            low, high = span
            assert low <= field.minimum <= field.maximum <= high


def test_regeneration_is_deterministic(tmp_path: Path) -> None:
    first_ir = generate_characteristics(CHARACTERISTICS, root=ROOT, output_root=tmp_path / "first")
    second_ir = generate_characteristics(CHARACTERISTICS, root=ROOT, output_root=tmp_path / "second")
    first_cpp = emit_characteristics(CHARACTERISTICS, root=ROOT, output_root=tmp_path / "first")
    second_cpp = emit_characteristics(CHARACTERISTICS, root=ROOT, output_root=tmp_path / "second")

    assert first_ir == second_ir
    assert first_cpp == second_cpp


def test_blacklist_is_skipped_and_failures_are_recorded(tmp_path: Path) -> None:
    blacklist = tmp_path / "blacklist.json"
    blacklist.write_text(json.dumps(["org.bluetooth.characteristic.temperature"]), encoding="utf-8")

    generated = generate_characteristics(blacklist, root=ROOT, output_root=tmp_path / "out")

    assert "generated/ir/1/org.bluetooth.characteristic.temperature.json" not in generated
    errors = json.loads(generated["generated/errors.json"])
    recorded = {item["identifier"] for item in errors}
    assert "org.bluetooth.characteristic.temperature" not in recorded
    assert "org.bluetooth.characteristic.location_and_speed" in recorded
    assert "org.bluetooth.characteristic.battery_level" not in recorded


def test_emitted_code_calls_the_handwritten_codec(tmp_path: Path) -> None:
    generated = generate_characteristics(CHARACTERISTICS, root=ROOT, output_root=tmp_path)
    emitted = emit_characteristics(CHARACTERISTICS, root=ROOT, output_root=tmp_path)
    ir_paths = [path for path in generated if path.startswith("generated/ir/")]
    cpp_paths = [path for path in emitted if path.endswith(".cpp")]
    assert len(ir_paths) >= 30
    assert len(cpp_paths) == len(ir_paths)
    for path in cpp_paths:
        text = emitted[path].decode()
        assert "btsig::decode(" in text
        assert "btsig::encode(" in text
        assert "virtual " not in text
        assert all(len(line) <= 120 for line in text.splitlines())

    source = emitted["btsig/generated/temperature/src/temperature.cpp"].decode()
    header = emitted["btsig/generated/temperature/include/btsig/temperature.h"].decode()
    range_header = emitted["btsig/generated/temperature_range/include/btsig/temperature_range.h"].decode()

    assert "btsig::decode(" in source
    assert "btsig::encode(" in source
    assert "Temperature::decode" in source
    assert "catalog" not in source
    assert "virtual " not in source
    assert "pow(" not in source
    assert "0.01" not in source
    assert "-32768" in source
    assert "-27315" in source
    assert "32767" in source
    assert "static_assert" in source
    assert "btsig_decode_temperature" in header
    assert "btsig_encode_temperature" in header
    assert "typedef struct btsig_temperature " in header
    assert "double temperature" in header
    assert "btsig_decode_temperature_range" in range_header
    assert "double minimum" in range_header
    assert "double maximum" in range_header
    last_name = emitted["btsig/generated/last_name/include/btsig/last_name.h"].decode()
    last_name_hpp = emitted["btsig/generated/last_name/include/btsig/last_name.hpp"].decode()
    fixed_string = emitted["btsig/generated/fixed_string_16/include/btsig/fixed_string_16.h"].decode()
    object_name = emitted["btsig/generated/object_name/include/btsig/object_name.h"].decode()
    assert "uint16_t size;" in last_name
    assert "uint8_t data[512];" in last_name
    assert "last_name_length" not in last_name
    assert "btsig::utf8_text<512> last_name;" in last_name_hpp
    assert "struct LastName {" in last_name_hpp
    assert "uint16_t size;" in fixed_string
    assert "uint8_t data[16];" in fixed_string
    assert "uint8_t data[120];" in object_name
    temperature_type = emitted["btsig/generated/temperature_type/include/btsig/temperature_type.hpp"].decode()
    temperature_type_c = emitted["btsig/generated/temperature_type/include/btsig/temperature_type.h"].decode()
    glucose = emitted["btsig/generated/glucose_feature/include/btsig/glucose_feature.hpp"].decode()
    assert "enum class TemperatureTypeDescription : int" in temperature_type
    assert "armpit = 1" in temperature_type
    assert "operator|" not in temperature_type
    assert "enum btsig_temperature_type_description {" in temperature_type_c
    assert "typedef uint" not in temperature_type_c
    assert "typedef enum" not in temperature_type_c
    assert "BTSIG_TEMPERATURE_TYPE_DESCRIPTION_ARMPIT = 1" in temperature_type_c
    assert "enum btsig_temperature_type_description temperature_type_description" in temperature_type_c
    glucose_c = emitted["btsig/generated/glucose_feature/include/btsig/glucose_feature.h"].decode()
    assert "enum class GlucoseFeatureValue : std::uint32_t" in glucose
    assert "enum btsig_glucose_feature_value {" in glucose_c
    assert "BTSIG_GLUCOSE_FEATURE_VALUE_LOW_BATTERY_DETECTION_DURING_MEASUREMENT = 1U << 0" in glucose_c
    assert "operator|" in glucose
    assert "operator&" in glucose
    assert "operator~" in glucose
    assert "1U << 0" in glucose
    assert "1U << 11" not in glucose
    assert source.startswith("// Generated by `python -m tools.gss_ir.emit_cpp ")
    assert "Do not edit." in source

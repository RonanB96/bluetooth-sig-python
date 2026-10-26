"""SIG YAML readers return raw text and assigned numbers."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.gss_ir.sources.characteristic_uuids import read_characteristic_records, read_characteristic_uuids
from tools.gss_ir.sources.dp import read_device_properties
from tools.gss_ir.sources.errors import GssSourceError
from tools.gss_ir.sources.gss import read_characteristic
from tools.gss_ir.sources.unit_uuids import read_unit_uuids

ROOT = Path(__file__).resolve().parents[3]


def test_gss_reader_keeps_raw_temperature_strings() -> None:
    path = ROOT / "bluetooth_sig/gss/org.bluetooth.characteristic.temperature.yaml"
    characteristic = read_characteristic(path, source_path=path.relative_to(ROOT).as_posix())
    field = characteristic.fields[0]

    assert characteristic.identifier == "org.bluetooth.characteristic.temperature"
    assert field.field == "Temperature"
    assert field.type_text == "sint16"
    assert field.size == "2"
    assert "M = 1, d = -2, b = 0" in field.description


def test_gss_reader_keeps_raw_enumeration_entries() -> None:
    path = ROOT / "bluetooth_sig/gss/org.bluetooth.characteristic.temperature_type.yaml"
    characteristic = read_characteristic(path, source_path=path.relative_to(ROOT).as_posix())
    table = characteristic.value_tables[0]
    entry = table.entries[1]

    assert table.name == "Temperature Type Description"
    assert entry.kind == "value"
    assert entry.raw == "1"
    assert entry.description == "Armpit"


def test_characteristic_uuid_reader_maps_the_pilot() -> None:
    table = read_characteristic_uuids(ROOT / "bluetooth_sig/assigned_numbers/uuids/characteristic_uuids.yaml")

    assert table["org.bluetooth.characteristic.battery_level"] == 0x2A19
    assert table["org.bluetooth.characteristic.temperature"] == 0x2A6E
    assert table["org.bluetooth.characteristic.temperature_range"] == 0x2B10


def test_characteristic_records_keep_the_display_name() -> None:
    records = read_characteristic_records(ROOT / "bluetooth_sig/assigned_numbers/uuids/characteristic_uuids.yaml")
    by_id = {record.identifier: record for record in records}

    assert len(records) == 502
    assert by_id["org.bluetooth.characteristic.gap.device_name"].name == "Device Name"
    assert by_id["org.bluetooth.characteristic.gap.device_name"].uuid == 0x2A00
    assert by_id["org.bluetooth.characteristic.battery_level"].name == "Battery Level"


def test_device_property_reader_names_characteristics() -> None:
    properties = read_device_properties(ROOT / "bluetooth_sig/dp/properties")
    by_id = {prop.identifier: prop for prop in properties}

    assert by_id["org.bluetooth.property.wind_chill"].characteristics == ("org.bluetooth.characteristic.wind_chill",)
    assert by_id["org.bluetooth.property.subsensor_weights_5"].characteristics == (
        "org.bluetooth.characteristic.percentage_8_steps",
        "org.bluetooth.characteristic.percentage_8",
    )


def test_device_property_reader_rejects_a_missing_characteristic(tmp_path: Path) -> None:
    document = "\n".join(
        (
            "property:",
            "  identifier: org.bluetooth.property.example",
            "  name: Example",
            "  group: org.bluetooth.property_group.example",
        )
    )
    (tmp_path / "org.bluetooth.property.example.yaml").write_text(document, encoding="utf-8")

    with pytest.raises(GssSourceError) as error:
        read_device_properties(tmp_path)

    assert "characteristic" in error.value.detail


def test_unit_uuid_reader_maps_celsius_and_percentage() -> None:
    table = read_unit_uuids(ROOT / "bluetooth_sig/assigned_numbers/uuids/units.yaml")

    assert table["org.bluetooth.unit.thermodynamic_temperature.degree_celsius"] == 0x272F
    assert table["org.bluetooth.unit.percentage"] == 0x27AD

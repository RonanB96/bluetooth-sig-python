"""SIG YAML readers return raw text and assigned numbers."""

from __future__ import annotations

from pathlib import Path

from tools.gss_ir.sources.characteristic_uuids import read_characteristic_uuids
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


def test_unit_uuid_reader_maps_celsius_and_percentage() -> None:
    table = read_unit_uuids(ROOT / "bluetooth_sig/assigned_numbers/uuids/units.yaml")

    assert table["org.bluetooth.unit.thermodynamic_temperature.degree_celsius"] == 0x272F
    assert table["org.bluetooth.unit.percentage"] == 0x27AD

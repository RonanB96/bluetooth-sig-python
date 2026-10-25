"""Golden IR for the pilot characteristics."""

from __future__ import annotations

from tools.gss_ir.normalise import Unsupported, normalise_identifier
from tools.gss_ir.v1 import (
    IrDocument,
    Provenance,
    ScalarField,
    Sentinel,
    SentinelMeaning,
    Transform,
    UnitRef,
    WireType,
    encode_ir,
)


def _temperature_field(name: str) -> ScalarField:
    return ScalarField(
        name=name,
        wire_type=WireType.SINT16,
        minimum=-27315,
        maximum=32767,
        transform=Transform(decimal_exponent=-2),
        unit=UnitRef(
            identifier="org.bluetooth.unit.thermodynamic_temperature.degree_celsius",
            uuid=0x272F,
        ),
        sentinels=(Sentinel(raw_value=-32768, meaning=SentinelMeaning.NOT_KNOWN),),
    )


def _expect(identifier: str, uuid: int, fields: tuple[ScalarField, ...]) -> bytes:
    document = IrDocument(
        schema_version=1,
        identifier=identifier,
        uuid=uuid,
        provenance=Provenance(
            source_path=f"bluetooth_sig/gss/{identifier}.yaml",
            source_identifier=identifier,
        ),
        fields=fields,
    )
    return encode_ir(document)


def test_battery_level_ir() -> None:
    result = normalise_identifier("org.bluetooth.characteristic.battery_level")

    assert not isinstance(result, Unsupported)
    assert encode_ir(result) == _expect(
        "org.bluetooth.characteristic.battery_level",
        0x2A19,
        (
            ScalarField(
                name="battery_level",
                wire_type=WireType.UINT8,
                minimum=0,
                maximum=100,
                unit=UnitRef(identifier="org.bluetooth.unit.percentage", uuid=0x27AD),
            ),
        ),
    )


def test_temperature_ir() -> None:
    result = normalise_identifier("org.bluetooth.characteristic.temperature")

    assert not isinstance(result, Unsupported)
    assert encode_ir(result) == _expect(
        "org.bluetooth.characteristic.temperature",
        0x2A6E,
        (_temperature_field("temperature"),),
    )


def test_temperature_range_copies_two_scalars() -> None:
    result = normalise_identifier("org.bluetooth.characteristic.temperature_range")

    assert not isinstance(result, Unsupported)
    encoded = encode_ir(result)
    assert encoded == _expect(
        "org.bluetooth.characteristic.temperature_range",
        0x2B10,
        (
            _temperature_field("minimum"),
            _temperature_field("maximum"),
        ),
    )
    assert b"struct_ref" not in encoded

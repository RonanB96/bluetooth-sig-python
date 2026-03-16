"""Tests for characteristic role classification.

Verifies that :attr:`BaseCharacteristic.role` assigns the correct
:class:`CharacteristicRole` based on SIG spec metadata (name patterns,
value_type, unit presence, and GSS field structure).

Also tests :func:`classify_role` directly for edge-case coverage of the
multi-field struct detection path.
"""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.gatt.characteristics.role_classifier import (
    _spec_has_unit_fields,
    _spec_is_multi_field_measurement,
    classify_role,
)
from bluetooth_sig.types.gatt_enums import CharacteristicRole
from bluetooth_sig.types.registry.common import CharacteristicSpec
from bluetooth_sig.types.registry.gss_characteristic import FieldSpec
from bluetooth_sig.types.uuid import BluetoothUUID

# ---------------------------------------------------------------------------
# Helper — instantiate a registered characteristic by its SIG name
# ---------------------------------------------------------------------------


def _get_char(sig_name: str) -> BaseCharacteristic:  # type: ignore[type-arg]
    """Return an instance of the characteristic registered under *sig_name*.

    Raises ``KeyError`` if the name is not in the registry.
    """
    chars = CharacteristicRegistry.get_all_characteristics()
    for name_enum, cls in chars.items():
        display = name_enum.value if hasattr(name_enum, "value") else str(name_enum)
        if display == sig_name:
            return cls()
    raise KeyError(f"{sig_name!r} not found in CharacteristicRegistry")


# ---------------------------------------------------------------------------
# MEASUREMENT — numeric / structured data with physical units
# ---------------------------------------------------------------------------


class TestMeasurementRole:
    """Characteristics that carry sensor data should be classified MEASUREMENT."""

    @pytest.mark.parametrize(
        "sig_name",
        [
            # Rule 3: name contains "Measurement"
            "Temperature Measurement",
            "Heart Rate Measurement",
            "Blood Pressure Measurement",
            "Weight Measurement",
            "CSC Measurement",
            # Rule 4: numeric scalar with a unit
            "Temperature",
            "Humidity",
            "Pressure",
            "Acceleration",
            "Elevation",
            # Rule 5: multi-field struct with per-field units
            "Location and Speed",
            "Navigation",
            "Activity Goal",
            # Rule 6: compound type
            "Acceleration 3D",
            "Appearance",
            "PnP ID",
            "System ID",
        ],
    )
    def test_measurement_characteristics(self, sig_name: str) -> None:
        char = _get_char(sig_name)
        assert char.role == CharacteristicRole.MEASUREMENT, (
            f"{sig_name} expected MEASUREMENT, got {char.role.value}"
            f" (python_type={char.python_type}, unit={char.unit!r})"
        )

    def test_measurement_interval_by_name(self) -> None:
        """'Measurement Interval' matches the name rule even though it could
        also match numeric-with-unit.
        """
        char = _get_char("Measurement Interval")
        assert char.role == CharacteristicRole.MEASUREMENT


# ---------------------------------------------------------------------------
# CONTROL — write-only control points
# ---------------------------------------------------------------------------


class TestControlRole:
    """Control Point characteristics should be classified CONTROL."""

    @pytest.mark.parametrize(
        "sig_name",
        [
            "Heart Rate Control Point",
            "Cycling Power Control Point",
            "Bond Management Control Point",
            "Alert Notification Control Point",
            "LN Control Point",
            "Time Update Control Point",
            "HID Control Point",
        ],
    )
    def test_control_point_characteristics(self, sig_name: str) -> None:
        char = _get_char(sig_name)
        assert char.role == CharacteristicRole.CONTROL


# ---------------------------------------------------------------------------
# FEATURE — capability bitfields
# ---------------------------------------------------------------------------


class TestFeatureRole:
    """Feature / capability bitfield characteristics should be FEATURE."""

    @pytest.mark.parametrize(
        "sig_name",
        [
            "Blood Pressure Feature",
            "Body Composition Feature",
            "Bond Management Feature",
            "CSC Feature",
            "Cycling Power Feature",
            "Glucose Feature",
            "LN Feature",
            "RSC Feature",
            "Weight Scale Feature",
        ],
    )
    def test_feature_characteristics(self, sig_name: str) -> None:
        char = _get_char(sig_name)
        assert char.role == CharacteristicRole.FEATURE


# ---------------------------------------------------------------------------
# STATUS — state / enum reporting
# ---------------------------------------------------------------------------


class TestStatusRole:
    """Status reporting characteristics should be classified STATUS."""

    @pytest.mark.parametrize(
        "sig_name",
        [
            "Alert Status",
            "Unread Alert Status",
            "Battery Level Status",
            "Battery Critical Status",
            "Acceleration Detection Status",
        ],
    )
    def test_status_characteristics(self, sig_name: str) -> None:
        char = _get_char(sig_name)
        assert char.role == CharacteristicRole.STATUS


# ---------------------------------------------------------------------------
# INFO — static metadata strings
# ---------------------------------------------------------------------------


class TestInfoRole:
    """String metadata characteristics should be classified INFO."""

    @pytest.mark.parametrize(
        "sig_name",
        [
            "Device Name",
            "Firmware Revision String",
            "Hardware Revision String",
            "Software Revision String",
            "Manufacturer Name String",
            "Model Number String",
            "Serial Number String",
            "Email Address",
            "First Name",
            "Last Name",
        ],
    )
    def test_info_characteristics(self, sig_name: str) -> None:
        char = _get_char(sig_name)
        assert char.role == CharacteristicRole.INFO


# ---------------------------------------------------------------------------
# Classification priority — earlier rules win over later ones
# ---------------------------------------------------------------------------


class TestRolePriority:
    """Verify that the priority ordering resolves ambiguity correctly."""

    def test_control_point_beats_measurement_name(self) -> None:
        """A hypothetical 'Measurement Control Point' would be CONTROL,
        not MEASUREMENT, because rule 1 fires before rule 3.
        Verified via Heart Rate Control Point (INT, no unit).
        """
        char = _get_char("Heart Rate Control Point")
        assert char.role == CharacteristicRole.CONTROL

    def test_feature_bitfield_type_beats_unknown(self) -> None:
        """A BITFIELD value_type triggers FEATURE even without 'Feature'
        in the name.
        """
        char = _get_char("Body Composition Feature")
        assert char.is_bitfield
        assert char.role == CharacteristicRole.FEATURE


# ---------------------------------------------------------------------------
# UNKNOWN — characteristics that cannot be classified from metadata alone
# ---------------------------------------------------------------------------


class TestUnknownRole:
    """Characteristics with insufficient metadata remain UNKNOWN."""

    @pytest.mark.parametrize(
        "sig_name",
        [
            "Alert Level",  # INT, no unit, no matching name pattern
            "Boolean",  # BOOL, no unit
        ],
    )
    def test_unknown_characteristics(self, sig_name: str) -> None:
        char = _get_char(sig_name)
        assert char.role == CharacteristicRole.UNKNOWN


# ---------------------------------------------------------------------------
# Property semantics — caching, type
# ---------------------------------------------------------------------------


class TestRolePropertySemantics:
    """Verify that the role property behaves correctly as a cached_property."""

    def test_role_returns_enum_member(self) -> None:
        char = _get_char("Temperature")
        assert isinstance(char.role, CharacteristicRole)

    def test_role_is_cached(self) -> None:
        """Accessing role twice should return the same object (cached)."""
        char = _get_char("Temperature")
        first = char.role
        second = char.role
        assert first is second

    def test_all_roles_are_valid_enum_members(self) -> None:
        """Every registered characteristic should return a valid
        CharacteristicRole member.
        """
        chars = CharacteristicRegistry.get_all_characteristics()
        for _name_enum, cls in chars.items():
            inst = cls()
            assert isinstance(inst.role, CharacteristicRole), (
                f"{inst.name} returned {type(inst.role)} instead of CharacteristicRole"
            )


# ---------------------------------------------------------------------------
# Helpers for building synthetic specs
# ---------------------------------------------------------------------------

_DUMMY_UUID = BluetoothUUID("00002a37-0000-1000-8000-00805f9b34fb")


def _make_field(
    name: str = "Value",
    data_type: str = "uint16",
    size: str = "2",
    description: str = "",
) -> FieldSpec:
    """Build a minimal FieldSpec for testing."""
    return FieldSpec(field=name, type=data_type, size=size, description=description)


def _make_spec(fields: list[FieldSpec]) -> CharacteristicSpec:
    """Build a CharacteristicSpec with the given field list."""
    return CharacteristicSpec(
        uuid=_DUMMY_UUID,
        name="Test Characteristic",
        structure=fields,
    )


# ---------------------------------------------------------------------------
# Direct classify_role() tests — multi-field struct detection
# ---------------------------------------------------------------------------


class TestClassifyRoleMultiField:
    """Direct tests for classify_role() covering the multi-field struct path."""

    def test_multi_field_with_unit_fields_is_measurement(self) -> None:
        """A multi-field spec with per-field units → MEASUREMENT,
        even with python_type=None and unit=''.
        """
        spec = _make_spec([
            _make_field("Heart Rate", description="Unit: org.bluetooth.unit.period.beats_per_minute"),
            _make_field("Energy Expended", description="Unit: org.bluetooth.unit.energy.joule"),
        ])
        result = classify_role("Some Sensor", None, False, "", spec)
        assert result == CharacteristicRole.MEASUREMENT

    def test_multi_field_without_units_is_not_measurement(self) -> None:
        """A multi-field spec where NO field has a unit_id should not
        trigger the multi-field measurement rule.
        """
        spec = _make_spec([
            _make_field("Flags", description="Flags field"),
            _make_field("Opcode", description="Control opcode"),
        ])
        result = classify_role("Some Thing", None, False, "", spec)
        assert result == CharacteristicRole.UNKNOWN

    def test_single_field_with_unit_does_not_trigger_multi_field_rule(self) -> None:
        """A single-field spec should not be matched by the multi-field rule;
        it falls through to other heuristics.
        """
        spec = _make_spec([
            _make_field("Temperature", description="Unit: org.bluetooth.unit.thermodynamic_temperature.degree_celsius"),
        ])
        # With python_type=None and unit='', rule 4 doesn't fire,
        # rule 5 requires >1 field → falls to UNKNOWN
        result = classify_role("Custom Temp", None, False, "", spec)
        assert result == CharacteristicRole.UNKNOWN

    def test_multi_field_with_python_type_none(self) -> None:
        """After the python_type pollution fix, multi-field chars arrive
        with python_type=None. Should still be MEASUREMENT via rule 5.
        """
        spec = _make_spec([
            _make_field("Speed", description="Unit: org.bluetooth.unit.velocity.metres_per_second"),
            _make_field("Distance", description="Unit: org.bluetooth.unit.length.metre"),
            _make_field("Position Status", description="Status flags"),
        ])
        result = classify_role("Location and Speed", None, False, "", spec)
        assert result == CharacteristicRole.MEASUREMENT

    def test_name_based_rule_takes_priority_over_multi_field(self) -> None:
        """Rule 3 ('Measurement' in name) fires before rule 5."""
        spec = _make_spec([
            _make_field("Systolic", description="Unit: org.bluetooth.unit.pressure.pascal"),
            _make_field("Diastolic", description="Unit: org.bluetooth.unit.pressure.pascal"),
        ])
        result = classify_role("Blood Pressure Measurement", None, False, "", spec)
        assert result == CharacteristicRole.MEASUREMENT


# ---------------------------------------------------------------------------
# Direct tests for spec helper functions
# ---------------------------------------------------------------------------


class TestSpecHelpers:
    """Tests for _spec_is_multi_field_measurement and _spec_has_unit_fields."""

    def test_spec_is_multi_field_none_spec(self) -> None:
        assert _spec_is_multi_field_measurement(None) is False

    def test_spec_is_multi_field_empty_structure(self) -> None:
        spec = _make_spec([])
        assert _spec_is_multi_field_measurement(spec) is False

    def test_spec_is_multi_field_single_field(self) -> None:
        spec = _make_spec([
            _make_field("Temp", description="Unit: org.bluetooth.unit.thermodynamic_temperature.degree_celsius"),
        ])
        assert _spec_is_multi_field_measurement(spec) is False

    def test_spec_is_multi_field_two_fields_with_units(self) -> None:
        spec = _make_spec([
            _make_field("HR", description="Unit: org.bluetooth.unit.period.beats_per_minute"),
            _make_field("Energy", description="Unit: org.bluetooth.unit.energy.joule"),
        ])
        assert _spec_is_multi_field_measurement(spec) is True

    def test_spec_is_multi_field_two_fields_no_units(self) -> None:
        spec = _make_spec([
            _make_field("Flags", description="Flags field"),
            _make_field("Value", description="Some value"),
        ])
        assert _spec_is_multi_field_measurement(spec) is False

    def test_spec_has_unit_fields_none_spec(self) -> None:
        assert _spec_has_unit_fields(None) is False

    def test_spec_has_unit_fields_with_unit(self) -> None:
        spec = _make_spec([
            _make_field("Temp", description="Unit: org.bluetooth.unit.thermodynamic_temperature.degree_celsius"),
        ])
        assert _spec_has_unit_fields(spec) is True

    def test_spec_has_unit_fields_without_unit(self) -> None:
        spec = _make_spec([
            _make_field("Flags", description="Control flags"),
        ])
        assert _spec_has_unit_fields(spec) is False

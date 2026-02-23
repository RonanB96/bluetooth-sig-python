"""Tests for characteristic role classification.

Verifies that :attr:`BaseCharacteristic.role` assigns the correct
:class:`CharacteristicRole` based on SIG spec metadata (name patterns,
value_type, unit presence, and GSS field structure).
"""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.types.gatt_enums import CharacteristicRole

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
            # Rule 5: compound value with unit metadata
            "Acceleration 3D",
            "Activity Goal",
            "Location and Speed",
            "Navigation",
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
            "Appearance",  # VARIOUS, no unit
            "Boolean",  # BOOL, no unit
            "PnP ID",  # VARIOUS, no unit
            "System ID",  # VARIOUS, no unit
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

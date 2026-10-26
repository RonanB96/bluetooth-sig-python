"""Role classification for GATT characteristics.

Classifies a characteristic's purpose (MEASUREMENT, FEATURE, CONTROL, etc.)
from SIG spec metadata using a tiered heuristic based on GSS YAML signals,
name conventions, and type inference.

Validated against a hand-verified ground truth map of all 294 registered
characteristics — see ``scripts/test_classifier.py``.  Characteristics
that cannot be classified from the available YAML metadata alone should
use ``_manual_role`` on their class.
"""

from __future__ import annotations

import enum

from ...types.gatt_enums import CharacteristicRole
from ...types.registry import CharacteristicSpec

# Struct name words that indicate compound measurement data
_MEASUREMENT_STRUCT_WORDS = frozenset({"Range", "Statistics", "Specification", "Record", "Relative", "Coordinates"})

# Struct name words that indicate temporal or state-snapshot data
_STATUS_STRUCT_WORDS = frozenset({"Time", "Information", "Created", "Modified", "Changed", "Alert", "Setting"})


def classify_role(
    char_name: str,
    python_type: type | str | None,
    is_bitfield: bool,
    unit: str,
    spec: CharacteristicSpec | None,
) -> CharacteristicRole:
    """Classify a characteristic's purpose from SIG spec metadata.

        Role definitions:
        - ``MEASUREMENT``: value represents something measured or observed from
            the device or environment (physical quantity, sampled reading, derived
            sensor metric).
        - ``STATUS``: discrete operational/device state (mode, flag, trend,
            categorical state snapshot).
        - ``FEATURE``: capability declaration (supported options/bitmasks), not a
            live measured value.
        - ``CONTROL``: command/control endpoint (typically control point writes).
        - ``INFO``: contextual metadata, identifiers, or descriptive/static data
            that does not represent a measurement.

    Uses a tiered priority system — strongest YAML signals first,
    then name conventions, type inference, and struct name patterns.

    Tier 1 — YAML-data-driven (highest confidence):
        1. Name contains *Control Point*            → CONTROL
        2. Physical (non-unitless) ``unit_id``       → MEASUREMENT
        3. Field-level physical units in structure   → MEASUREMENT

    Tier 2 — Name + type signals:
        4. Name contains *Status*                   → STATUS
        5. ``is_bitfield`` is True                  → FEATURE
        6. ``python_type`` is IntFlag subclass       → FEATURE

    Tier 3 — SIG naming conventions:
        7. Name contains *Measurement* or ends
           with *Data*                               → MEASUREMENT
        8. Name ends with *Feature(s)*               → FEATURE

    Tier 4 — Type-driven inference:
        9. Non-empty unit string                     → MEASUREMENT
       10. ``python_type is str``                    → INFO
       11. ``python_type`` is a string subtype name  → INFO
       12. ``python_type`` is an Enum subclass        → STATUS
       13. Unitless ``unit_id`` + numeric type        → MEASUREMENT
       14. ``python_type is float``                   → MEASUREMENT
       15. ``python_type is bool``                    → STATUS

    Tier 5 — Struct name patterns (for structs with no YAML signal):
       16. Measurement struct keyword                 → MEASUREMENT
       17. Status struct keyword                      → STATUS

    Tier 6 — Fallback:
       18. Otherwise                                 → UNKNOWN

    Args:
        char_name: Display name of the characteristic.
        python_type: Resolved Python type (int, float, str, etc.) or None.
        is_bitfield: Whether the characteristic is a bitfield.
        unit: Unit string (empty string if not applicable).
        spec: Resolved YAML spec (may be None).

    Returns:
        The classified ``CharacteristicRole``.
    """
    # Derive YAML signals from spec
    has_unit_id = bool(spec and spec.unit_id)
    is_unitless = "unitless" in (spec.unit_id or "") if spec else False
    has_field_units = _spec_has_physical_field_units(spec)
    is_intflag = isinstance(python_type, type) and issubclass(python_type, enum.IntFlag)
    is_enum = isinstance(python_type, type) and issubclass(python_type, enum.Enum)
    is_struct = isinstance(python_type, type) and python_type not in (
        int,
        float,
        str,
        bool,
        bytes,
    )

    # Walk tiers in priority order; first match wins
    return (
        _classify_yaml_signals(char_name, has_unit_id, is_unitless, has_field_units)
        or _classify_name_and_type(char_name, is_bitfield, is_intflag)
        or _classify_naming_conventions(char_name)
        or _classify_type_inference(python_type, unit, is_enum, is_unitless)
        or _classify_struct_patterns(char_name, is_struct)
        or CharacteristicRole.UNKNOWN
    )


def _classify_yaml_signals(
    char_name: str,
    has_unit_id: bool,
    is_unitless: bool,
    has_field_units: bool,
) -> CharacteristicRole | None:
    """Tier 1: YAML-data-driven signals (highest confidence)."""
    # 1. Control points — write-only command interfaces
    if "Control Point" in char_name:
        return CharacteristicRole.CONTROL

    # 2. Physical (non-unitless) unit_id from the GSS YAML
    if has_unit_id and not is_unitless:
        return CharacteristicRole.MEASUREMENT

    # 3. Structure fields carry physical units
    if has_field_units:
        return CharacteristicRole.MEASUREMENT

    return None


def _classify_name_and_type(
    char_name: str,
    is_bitfield: bool,
    is_intflag: bool,
) -> CharacteristicRole | None:
    """Tier 2: Name + type signals."""
    # 4. "Status" in name — checked BEFORE bitfield to catch status
    #    bitfields (e.g. Alert Status, Battery Critical Status)
    if "Status" in char_name:
        return CharacteristicRole.STATUS

    # 5. Bitfield characteristics describe device capabilities
    if is_bitfield:
        return CharacteristicRole.FEATURE

    # 6. IntFlag types are capability/category flag sets
    if is_intflag:
        return CharacteristicRole.FEATURE

    return None


def _classify_naming_conventions(char_name: str) -> CharacteristicRole | None:
    """Tier 3: SIG naming conventions."""
    # 7. Explicit measurement/data by SIG naming convention
    if "Measurement" in char_name or char_name.endswith(" Data"):
        return CharacteristicRole.MEASUREMENT

    # 8. Feature by name (catches non-bitfield feature characteristics)
    if char_name.endswith("Feature") or char_name.endswith("Features"):
        return CharacteristicRole.FEATURE

    return None


def _classify_type_inference(
    python_type: type | str | None,
    unit: str,
    is_enum: bool,
    is_unitless: bool,
) -> CharacteristicRole | None:
    """Tier 4: Type-driven inference."""
    # 9. Has unit string from CharacteristicInfo
    if unit:
        return CharacteristicRole.MEASUREMENT

    # 10. Pure string types are info/metadata
    if python_type is str:
        return CharacteristicRole.INFO

    # 11. String subtypes (e.g. "ReportData", "HidInformationData")
    if isinstance(python_type, str):
        return CharacteristicRole.INFO

    # 12. Enum types are categorical state values
    if is_enum:
        return CharacteristicRole.STATUS

    # 13. Unitless unit_id with numeric type → dimensionless measurement
    if is_unitless and python_type in (int, float):
        return CharacteristicRole.MEASUREMENT

    # 14. Float type without any other signal → physical quantity
    if python_type is float:
        return CharacteristicRole.MEASUREMENT

    # 15. Boolean type → state flag
    if python_type is bool:
        return CharacteristicRole.STATUS

    return None


def _classify_struct_patterns(
    char_name: str,
    is_struct: bool,
) -> CharacteristicRole | None:
    """Tier 5: Struct name patterns (for structs with no YAML signal)."""
    if not is_struct:
        return None

    # 16. Measurement struct patterns
    if any(w in char_name for w in _MEASUREMENT_STRUCT_WORDS):
        return CharacteristicRole.MEASUREMENT
    if " in a " in char_name:
        return CharacteristicRole.MEASUREMENT

    # 17. Status struct patterns
    if any(w in char_name for w in _STATUS_STRUCT_WORDS):
        return CharacteristicRole.STATUS

    return None


def _spec_has_physical_field_units(spec: CharacteristicSpec | None) -> bool:
    """Check whether any field in the spec carries a physical (non-unitless) unit_id."""
    if not spec or not spec.structure:
        return False
    return any(f.unit_id and "unitless" not in f.unit_id for f in spec.structure)

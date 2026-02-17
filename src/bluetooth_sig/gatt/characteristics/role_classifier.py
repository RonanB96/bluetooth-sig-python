"""Role classification for GATT characteristics.

Classifies a characteristic's purpose (MEASUREMENT, FEATURE, CONTROL, etc.)
from SIG spec metadata using a heuristic based on name, value type, unit, and
specification structure.
"""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole, ValueType
from ...types.registry import CharacteristicSpec


def classify_role(
    char_name: str,
    value_type: ValueType,
    unit: str,
    spec: CharacteristicSpec | None,
) -> CharacteristicRole:
    """Classify a characteristic's purpose from SIG spec metadata.

    Classification priority (first match wins):
        1. Name contains *Control Point*           → CONTROL
        2. Name ends with *Feature(s)* or
           ``value_type`` is BITFIELD               → FEATURE
        3. Name contains *Measurement*              → MEASUREMENT
        4. Numeric type (INT / FLOAT) with a unit   → MEASUREMENT
        5. Compound type (VARIOUS / DICT) with a
           unit or field-level ``unit_id``          → MEASUREMENT
        6. Name ends with *Data*                    → MEASUREMENT
        7. Name contains *Status*                   → STATUS
        8. ``value_type`` is STRING                  → INFO
        9. Otherwise                                → UNKNOWN

    Args:
        char_name: Display name of the characteristic.
        value_type: Resolved value type enum.
        unit: Unit string (empty string if not applicable).
        spec: Resolved YAML spec (may be None).

    Returns:
        The classified ``CharacteristicRole``.

    """
    # 1. Control points are write-only command interfaces
    if "Control Point" in char_name:
        return CharacteristicRole.CONTROL

    # 2. Feature / capability bitfields describe device capabilities
    if char_name.endswith("Feature") or char_name.endswith("Features") or value_type == ValueType.BITFIELD:
        return CharacteristicRole.FEATURE

    # 3. Explicit measurement by SIG naming convention
    if "Measurement" in char_name:
        return CharacteristicRole.MEASUREMENT

    # 4. Numeric scalar with a physical unit
    if value_type in (ValueType.INT, ValueType.FLOAT) and unit:
        return CharacteristicRole.MEASUREMENT

    # 5. Compound value with unit metadata (char-level or per-field)
    if value_type in (ValueType.VARIOUS, ValueType.DICT) and (unit or _spec_has_unit_fields(spec)):
        return CharacteristicRole.MEASUREMENT

    # 6. SIG *Data* characteristics (Treadmill Data, Indoor Bike Data, …)
    if char_name.endswith(" Data"):
        return CharacteristicRole.MEASUREMENT

    # 7. State / status reporting characteristics
    if "Status" in char_name:
        return CharacteristicRole.STATUS

    # 8. Pure string metadata (device name, revision strings, …)
    if value_type == ValueType.STRING:
        return CharacteristicRole.INFO

    return CharacteristicRole.UNKNOWN


def _spec_has_unit_fields(spec: CharacteristicSpec | None) -> bool:
    """Check whether any field in the GSS spec carries a ``unit_id``.

    Returns ``True`` if the characteristic's resolved GSS specification
    contains at least one field with a non-empty ``unit_id``, indicating
    that the field represents a physical quantity with a unit.
    """
    if not spec:
        return False
    structure = getattr(spec, "structure", None)
    if not structure:
        return False
    return any(getattr(f, "unit_id", None) for f in structure)

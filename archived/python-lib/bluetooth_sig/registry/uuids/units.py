"""Registry for Bluetooth SIG unit UUID metadata.

Loads unit definitions from the Bluetooth SIG units.yaml specification,
providing UUID-to-name-to-symbol resolution. Used primarily for:
- Resolving org.bluetooth.unit.* identifiers from GSS YAML files
- Converting unit IDs to human-readable SI symbols for display

Note: This is distinct from the domain enums in types/units.py which
provide type-safe unit representations for decoded characteristic data.
The symbols derived here match those enum values for consistency.
"""

from __future__ import annotations

from bluetooth_sig.registry.base import BaseUUIDRegistry
from bluetooth_sig.types.registry.units import UnitInfo
from bluetooth_sig.types.uuid import BluetoothUUID

# SI symbol mappings for unit names in parentheses
_UNIT_NAME_TO_SYMBOL: dict[str, str] = {
    "degree celsius": "°C",
    "degree fahrenheit": "°F",
    "kelvin": "K",
    "pascal": "Pa",
    "bar": "bar",
    "millimetre of mercury": "mmHg",
    "ampere": "A",
    "volt": "V",
    "coulomb": "C",
    "farad": "F",
    "ohm": "Ω",
    "siemens": "S",
    "weber": "Wb",
    "tesla": "T",
    "henry": "H",
    "joule": "J",
    "watt": "W",
    "hertz": "Hz",
    "metre": "m",
    "kilogram": "kg",
    "second": "s",
    "metres per second": "m/s",
    "metres per second squared": "m/s²",
    "square metres": "m²",
    "cubic metres": "m³",
    "radian per second": "rad/s",
    "newton": "N",
    "candela": "cd",
    "lux": "lx",
    "lumen": "lm",
    "becquerel": "Bq",
    "gray": "Gy",
    "sievert": "Sv",
    "katal": "kat",
    "degree": "°",
    "radian": "rad",
    "steradian": "sr",
    "mole": "mol",
    "beats per minute": "bpm",
    "kilometre per hour": "km/h",
    "kilowatt hour": "kWh",
    "watt per square metre": "W/m²",
    "newton metre": "N·m",
    "lumen per watt": "lm/W",
    "lux hour": "lx·h",
    "gram per second": "g/s",
    "litre per second": "L/s",
    "kilogram calorie": "kcal",
    "minute": "min",
    "hour": "h",
    "day": "d",
    "month": "mo",
    "year": "yr",
    "decibel": "dB",
    "count per second": "cps",
    "revolution per minute": "rpm",
    "step per minute": "steps/min",
    "stroke per minute": "strokes/min",
}

_SPECIAL_UNIT_NAMES: dict[str, str] = {
    "percentage": "%",
    "per mille": "‰",
    "unitless": "",
}


def _derive_symbol_from_name(name: str) -> str:
    """Derive SI symbol from unit name.

    Handles formats like:
    - "thermodynamic temperature (degree celsius)" -> "°C"
    - "percentage" -> "%"
    - "length (metre)" -> "m"

    Args:
        name: Unit name from YAML

    Returns:
        SI symbol, or empty string if unknown
    """
    name_lower = name.lower()

    if name_lower in _SPECIAL_UNIT_NAMES:
        return _SPECIAL_UNIT_NAMES[name_lower]

    if "(" in name and ")" in name:
        start = name.find("(") + 1
        end = name.find(")", start)
        if 0 < start < end:
            parenthetical = name[start:end].strip().lower()
            if parenthetical in _UNIT_NAME_TO_SYMBOL:
                return _UNIT_NAME_TO_SYMBOL[parenthetical]
            return parenthetical

    return ""


class UnitsRegistry(BaseUUIDRegistry[UnitInfo]):
    """Registry for Bluetooth SIG unit UUIDs."""

    def _load_yaml_path(self) -> str:
        """Return the YAML file path relative to bluetooth_sig/ root."""
        return "units.yaml"

    def _create_info_from_yaml(self, uuid_data: dict[str, str], uuid: BluetoothUUID) -> UnitInfo:
        """Create UnitInfo from YAML data with derived symbol."""
        unit_name = uuid_data["name"]
        return UnitInfo(
            uuid=uuid,
            name=unit_name,
            id=uuid_data["id"],
            symbol=_derive_symbol_from_name(unit_name),
        )

    def _create_runtime_info(self, entry: object, uuid: BluetoothUUID) -> UnitInfo:
        """Create runtime UnitInfo from entry."""
        unit_name = getattr(entry, "name", "")
        return UnitInfo(
            uuid=uuid,
            name=unit_name,
            id=getattr(entry, "id", ""),
            symbol=getattr(entry, "symbol", "") or _derive_symbol_from_name(unit_name),
        )

    def get_unit_info(self, uuid: str | BluetoothUUID) -> UnitInfo | None:
        """Get unit information by UUID.

        Args:
            uuid: 16-bit UUID as string (with or without 0x) or BluetoothUUID

        Returns:
            UnitInfo object, or None if not found
        """
        return self.get_info(uuid)

    def get_unit_info_by_name(self, name: str) -> UnitInfo | None:
        """Get unit information by name.

        Args:
            name: Unit name (case-insensitive)

        Returns:
            UnitInfo object, or None if not found
        """
        return self.get_info(name)

    def get_unit_info_by_id(self, unit_id: str) -> UnitInfo | None:
        """Get unit information by ID.

        Args:
            unit_id: Unit ID (e.g., "org.bluetooth.unit.celsius")

        Returns:
            UnitInfo object, or None if not found
        """
        return self.get_info(unit_id)

    def is_unit_uuid(self, uuid: str | BluetoothUUID) -> bool:
        """Check if a UUID is a registered unit UUID.

        Args:
            uuid: UUID to check

        Returns:
            True if the UUID is a unit UUID, False otherwise
        """
        return self.get_unit_info(uuid) is not None

    def get_all_units(self) -> list[UnitInfo]:
        """Get all registered units.

        Returns:
            List of all UnitInfo objects
        """
        self._ensure_loaded()
        with self._lock:
            return list(self._canonical_store.values())


# Global instance
def get_units_registry() -> UnitsRegistry:
    """Return the process-wide units_registry singleton instance."""
    return UnitsRegistry.get_instance()


_UNIT_ID_PREFIX = "org.bluetooth.unit."


def resolve_unit_symbol(unit_id: str) -> str:
    """Resolve a SIG unit identifier to its canonical symbol.

    Accepts both short-form (``thermodynamic_temperature.degree_celsius``)
    and full-form (``org.bluetooth.unit.thermodynamic_temperature.degree_celsius``)
    identifiers, normalises to full-form, and looks up the symbol via
    :data:`units_registry`.

    Args:
        unit_id: Unit identifier (short or full form).

    Returns:
        SI symbol string (e.g. ``'°C'``, ``'bpm'``), or empty string
        if the identifier cannot be resolved.

    """
    full_id = unit_id if unit_id.startswith(_UNIT_ID_PREFIX) else f"{_UNIT_ID_PREFIX}{unit_id}"
    info = get_units_registry().get_unit_info_by_id(full_id)
    return info.symbol if info and info.symbol else ""

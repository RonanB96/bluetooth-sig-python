"""Types for Bluetooth SIG units registry."""

from __future__ import annotations

from bluetooth_sig.types.registry.common import UuidIdInfo


class UnitInfo(UuidIdInfo, frozen=True, kw_only=True):
    """Unit information from Bluetooth SIG units registry.

    Extends UuidIdInfo with a symbol field for the SI unit symbol.

    Attributes:
        uuid: Bluetooth UUID for this unit
        name: Descriptive name (e.g., "thermodynamic temperature (degree celsius)")
        id: Org.bluetooth identifier (e.g., "org.bluetooth.unit.thermodynamic_temperature.degree_celsius")
        symbol: SI unit symbol (e.g., "°C"), derived from name during loading
    """

    symbol: str = ""

    @property
    def readable_name(self) -> str:
        """Human-readable unit name extracted from the descriptive name.

        Extracts the parenthetical content from YAML-style names:
        - ``"thermodynamic temperature (degree celsius)"`` → ``"degree celsius"``
        - ``"period (beats per minute)"`` → ``"beats per minute"``
        - ``"percentage"`` → ``"percentage"`` (no parenthetical → returns full name)
        """
        if "(" in self.name and ")" in self.name:
            start = self.name.find("(") + 1
            end = self.name.find(")", start)
            if 0 < start < end:
                return self.name[start:end].strip()
        return self.name

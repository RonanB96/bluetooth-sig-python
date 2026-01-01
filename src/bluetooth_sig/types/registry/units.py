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

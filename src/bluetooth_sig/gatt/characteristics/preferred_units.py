"""Preferred Units characteristic (0x2B46)."""

from __future__ import annotations

import msgspec

from ...registry.uuids.units import units_registry
from ...types.registry.units import UnitInfo
from ...types.uuid import BluetoothUUID
from ..context import CharacteristicContext
from ..exceptions import InsufficientDataError
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class PreferredUnitsData(msgspec.Struct, frozen=True, kw_only=True):
    """Preferred Units data structure."""

    units: list[BluetoothUUID]


class PreferredUnitsCharacteristic(BaseCharacteristic[PreferredUnitsData]):
    """Preferred Units characteristic (0x2B46).

    org.bluetooth.characteristic.preferred_units

    The Preferred Units characteristic is the list of units the user prefers.
    Each unit is represented by a 16-bit Bluetooth UUID from the Bluetooth SIG units registry.
    """

    # Variable length: minimum 0 bytes (empty list), multiples of 2 bytes (16-bit UUIDs)
    min_length = 0
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> PreferredUnitsData:
        """Decode Preferred Units from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (variable length, multiples of 2)
            ctx: Optional context for parsing
            validate: Whether to validate ranges (default True)

        Returns:
            PreferredUnitsData: Parsed preferred units as Bluetooth UUID objects

        Raises:
            InsufficientDataError: If data length is not a multiple of 2
        """
        if len(data) % 2 != 0:
            raise InsufficientDataError("Preferred Units", data, len(data) + (len(data) % 2))

        units: list[BluetoothUUID] = []
        for i in range(0, len(data), 2):
            unit_value = DataParser.parse_int16(data, i, signed=False)
            unit_uuid = BluetoothUUID(unit_value)
            units.append(unit_uuid)

        return PreferredUnitsData(units=units)

    def _encode_value(self, data: PreferredUnitsData) -> bytearray:
        """Encode Preferred Units to raw bytes.

        Args:
            data: PreferredUnitsData to encode

        Returns:
            bytearray: Encoded bytes
        """
        result = bytearray()
        for unit_uuid in data.units:
            # Extract 16-bit short form value from UUID for encoding
            unit_value = int(unit_uuid.short_form, 16)
            result.extend(DataParser.encode_int16(unit_value, signed=False))
        return result

    def get_units(self, data: PreferredUnitsData) -> list[UnitInfo]:
        """Get unit information for the preferred units.

        Args:
            data: PreferredUnitsData containing unit UUIDs

        Returns:
            List of UnitInfo objects, with placeholder UnitInfo for unrecognized UUIDs
        """
        units: list[UnitInfo] = []
        for unit_uuid in data.units:
            unit_info = units_registry.get_unit_info(unit_uuid)
            if unit_info:
                units.append(unit_info)
            else:
                # Create a placeholder UnitInfo for unknown units
                units.append(
                    UnitInfo(
                        uuid=unit_uuid,
                        name=f"Unknown Unit ({unit_uuid.short_form})",
                        id=f"unknown.{unit_uuid.short_form.lower()}",
                    )
                )
        return units

    def validate_units(self, data: PreferredUnitsData) -> list[str]:
        """Validate that all units in the data are recognized Bluetooth SIG units.

        Args:
            data: PreferredUnitsData to validate

        Returns:
            List of validation errors (empty if all units are valid)
        """
        errors: list[str] = []
        for i, unit_uuid in enumerate(data.units):
            if not units_registry.is_unit_uuid(unit_uuid):
                errors.append(f"Unit at index {i} ({unit_uuid.short_form}) is not a recognized Bluetooth SIG unit")
        return errors

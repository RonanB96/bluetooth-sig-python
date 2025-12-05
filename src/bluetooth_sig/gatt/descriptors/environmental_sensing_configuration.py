"""Environmental Sensing Configuration Descriptor implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class ESCFlags(IntFlag):
    """ESC (Environmental Sensing Configuration) flags."""

    TRIGGER_LOGIC_VALUE = 0x0001
    TRANSMISSION_INTERVAL_PRESENT = 0x0002
    MEASUREMENT_PERIOD_PRESENT = 0x0004
    UPDATE_INTERVAL_PRESENT = 0x0008
    APPLICATION_PRESENT = 0x0010
    MEASUREMENT_UNCERTAINTY_PRESENT = 0x0020


class EnvironmentalSensingConfigurationData(msgspec.Struct, frozen=True, kw_only=True):
    """Environmental Sensing Configuration descriptor data."""

    trigger_logic_value: bool
    transmission_interval_present: bool
    measurement_period_present: bool
    update_interval_present: bool
    application_present: bool
    measurement_uncertainty_present: bool


class EnvironmentalSensingConfigurationDescriptor(BaseDescriptor):
    """Environmental Sensing Configuration Descriptor (0x290B).

    Configures environmental sensing measurement parameters.
    Contains various configuration flags for sensor behaviour.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "uint16"

    def _parse_descriptor_value(self, data: bytes) -> EnvironmentalSensingConfigurationData:
        """Parse Environmental Sensing Configuration value.

        Args:
            data: Raw bytes (should be 2 bytes for uint16)

        Returns:
            EnvironmentalSensingConfigurationData with configuration flags

        Raises:
            ValueError: If data is not exactly 2 bytes
        """
        if len(data) != 2:
            raise ValueError(f"Environmental Sensing Configuration data must be exactly 2 bytes, got {len(data)}")

        # Parse as little-endian uint16
        value = DataParser.parse_int16(data, endian="little")

        return EnvironmentalSensingConfigurationData(
            trigger_logic_value=bool(value & ESCFlags.TRIGGER_LOGIC_VALUE),
            transmission_interval_present=bool(value & ESCFlags.TRANSMISSION_INTERVAL_PRESENT),
            measurement_period_present=bool(value & ESCFlags.MEASUREMENT_PERIOD_PRESENT),
            update_interval_present=bool(value & ESCFlags.UPDATE_INTERVAL_PRESENT),
            application_present=bool(value & ESCFlags.APPLICATION_PRESENT),
            measurement_uncertainty_present=bool(value & ESCFlags.MEASUREMENT_UNCERTAINTY_PRESENT),
        )

    def has_trigger_logic_value(self, data: bytes) -> bool:
        """Check if trigger logic value is present."""
        parsed = self._parse_descriptor_value(data)
        return parsed.trigger_logic_value

    def has_transmission_interval(self, data: bytes) -> bool:
        """Check if transmission interval is present."""
        parsed = self._parse_descriptor_value(data)
        return parsed.transmission_interval_present

    def has_measurement_period(self, data: bytes) -> bool:
        """Check if measurement period is present."""
        parsed = self._parse_descriptor_value(data)
        return parsed.measurement_period_present

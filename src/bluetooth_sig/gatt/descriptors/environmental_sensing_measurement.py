"""Environmental Sensing Measurement Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class EnvironmentalSensingMeasurementData(msgspec.Struct, frozen=True, kw_only=True):
    """Environmental Sensing Measurement descriptor data."""

    sampling_function: int
    measurement_period: int
    update_interval: int
    application: int
    measurement_uncertainty: int


class EnvironmentalSensingMeasurementDescriptor(BaseDescriptor):
    """Environmental Sensing Measurement Descriptor (0x290C).

    Contains measurement parameters for environmental sensors.
    Includes sampling function, measurement period, and other parameters.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "struct"

    def _parse_descriptor_value(self, data: bytes) -> EnvironmentalSensingMeasurementData:
        """Parse Environmental Sensing Measurement value.

        Format: 12 bytes
        - Sampling Function (3 bytes, uint24) - using uint32 for simplicity
        - Measurement Period (3 bytes, uint24) - using uint32 for simplicity
        - Update Interval (3 bytes, uint24) - using uint32 for simplicity
        - Application (1 byte)
        - Measurement Uncertainty (2 bytes, uint16)

        Args:
            data: Raw bytes (should be 12 bytes)

        Returns:
            EnvironmentalSensingMeasurementData with measurement parameters

        Raises:
            ValueError: If data is not exactly 12 bytes
        """
        # For simplicity, treat uint24 values as uint32 (they'll fit)
        return EnvironmentalSensingMeasurementData(
            sampling_function=DataParser.parse_int32(data, offset=0, endian="little") & 0xFFFFFF,
            measurement_period=DataParser.parse_int32(data, offset=3, endian="little") & 0xFFFFFF,
            update_interval=DataParser.parse_int32(data, offset=6, endian="little") & 0xFFFFFF,
            application=DataParser.parse_int8(data, offset=9),
            measurement_uncertainty=DataParser.parse_int16(data, offset=10, endian="little"),
        )

    def get_sampling_function(self, data: bytes) -> int:
        """Get the sampling function."""
        parsed = self._parse_descriptor_value(data)
        return parsed.sampling_function

    def get_measurement_period(self, data: bytes) -> int:
        """Get the measurement period."""
        parsed = self._parse_descriptor_value(data)
        return parsed.measurement_period

    def get_update_interval(self, data: bytes) -> int:
        """Get the update interval."""
        parsed = self._parse_descriptor_value(data)
        return parsed.update_interval

    def get_application(self, data: bytes) -> int:
        """Get the application identifier."""
        parsed = self._parse_descriptor_value(data)
        return parsed.application

    def get_measurement_uncertainty(self, data: bytes) -> int:
        """Get the measurement uncertainty."""
        parsed = self._parse_descriptor_value(data)
        return parsed.measurement_uncertainty

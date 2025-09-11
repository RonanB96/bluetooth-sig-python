"""Electric Current Statistics characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ElectricCurrentStatisticsData:
    """Data class for electric current statistics."""

    minimum: float  # Minimum current in Amperes
    maximum: float  # Maximum current in Amperes
    average: float  # Average current in Amperes
    unit: str = "A"

    def __post_init__(self) -> None:
        """Validate current statistics data."""
        # Validate logical order
        if self.minimum > self.maximum:
            raise ValueError(
                f"Minimum current {self.minimum} A cannot be greater than maximum {self.maximum} A"
            )
        if not self.minimum <= self.average <= self.maximum:
            raise ValueError(
                f"Average current {self.average} A must be between minimum {self.minimum} A and maximum {self.maximum} A"
            )

        # Validate range for uint16 with 0.01 A resolution (0 to 655.35 A)
        max_current_value = 65535 * 0.01
        for name, current in [
            ("minimum", self.minimum),
            ("maximum", self.maximum),
            ("average", self.average),
        ]:
            if not 0.0 <= current <= max_current_value:
                raise ValueError(
                    f"{name.capitalize()} current {current} A is outside valid range (0.0 to {max_current_value} A)"
                )


@dataclass
class ElectricCurrentStatisticsCharacteristic(BaseCharacteristic):
    """Electric Current Statistics characteristic.

    Provides statistical current data (min, max, average over time).
    """

    _characteristic_name: str = "Electric Current Statistics"
    _manual_value_type: str = "string"  # Override since decode_value returns dataclass

    def decode_value(self, data: bytearray) -> ElectricCurrentStatisticsData:
        """Parse current statistics data (3x uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            ElectricCurrentStatisticsData with 'minimum', 'maximum', and 'average' current values in Amperes

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 6:
            raise ValueError(
                "Electric current statistics data must be at least 6 bytes"
            )

        # Convert 3x uint16 (little endian) to current statistics in Amperes
        min_current_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_current_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)
        avg_current_raw = int.from_bytes(data[4:6], byteorder="little", signed=False)

        return ElectricCurrentStatisticsData(
            minimum=min_current_raw * 0.01,
            maximum=max_current_raw * 0.01,
            average=avg_current_raw * 0.01,
        )

    def encode_value(
        self, data: ElectricCurrentStatisticsData | dict[str, float]
    ) -> bytearray:
        """Encode electric current statistics value back to bytes.

        Args:
            data: ElectricCurrentStatisticsData instance or dict with 'minimum', 'maximum', and 'average' current values in Amperes

        Returns:
            Encoded bytes representing the current statistics (3x uint16, 0.01 A resolution)
        """
        if isinstance(data, dict):
            # Convert dict to dataclass for backward compatibility
            if "minimum" not in data or "maximum" not in data or "average" not in data:
                raise ValueError(
                    "Electric current statistics data must contain 'minimum', 'maximum', and 'average' keys"
                )
            data = ElectricCurrentStatisticsData(
                minimum=float(data["minimum"]),
                maximum=float(data["maximum"]),
                average=float(data["average"]),
            )
        elif not isinstance(data, ElectricCurrentStatisticsData):
            raise TypeError(
                "Electric current statistics data must be ElectricCurrentStatisticsData or dictionary"
            )

        # Convert Amperes to raw values (multiply by 100 for 0.01 A resolution)
        min_current_raw = round(data.minimum * 100)
        max_current_raw = round(data.maximum * 100)
        avg_current_raw = round(data.average * 100)

        # Encode as 3 uint16 values (little endian)
        result = bytearray()
        result.extend(min_current_raw.to_bytes(2, byteorder="little", signed=False))
        result.extend(max_current_raw.to_bytes(2, byteorder="little", signed=False))
        result.extend(avg_current_raw.to_bytes(2, byteorder="little", signed=False))

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "A"

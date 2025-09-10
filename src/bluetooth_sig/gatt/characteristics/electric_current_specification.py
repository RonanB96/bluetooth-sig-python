"""Electric Current Specification characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ElectricCurrentSpecificationData:
    """Data class for electric current specification."""

    minimum: float  # Minimum current in Amperes
    maximum: float  # Maximum current in Amperes
    unit: str = "A"

    def __post_init__(self) -> None:
        """Validate current specification data."""
        if self.minimum > self.maximum:
            raise ValueError(
                f"Minimum current {self.minimum} A cannot be greater than maximum {self.maximum} A"
            )

        # Validate range for uint16 with 0.01 A resolution (0 to 655.35 A)
        max_current_value = 65535 * 0.01
        if not 0.0 <= self.minimum <= max_current_value:
            raise ValueError(
                f"Minimum current {self.minimum} A is outside valid range (0.0 to {max_current_value} A)"
            )
        if not 0.0 <= self.maximum <= max_current_value:
            raise ValueError(
                f"Maximum current {self.maximum} A is outside valid range (0.0 to {max_current_value} A)"
            )


@dataclass
class ElectricCurrentSpecificationCharacteristic(BaseCharacteristic):
    """Electric Current Specification characteristic.

    Specifies minimum and maximum current values for electrical specifications.
    """

    _characteristic_name: str = "Electric Current Specification"
    _manual_value_type: str = "string"  # Override since decode_value returns dataclass

    def decode_value(self, data: bytearray) -> ElectricCurrentSpecificationData:
        """Parse current specification data (2x uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            ElectricCurrentSpecificationData with 'minimum' and 'maximum' current specification values in Amperes

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 4:
            raise ValueError(
                "Electric current specification data must be at least 4 bytes"
            )

        # Convert 2x uint16 (little endian) to current specification in Amperes
        min_current_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_current_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)

        return ElectricCurrentSpecificationData(
            minimum=min_current_raw * 0.01, maximum=max_current_raw * 0.01
        )

    def encode_value(
        self, data: ElectricCurrentSpecificationData | dict[str, float]
    ) -> bytearray:
        """Encode electric current specification value back to bytes.

        Args:
            data: ElectricCurrentSpecificationData instance or dict with 'minimum' and 'maximum' current values in Amperes

        Returns:
            Encoded bytes representing the current specification (2x uint16, 0.01 A resolution)
        """
        if isinstance(data, dict):
            # Convert dict to dataclass for backward compatibility
            if "minimum" not in data or "maximum" not in data:
                raise ValueError(
                    "Electric current specification data must contain 'minimum' and 'maximum' keys"
                )
            data = ElectricCurrentSpecificationData(
                minimum=float(data["minimum"]), maximum=float(data["maximum"])
            )
        elif not isinstance(data, ElectricCurrentSpecificationData):
            raise TypeError(
                "Electric current specification data must be ElectricCurrentSpecificationData or dictionary"
            )

        # Convert Amperes to raw values (multiply by 100 for 0.01 A resolution)
        min_current_raw = round(data.minimum * 100)
        max_current_raw = round(data.maximum * 100)

        # Encode as 2 uint16 values (little endian)
        result = bytearray()
        result.extend(min_current_raw.to_bytes(2, byteorder="little", signed=False))
        result.extend(max_current_raw.to_bytes(2, byteorder="little", signed=False))

        return result

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "A"

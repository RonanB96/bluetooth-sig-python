"""True Wind Speed characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class TrueWindSpeedCharacteristic(BaseCharacteristic):
    """True Wind Speed measurement characteristic."""

    _characteristic_name: str = "True Wind Speed"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse true wind speed data (uint16 in units of 0.01 m/s)."""
        if len(data) < 2:
            raise ValueError("True wind speed data must be at least 2 bytes")

        # Convert uint16 (little endian) to wind speed in m/s
        wind_speed_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return wind_speed_raw * 0.01

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "m/s"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "wind_speed"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
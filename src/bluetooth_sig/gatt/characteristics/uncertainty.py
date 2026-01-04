"""Uncertainty characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint8Template


class UncertaintyCharacteristic(BaseCharacteristic[float]):
    """Uncertainty characteristic (0x2AB4).

    org.bluetooth.characteristic.uncertainty

    Uncertainty characteristic for Indoor Positioning Service.

    This characteristic represents the uncertainty or accuracy of the indoor positioning
    measurements. It provides an estimate of the error margin for the position coordinates
    (Local North Coordinate, Local East Coordinate, and Altitude).

    The uncertainty value indicates the radius of a circle (in 2D) or sphere (in 3D) within
    which the actual position is expected to lie with a certain confidence level. The value
    is encoded as a scaled uint8 with 0.1 meter resolution, providing a range of 0-25.5 meters.

    A value of 0 indicates the highest accuracy (no uncertainty), while higher values
    indicate increasing uncertainty in the position measurements.

    Args:
        data: Raw bytes from BLE characteristic (exactly 1 byte, uint8)
        ctx: Optional context for parsing

    Returns:
        Uncertainty radius in meters (0.0 to 25.5)

    Raises:
        InsufficientDataError: If data is not exactly 1 byte
        ValueRangeError: If decoded value exceeds maximum 25.5 meters

    Spec Reference:
        Bluetooth SIG Assigned Numbers, Uncertainty characteristic (0x2AB4)
        Indoor Positioning Service specification
    """

    # Manual overrides required as Bluetooth SIG registry doesn't provide unit/value type
    _manual_unit = "m"
    _manual_value_type = "float"
    _template = ScaledUint8Template(scale_factor=0.1)

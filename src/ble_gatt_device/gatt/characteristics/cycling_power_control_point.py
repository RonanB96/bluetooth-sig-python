"""Cycling Power Control Point characteristic implementation."""

import struct
from dataclasses import dataclass
from typing import Any, Dict

from .base import BaseCharacteristic


@dataclass
class CyclingPowerControlPointCharacteristic(BaseCharacteristic):
    """Cycling Power Control Point characteristic (0x2A66).

    Used for control and configuration of cycling power sensors.
    Provides commands for calibration, configuration, and sensor control.
    """

    _characteristic_name: str = "Cycling Power Control Point"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "string"  # JSON string representation
        super().__post_init__()

    def parse_value(self, data: bytearray) -> Dict[str, Any]:
        """Parse cycling power control point data.

        Format: Op Code(1) + [Request Parameter] or Response Code(1) + [Response Parameter]

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            Dict containing parsed control point data

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 1:
            raise ValueError("Cycling Power Control Point data must be at least 1 byte")

        op_code = data[0]
        
        result = {
            "op_code": op_code,
            "op_code_name": self._get_op_code_name(op_code)
        }

        # Parse additional data based on op code
        if len(data) > 1:
            if op_code == 0x01:  # Set Cumulative Value
                if len(data) >= 5:
                    cumulative_value = struct.unpack("<I", data[1:5])[0]
                    result["cumulative_value"] = cumulative_value
            elif op_code == 0x02:  # Update Sensor Location
                if len(data) >= 2:
                    sensor_location = data[1]
                    result["sensor_location"] = sensor_location
            elif op_code == 0x03:  # Request Supported Sensor Locations
                pass  # No additional parameters
            elif op_code == 0x04:  # Set Crank Length
                if len(data) >= 3:
                    crank_length = struct.unpack("<H", data[1:3])[0]
                    result["crank_length"] = crank_length / 2.0  # 0.5mm resolution
            elif op_code == 0x05:  # Request Crank Length
                pass  # No additional parameters
            elif op_code == 0x06:  # Set Chain Length
                if len(data) >= 3:
                    chain_length = struct.unpack("<H", data[1:3])[0]
                    result["chain_length"] = chain_length / 10.0  # 0.1mm resolution
            elif op_code == 0x07:  # Request Chain Length
                pass  # No additional parameters
            elif op_code == 0x08:  # Set Chain Weight
                if len(data) >= 3:
                    chain_weight = struct.unpack("<H", data[1:3])[0]
                    result["chain_weight"] = chain_weight / 10.0  # 0.1g resolution
            elif op_code == 0x09:  # Request Chain Weight
                pass  # No additional parameters
            elif op_code == 0x0A:  # Set Span Length
                if len(data) >= 3:
                    span_length = struct.unpack("<H", data[1:3])[0]
                    result["span_length"] = span_length  # mm
            elif op_code == 0x0B:  # Request Span Length
                pass  # No additional parameters
            elif op_code == 0x0C:  # Start Offset Compensation
                pass  # No additional parameters
            elif op_code == 0x0D:  # Mask Cycling Power Measurement
                if len(data) >= 3:
                    mask = struct.unpack("<H", data[1:3])[0]
                    result["measurement_mask"] = mask
            elif op_code == 0x0E:  # Request Sampling Rate
                pass  # No additional parameters
            elif op_code == 0x0F:  # Request Factory Calibration Date
                pass  # No additional parameters
            elif op_code == 0x20:  # Response Code
                if len(data) >= 3:
                    request_op_code = data[1]
                    response_value = data[2]
                    result["request_op_code"] = request_op_code
                    result["response_value"] = response_value
                    result["response_value_name"] = self._get_response_value_name(response_value)

        return result

    def _get_op_code_name(self, op_code: int) -> str:
        """Get human-readable name for operation code."""
        op_codes = {
            0x01: "Set Cumulative Value",
            0x02: "Update Sensor Location",
            0x03: "Request Supported Sensor Locations",
            0x04: "Set Crank Length",
            0x05: "Request Crank Length",
            0x06: "Set Chain Length",
            0x07: "Request Chain Length",
            0x08: "Set Chain Weight",
            0x09: "Request Chain Weight",
            0x0A: "Set Span Length",
            0x0B: "Request Span Length",
            0x0C: "Start Offset Compensation",
            0x0D: "Mask Cycling Power Measurement",
            0x0E: "Request Sampling Rate",
            0x0F: "Request Factory Calibration Date",
            0x20: "Response Code",
        }
        return op_codes.get(op_code, f"Unknown ({op_code:#04x})")

    def _get_response_value_name(self, response_value: int) -> str:
        """Get human-readable name for response value."""
        response_values = {
            0x01: "Success",
            0x02: "Op Code Not Supported",
            0x03: "Invalid Parameter",
            0x04: "Operation Failed",
        }
        return response_values.get(response_value, f"Unknown ({response_value:#04x})")

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""  # Control point has no unit

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return ""

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return ""
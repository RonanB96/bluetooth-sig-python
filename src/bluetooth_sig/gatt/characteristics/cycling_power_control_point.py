"""Cycling Power Control Point characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..constants import UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class OpCodeParameters(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed operation code parameters."""

    cumulative_value: int | None
    sensor_location: int | None
    crank_length: float | None
    chain_length: float | None
    chain_weight: float | None
    span_length: int | None
    measurement_mask: int | None
    request_op_code: CyclingPowerOpCode | None
    response_value: CyclingPowerResponseValue | None


class CyclingPowerControlPointData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from Cycling Power Control Point characteristic."""

    op_code: CyclingPowerOpCode
    # Optional parameters based on op_code
    cumulative_value: int | None = None
    sensor_location: int | None = None
    crank_length: float | None = None  # mm
    chain_length: float | None = None  # mm
    chain_weight: float | None = None  # g
    span_length: int | None = None  # mm
    measurement_mask: int | None = None
    request_op_code: CyclingPowerOpCode | None = None
    response_value: CyclingPowerResponseValue | None = None

    def __post_init__(self) -> None:
        """Validate cycling power control point data."""
        if not 0 <= self.op_code <= UINT8_MAX:
            raise ValueError("Op code must be a uint8 value (0-UINT8_MAX)")


class CyclingPowerOpCode(IntEnum):
    """Cycling Power Control Point operation codes as per Bluetooth SIG specification."""

    # Value 0x00 is Reserved for Future Use
    SET_CUMULATIVE_VALUE = 0x01
    UPDATE_SENSOR_LOCATION = 0x02
    REQUEST_SUPPORTED_SENSOR_LOCATIONS = 0x03
    SET_CRANK_LENGTH = 0x04
    REQUEST_CRANK_LENGTH = 0x05
    SET_CHAIN_LENGTH = 0x06
    REQUEST_CHAIN_LENGTH = 0x07
    SET_CHAIN_WEIGHT = 0x08
    REQUEST_CHAIN_WEIGHT = 0x09
    SET_SPAN_LENGTH = 0x0A
    REQUEST_SPAN_LENGTH = 0x0B
    START_OFFSET_COMPENSATION = 0x0C
    MASK_CYCLING_POWER_MEASUREMENT = 0x0D
    REQUEST_SAMPLING_RATE = 0x0E
    REQUEST_FACTORY_CALIBRATION_DATE = 0x0F
    # Values 0x10-0x1F are Reserved for Future Use
    RESPONSE_CODE = 0x20
    # Values 0x21-0xFF are Reserved for Future Use

    def __str__(self) -> str:
        """Return human-readable operation code name."""
        names = {
            self.SET_CUMULATIVE_VALUE: "Set Cumulative Value",
            self.UPDATE_SENSOR_LOCATION: "Update Sensor Location",
            self.REQUEST_SUPPORTED_SENSOR_LOCATIONS: "Request Supported Sensor Locations",
            self.SET_CRANK_LENGTH: "Set Crank Length",
            self.REQUEST_CRANK_LENGTH: "Request Crank Length",
            self.SET_CHAIN_LENGTH: "Set Chain Length",
            self.REQUEST_CHAIN_LENGTH: "Request Chain Length",
            self.SET_CHAIN_WEIGHT: "Set Chain Weight",
            self.REQUEST_CHAIN_WEIGHT: "Request Chain Weight",
            self.SET_SPAN_LENGTH: "Set Span Length",
            self.REQUEST_SPAN_LENGTH: "Request Span Length",
            self.START_OFFSET_COMPENSATION: "Start Offset Compensation",
            self.MASK_CYCLING_POWER_MEASUREMENT: "Mask Cycling Power Measurement",
            self.REQUEST_SAMPLING_RATE: "Request Sampling Rate",
            self.REQUEST_FACTORY_CALIBRATION_DATE: "Request Factory Calibration Date",
            self.RESPONSE_CODE: "Response Code",
        }
        return names[self]


# Constants
MIN_OP_CODE_LENGTH = 1  # Minimum length for op code data


class CyclingPowerResponseValue(IntEnum):
    """Cycling Power Control Point response values as per Bluetooth SIG specification."""

    # Value 0x00 is Reserved for Future Use
    SUCCESS = 0x01
    OP_CODE_NOT_SUPPORTED = 0x02
    INVALID_PARAMETER = 0x03
    OPERATION_FAILED = 0x04
    # Values 0x05-0xFF are Reserved for Future Use

    def __str__(self) -> str:
        """Return human-readable response value name."""
        names = {
            self.SUCCESS: "Success",
            self.OP_CODE_NOT_SUPPORTED: "Op Code Not Supported",
            self.INVALID_PARAMETER: "Invalid Parameter",
            self.OPERATION_FAILED: "Operation Failed",
        }
        return names[self]


class CyclingPowerControlPointCharacteristic(BaseCharacteristic[CyclingPowerControlPointData]):
    """Cycling Power Control Point characteristic (0x2A66).

    Used for control and configuration of cycling power sensors.
    Provides commands for calibration, configuration, and sensor
    control.
    """

    # Variable length: min 1 byte (op_code), variable parameters per op_code
    min_length = 1
    allow_variable_length = True

    # Resolution constants for parameter calculations
    CRANK_LENGTH_RESOLUTION = 2.0  # 0.5mm resolution (value / 2)
    CHAIN_LENGTH_RESOLUTION = 10.0  # 0.1mm resolution (value / 10)
    CHAIN_WEIGHT_RESOLUTION = 10.0  # 0.1g resolution (value / 10)

    # Data length constants
    MIN_OP_CODE_LENGTH = 1
    CUMULATIVE_VALUE_LENGTH = 5  # op_code(1) + value(4)
    SENSOR_LOCATION_LENGTH = 2  # op_code(1) + location(1)
    TWO_BYTE_PARAM_LENGTH = 3  # op_code(1) + param(2)
    RESPONSE_CODE_LENGTH = 3  # op_code(1) + request(1) + response(1)

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> CyclingPowerControlPointData:
        """Parse cycling power control point data.

        Format: Op Code(1) + [Request Parameter] or Response Code(1) + [Response Parameter].

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            CyclingPowerControlPointData containing parsed control point data.

        Raises:
            ValueError: If data format is invalid.

        """
        if len(data) < MIN_OP_CODE_LENGTH:
            raise ValueError("Cycling Power Control Point data must be at least 1 byte")

        op_code = data[0]

        # Parse additional data based on op code
        params = (
            self._parse_op_code_parameters(op_code, data)
            if len(data) > 1
            else OpCodeParameters(
                cumulative_value=None,
                sensor_location=None,
                crank_length=None,
                chain_length=None,
                chain_weight=None,
                span_length=None,
                measurement_mask=None,
                request_op_code=None,
                response_value=None,
            )
        )

        # Create struct with all parsed values
        return CyclingPowerControlPointData(
            op_code=CyclingPowerOpCode(op_code),
            cumulative_value=params.cumulative_value,
            sensor_location=params.sensor_location,
            crank_length=params.crank_length,
            chain_length=params.chain_length,
            chain_weight=params.chain_weight,
            span_length=params.span_length,
            measurement_mask=params.measurement_mask,
            request_op_code=params.request_op_code,
            response_value=params.response_value,
        )

    def _encode_value(self, data: CyclingPowerControlPointData | int) -> bytearray:
        """Encode cycling power control point value back to bytes.

        Args:
            data: CyclingPowerControlPointData with op_code and optional parameters, or raw op_code integer

        Returns:
            Encoded bytes representing the control point command

        """
        if isinstance(data, int):
            # Simple op code only
            op_code = data
            if not 0 <= op_code <= UINT8_MAX:
                raise ValueError(f"Op code {op_code} exceeds uint8 range")
            return bytearray([op_code])

        # Handle dataclass case
        op_code = data.op_code
        result = bytearray([op_code])

        # Add parameters based on op_code and available data
        if data.cumulative_value is not None:
            result.extend(DataParser.encode_int32(data.cumulative_value, signed=False))
        elif data.sensor_location is not None:
            result.append(data.sensor_location)
        elif data.crank_length is not None:
            result.extend(DataParser.encode_int16(int(data.crank_length * self.CRANK_LENGTH_RESOLUTION), signed=False))
        elif data.chain_length is not None:
            result.extend(DataParser.encode_int16(int(data.chain_length * self.CHAIN_LENGTH_RESOLUTION), signed=False))
        elif data.chain_weight is not None:
            result.extend(DataParser.encode_int16(int(data.chain_weight * self.CHAIN_WEIGHT_RESOLUTION), signed=False))
        elif data.span_length is not None:
            result.extend(DataParser.encode_int16(data.span_length, signed=False))
        elif data.measurement_mask is not None:
            result.extend(DataParser.encode_int16(data.measurement_mask, signed=False))
        elif data.request_op_code is not None and data.response_value is not None:
            result.extend([data.request_op_code.value, data.response_value.value])

        return result

    def _parse_op_code_parameters(  # pylint: disable=too-many-branches
        self, op_code: int, data: bytearray
    ) -> OpCodeParameters:
        """Parse operation code specific parameters.

        Args:
            op_code: Operation code
            data: Raw data

        Returns:
            OpCodeParameters containing all parsed parameters

        """
        cumulative_value: int | None = None
        sensor_location: int | None = None
        crank_length: float | None = None
        chain_length: float | None = None
        chain_weight: float | None = None
        span_length: int | None = None
        measurement_mask: int | None = None
        request_op_code: CyclingPowerOpCode | None = None
        response_value: CyclingPowerResponseValue | None = None

        if op_code == CyclingPowerOpCode.SET_CUMULATIVE_VALUE:
            if len(data) >= self.CUMULATIVE_VALUE_LENGTH:
                cumulative_value = DataParser.parse_int32(data, offset=1, signed=False)
        elif op_code == CyclingPowerOpCode.UPDATE_SENSOR_LOCATION:
            if len(data) >= self.SENSOR_LOCATION_LENGTH:
                sensor_location = int(data[1])
        elif op_code == CyclingPowerOpCode.SET_CRANK_LENGTH:
            if len(data) >= self.TWO_BYTE_PARAM_LENGTH:
                crank_length_raw = DataParser.parse_int16(data, offset=1, signed=False)
                crank_length = crank_length_raw / self.CRANK_LENGTH_RESOLUTION
        elif op_code == CyclingPowerOpCode.SET_CHAIN_LENGTH:
            if len(data) >= self.TWO_BYTE_PARAM_LENGTH:
                chain_length_raw = DataParser.parse_int16(data, offset=1, signed=False)
                chain_length = chain_length_raw / self.CHAIN_LENGTH_RESOLUTION
        elif op_code == CyclingPowerOpCode.SET_CHAIN_WEIGHT:
            if len(data) >= self.TWO_BYTE_PARAM_LENGTH:
                chain_weight_raw = DataParser.parse_int16(data, offset=1, signed=False)
                chain_weight = chain_weight_raw / self.CHAIN_WEIGHT_RESOLUTION
        elif op_code == CyclingPowerOpCode.SET_SPAN_LENGTH:
            if len(data) >= self.TWO_BYTE_PARAM_LENGTH:
                span_length = DataParser.parse_int16(data, offset=1, signed=False)  # mm
        elif op_code == CyclingPowerOpCode.MASK_CYCLING_POWER_MEASUREMENT:
            if len(data) >= self.TWO_BYTE_PARAM_LENGTH:
                measurement_mask = DataParser.parse_int16(data, offset=1, signed=False)
        elif op_code == CyclingPowerOpCode.RESPONSE_CODE:
            if len(data) >= self.RESPONSE_CODE_LENGTH:
                request_op_code = CyclingPowerOpCode(data[1])
                response_value = CyclingPowerResponseValue(data[2])

        return OpCodeParameters(
            cumulative_value=cumulative_value,
            sensor_location=sensor_location,
            crank_length=crank_length,
            chain_length=chain_length,
            chain_weight=chain_weight,
            span_length=span_length,
            measurement_mask=measurement_mask,
            request_op_code=request_op_code,
            response_value=response_value,
        )

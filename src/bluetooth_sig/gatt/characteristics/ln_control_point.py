"""LN Control Point characteristic implementation."""

from __future__ import annotations

from datetime import datetime
from enum import IntEnum

import msgspec

from ...types.gatt_enums import ValueType
from ..constants import UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser


class LNControlPointOpCode(IntEnum):
    """LN Control Point operation codes as per Bluetooth SIG specification."""

    # Value 0x00 is Reserved for Future Use
    SET_CUMULATIVE_VALUE = 0x01
    MASK_LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT = 0x02
    NAVIGATION_CONTROL = 0x03
    REQUEST_NUMBER_OF_ROUTES = 0x04
    REQUEST_NAME_OF_ROUTE = 0x05
    SELECT_ROUTE = 0x06
    SET_FIX_RATE = 0x07
    SET_ELEVATION = 0x08
    # Values 0x09-0x1F are Reserved for Future Use
    RESPONSE_CODE = 0x20
    # Values 0x21-0xFF are Reserved for Future Use

    def __str__(self) -> str:
        """Return human-readable operation code name."""
        names = {
            self.SET_CUMULATIVE_VALUE: "Set Cumulative Value",
            self.MASK_LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT: "Mask Location and Speed Characteristic Content",
            self.NAVIGATION_CONTROL: "Navigation Control",
            self.REQUEST_NUMBER_OF_ROUTES: "Request Number of Routes",
            self.REQUEST_NAME_OF_ROUTE: "Request Name of Route",
            self.SELECT_ROUTE: "Select Route",
            self.SET_FIX_RATE: "Set Fix Rate",
            self.SET_ELEVATION: "Set Elevation",
            self.RESPONSE_CODE: "Response Code",
        }
        return names[self]


class LNControlPointResponseValue(IntEnum):
    """LN Control Point response values as per Bluetooth SIG specification."""

    # Value 0x00 is Reserved for Future Use
    SUCCESS = 0x01
    OP_CODE_NOT_SUPPORTED = 0x02
    INVALID_OPERAND = 0x03
    OPERATION_FAILED = 0x04
    # Values 0x05-0xFF are Reserved for Future Use

    def __str__(self) -> str:
        """Return human-readable response value name."""
        names = {
            self.SUCCESS: "Success",
            self.OP_CODE_NOT_SUPPORTED: "Op Code not supported",
            self.INVALID_OPERAND: "Invalid Operand",
            self.OPERATION_FAILED: "Operation Failed",
        }
        return names[self]


class LNControlPointData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Parsed data from LN Control Point characteristic."""

    op_code: LNControlPointOpCode
    # Parameters based on op_code
    cumulative_value: int | None = None
    content_mask: int | None = None
    navigation_control_value: int | None = None
    route_number: int | None = None
    route_name: str | None = None
    fix_rate: int | None = None
    elevation: float | None = None
    # Response fields
    request_op_code: LNControlPointOpCode | None = None
    response_value: LNControlPointResponseValue | None = None
    response_parameter: int | str | datetime | bytearray | None = None

    def __post_init__(self) -> None:
        """Validate LN control point data."""
        if not 0 <= self.op_code <= UINT8_MAX:
            raise ValueError("Op code must be a uint8 value (0-UINT8_MAX)")


class LNControlPointCharacteristic(BaseCharacteristic[LNControlPointData]):
    """LN Control Point characteristic.

    Used to enable device-specific procedures related to the exchange of location and navigation information.
    """

    _manual_value_type: ValueType | str | None = ValueType.DICT  # Override since decode_value returns dataclass

    min_length = 1  # Op Code(1) minimum
    max_length = 18  # Op Code(1) + Parameter(max 17) maximum
    allow_variable_length: bool = True  # Variable parameter length

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> LNControlPointData:  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """Parse LN control point data according to Bluetooth specification.

        Format: Op Code(1) + Parameter(0-17).

        Args:
            data: Raw bytearray from BLE characteristic
            ctx: Optional context providing surrounding context (may be None)

        Returns:
            LNControlPointData containing parsed control point data

        """
        if len(data) < 1:
            raise ValueError("LN Control Point data must be at least 1 byte")

        op_code = LNControlPointOpCode(data[0])

        # Initialize optional fields
        cumulative_value: int | None = None
        content_mask: int | None = None
        navigation_control_value: int | None = None
        route_number: int | None = None
        route_name: str | None = None
        fix_rate: int | None = None
        elevation: float | None = None
        request_op_code: LNControlPointOpCode | None = None
        response_value: LNControlPointResponseValue | None = None
        response_parameter: int | str | datetime | bytearray | None = None

        if op_code == LNControlPointOpCode.SET_CUMULATIVE_VALUE:
            if len(data) >= 5:
                cumulative_value = DataParser.parse_int32(data, 1, signed=False)
        elif op_code == LNControlPointOpCode.MASK_LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT:
            if len(data) >= 3:
                content_mask = DataParser.parse_int16(data, 1, signed=False)
        elif op_code == LNControlPointOpCode.NAVIGATION_CONTROL:
            if len(data) >= 2:
                navigation_control_value = data[1]
        elif op_code == LNControlPointOpCode.REQUEST_NAME_OF_ROUTE:
            if len(data) >= 2:
                route_number = data[1]
        elif op_code == LNControlPointOpCode.SELECT_ROUTE:
            if len(data) >= 2:
                route_number = data[1]
        elif op_code == LNControlPointOpCode.SET_FIX_RATE:
            if len(data) >= 2:
                fix_rate = data[1]
        elif op_code == LNControlPointOpCode.SET_ELEVATION:
            if len(data) >= 5:
                # Unit is 1/100 m
                elevation = DataParser.parse_int32(data, 1, signed=True) / 100.0
        elif op_code == LNControlPointOpCode.RESPONSE_CODE:
            if len(data) >= 3:
                request_op_code = LNControlPointOpCode(data[1])
                response_value = LNControlPointResponseValue(data[2])
                # Parse response parameter based on request op code
                if len(data) > 3:
                    parameter_length = len(data) - 3
                    if request_op_code == LNControlPointOpCode.REQUEST_NUMBER_OF_ROUTES:
                        response_parameter = DataParser.parse_int16(data, 3, signed=False)
                    elif request_op_code == LNControlPointOpCode.REQUEST_NAME_OF_ROUTE:
                        response_parameter = data[3:].decode("utf-8", errors="ignore")
                    else:
                        # For other responses, parse based on parameter length
                        if parameter_length == 1:
                            response_parameter = data[3]
                        elif parameter_length == 2:
                            response_parameter = DataParser.parse_int16(data, 3, signed=False)
                        elif parameter_length == 4:
                            response_parameter = DataParser.parse_int32(data, 3, signed=False)
                        elif parameter_length == 7:
                            response_parameter = IEEE11073Parser.parse_timestamp(data, 3)
                        else:
                            # Unknown parameter format, store as bytes
                            response_parameter = data[3:]

        return LNControlPointData(
            op_code=op_code,
            cumulative_value=cumulative_value,
            content_mask=content_mask,
            navigation_control_value=navigation_control_value,
            route_number=route_number,
            route_name=route_name,
            fix_rate=fix_rate,
            elevation=elevation,
            request_op_code=request_op_code,
            response_value=response_value,
            response_parameter=response_parameter,
        )

    def _encode_value(self, data: LNControlPointData) -> bytearray:
        """Encode LNControlPointData back to bytes.

        Args:
            data: LNControlPointData instance to encode

        Returns:
            Encoded bytes representing the LN control point data

        """
        result = bytearray()
        result.append(data.op_code)

        # Handle parameter encoding based on op code
        op_code_handlers = {
            LNControlPointOpCode.SET_CUMULATIVE_VALUE: lambda: (
                result.extend(DataParser.encode_int32(data.cumulative_value, signed=False))
                if data.cumulative_value is not None
                else None
            ),
            LNControlPointOpCode.MASK_LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT: lambda: (
                result.extend(DataParser.encode_int16(data.content_mask, signed=False))
                if data.content_mask is not None
                else None
            ),
            LNControlPointOpCode.NAVIGATION_CONTROL: lambda: (
                result.append(data.navigation_control_value) if data.navigation_control_value is not None else None
            ),
            LNControlPointOpCode.REQUEST_NAME_OF_ROUTE: lambda: (
                result.append(data.route_number) if data.route_number is not None else None
            ),
            LNControlPointOpCode.SELECT_ROUTE: lambda: (
                result.append(data.route_number) if data.route_number is not None else None
            ),
            LNControlPointOpCode.SET_FIX_RATE: lambda: (
                result.append(data.fix_rate) if data.fix_rate is not None else None
            ),
            LNControlPointOpCode.SET_ELEVATION: lambda: (
                result.extend(DataParser.encode_int32(int(data.elevation * 100), signed=True))
                if data.elevation is not None
                else None
            ),
        }

        # Execute handler if op code is supported
        handler = op_code_handlers.get(data.op_code)
        if handler:
            handler()

        # Special handling for response code
        if data.op_code == LNControlPointOpCode.RESPONSE_CODE:
            if data.request_op_code is not None:
                result.append(data.request_op_code)
            if data.response_value is not None:
                result.append(data.response_value)
            if data.response_parameter is not None:
                if isinstance(data.response_parameter, int):
                    if data.response_parameter <= 0xFF:
                        result.append(data.response_parameter)
                    elif data.response_parameter <= 0xFFFF:
                        result.extend(DataParser.encode_int16(data.response_parameter, signed=False))
                elif isinstance(data.response_parameter, str):
                    result.extend(data.response_parameter.encode("utf-8"))
                elif isinstance(data.response_parameter, datetime):
                    result.extend(IEEE11073Parser.encode_timestamp(data.response_parameter))
                elif isinstance(data.response_parameter, bytearray):
                    result.extend(data.response_parameter)

        return result

"""Reconnection Configuration Control Point characteristic (0x2B1F).

Control point for executing procedures on the Reconnection Configuration
server, including parameter negotiation and connection management.

References:
    Bluetooth SIG Reconnection Configuration Service v1.0.1, Section 3.3
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class RCCPOpCode(IntEnum):
    """RCCP opcodes as per RCS v1.0.1 Table 3.7."""

    ENABLE_DISCONNECT = 0x00
    GET_ACTUAL_COMMUNICATION_PARAMETERS = 0x01
    PROPOSE_SETTINGS = 0x02
    ACTIVATE_STORED_SETTINGS = 0x03
    GET_MAX_VALUES = 0x04
    GET_MIN_VALUES = 0x05
    GET_STORED_VALUES = 0x06
    SET_FILTER_ACCEPT_LIST_TIMER = 0x07
    GET_FILTER_ACCEPT_LIST_TIMER = 0x08
    SET_ADVERTISEMENT_CONFIGURATION = 0x09
    UPGRADE_TO_LESC_ONLY = 0x0A
    SWITCH_OOB_PAIRING = 0x0B
    LIMITED_ACCESS = 0x0C
    PROCEDURE_RESPONSE = 0x0E
    COMMUNICATION_PARAMETER_RESPONSE = 0x0F
    FILTER_ACCEPT_LIST_TIMER_RESPONSE = 0x10
    CLIENT_PARAMETER_INDICATION = 0x11


class RCCPResultCode(IntEnum):
    """RCCP result codes as per RCS v1.0.1 Table 3.10."""

    SUCCESS = 0x01
    OPCODE_NOT_SUPPORTED = 0x02
    INVALID_OPERAND = 0x03
    OPERATION_FAILED = 0x04
    COMMUNICATION_PARAMETER_OUT_OF_RANGE = 0x05
    INVALID_PARAMETER_COMBINATION = 0x06
    DEVICE_BUSY = 0x07
    COMMUNICATION_PARAMETERS_REJECTED = 0x08
    PROPOSAL_ACCEPTED = 0x09


class ReconnectionConfigurationControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Reconnection Configuration Control Point.

    Attributes:
        op_code: The RCCP opcode identifying the procedure.
        parameter: Raw operand/parameter bytes (None if absent).

    """

    op_code: RCCPOpCode
    parameter: bytes | None = None


class ReconnectionConfigurationControlPointCharacteristic(
    BaseCharacteristic[ReconnectionConfigurationControlPointData],
):
    """Reconnection Configuration Control Point characteristic (0x2B1F).

    org.bluetooth.characteristic.reconnection_configuration_control_point

    Structure: Opcode (uint8) + Operand (0–17 octets) + [E2E-CRC (uint16)].
    E2E-CRC is conditionally present when E2E-CRC Supported is set in RC Feature.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ReconnectionConfigurationControlPointData:
        """Parse RCCP data per RCS v1.0.1 Section 3.3."""
        op_code = RCCPOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameter = bytes(data[1:]) if len(data) > 1 else None

        return ReconnectionConfigurationControlPointData(
            op_code=op_code,
            parameter=parameter,
        )

    def _encode_value(self, data: ReconnectionConfigurationControlPointData) -> bytearray:
        """Encode RCCP data."""
        result = bytearray([int(data.op_code)])
        if data.parameter is not None:
            result.extend(data.parameter)
        return result

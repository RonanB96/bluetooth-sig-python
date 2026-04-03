"""Object List Control Point characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class OLCPOpcode(IntEnum):
    """Object List Control Point opcodes per OTS specification."""

    FIRST = 0x01
    LAST = 0x02
    PREVIOUS = 0x03
    NEXT = 0x04
    GO_TO = 0x05
    ORDER = 0x06
    REQUEST_NUMBER_OF_OBJECTS = 0x07
    CLEAR_MARKING = 0x08
    RESPONSE = 0x70


class OLCPResultCode(IntEnum):
    """OLCP response result codes per OTS specification."""

    SUCCESS = 0x01
    OPCODE_NOT_SUPPORTED = 0x02
    INVALID_PARAMETER = 0x03
    OPERATION_FAILED = 0x04
    OUT_OF_BOUNDS = 0x05
    TOO_MANY_OBJECTS = 0x06
    NO_OBJECT = 0x07
    OBJECT_ID_NOT_FOUND = 0x08


class OLCPSortOrder(IntEnum):
    """OLCP sort order values per OTS specification."""

    NAME_ASCENDING = 0x01
    TYPE_ASCENDING = 0x02
    CURRENT_SIZE_ASCENDING = 0x03
    FIRST_CREATED_ASCENDING = 0x04
    LAST_MODIFIED_ASCENDING = 0x05
    NAME_DESCENDING = 0x11
    TYPE_DESCENDING = 0x12
    CURRENT_SIZE_DESCENDING = 0x13
    FIRST_CREATED_DESCENDING = 0x14
    LAST_MODIFIED_DESCENDING = 0x15


class OLCPData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Object List Control Point characteristic.

    Attributes:
        opcode: The OLCP opcode.
        parameters: Raw parameter bytes (opcode-dependent).

    """

    opcode: OLCPOpcode
    parameters: bytes = b""


class ObjectListControlPointCharacteristic(BaseCharacteristic[OLCPData]):
    """Object List Control Point characteristic (0x2AC6).

    org.bluetooth.characteristic.object_list_control_point

    Control point for object list navigation in the Object Transfer
    Service (OTS). Opcodes include First, Last, Previous, Next, Go To,
    Order, Request Number of Objects, Clear Marking, and Response.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length: int = 1  # At minimum: opcode (1 byte)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> OLCPData:
        """Parse OLCP data.

        Args:
            data: Raw bytes (1+ bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            OLCPData with opcode and parameters.

        """
        opcode = OLCPOpcode(DataParser.parse_int8(data, 0, signed=False))
        parameters = bytes(data[1:])
        return OLCPData(opcode=opcode, parameters=parameters)

    def _encode_value(self, data: OLCPData) -> bytearray:
        """Encode OLCP data to bytes.

        Args:
            data: OLCPData to encode.

        Returns:
            Encoded bytes.

        """
        result = DataParser.encode_int8(int(data.opcode), signed=False)
        result.extend(data.parameters)
        return result

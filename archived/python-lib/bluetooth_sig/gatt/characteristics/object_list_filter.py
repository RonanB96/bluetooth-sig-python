"""Object List Filter characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ObjectListFilterType(IntEnum):
    """Object List Filter types per OTS specification."""

    NO_FILTER = 0x00
    NAME_STARTS_WITH = 0x01
    NAME_ENDS_WITH = 0x02
    NAME_CONTAINS = 0x03
    NAME_IS_EXACTLY = 0x04
    OBJECT_TYPE = 0x05
    CREATED_BETWEEN = 0x06
    MODIFIED_BETWEEN = 0x07
    CURRENT_SIZE_BETWEEN = 0x08
    ALLOCATED_SIZE_BETWEEN = 0x09
    MARKED_OBJECTS = 0x0A


class ObjectListFilterData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Object List Filter characteristic.

    Attributes:
        filter_type: The filter type.
        parameters: Raw parameter bytes (filter-type-dependent).

    """

    filter_type: ObjectListFilterType
    parameters: bytes = b""


class ObjectListFilterCharacteristic(BaseCharacteristic[ObjectListFilterData]):
    """Object List Filter characteristic (0x2AC7).

    org.bluetooth.characteristic.object_list_filter

    Filter condition for the object list in the Object Transfer Service (OTS).
    Filter types include No Filter, Name Starts With, Name Ends With,
    Name Contains, Name is Exactly, Object Type, Created Between,
    Modified Between, Current Size Between, Allocated Size Between, and
    Marked Objects.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length: int = 1  # At minimum: filter type (1 byte)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> ObjectListFilterData:
        """Parse object list filter data.

        Args:
            data: Raw bytes (1+ bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            ObjectListFilterData with filter_type and parameters.

        """
        filter_type = ObjectListFilterType(DataParser.parse_int8(data, 0, signed=False))
        parameters = bytes(data[1:])
        return ObjectListFilterData(filter_type=filter_type, parameters=parameters)

    def _encode_value(self, data: ObjectListFilterData) -> bytearray:
        """Encode object list filter data to bytes.

        Args:
            data: ObjectListFilterData to encode.

        Returns:
            Encoded bytes.

        """
        result = DataParser.encode_int8(int(data.filter_type), signed=False)
        result.extend(data.parameters)
        return result

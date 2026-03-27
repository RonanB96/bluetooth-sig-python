"""ESL Sensor Information characteristic implementation."""

from __future__ import annotations

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ESLSensorInformationData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from ESL Sensor Information characteristic.

    Attributes:
        property_id: Mesh Device Property ID (uint16).
        raw_data: Remaining raw mesh device property bytes.

    """

    property_id: int
    raw_data: bytes = b""


class ESLSensorInformationCharacteristic(BaseCharacteristic[ESLSensorInformationData]):
    """ESL Sensor Information characteristic (0x2BFC).

    org.bluetooth.characteristic.esl_sensor_information

    Variable-length characteristic containing a Mesh Device Property ID
    (uint16) followed by the associated property value bytes.
    """

    _manual_role = CharacteristicRole.INFO
    min_length: int = 2  # property_id (uint16)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> ESLSensorInformationData:
        """Parse ESL sensor information.

        Args:
            data: Raw bytes (2+ bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            ESLSensorInformationData with property_id and raw_data.

        """
        property_id = DataParser.parse_int16(data, 0, signed=False)
        raw_data = bytes(data[2:])
        return ESLSensorInformationData(property_id=property_id, raw_data=raw_data)

    def _encode_value(self, data: ESLSensorInformationData) -> bytearray:
        """Encode ESL sensor information to bytes.

        Args:
            data: ESLSensorInformationData to encode.

        Returns:
            Encoded bytes.

        """
        result = DataParser.encode_int16(data.property_id, signed=False)
        result.extend(data.raw_data)
        return result

"""CGM Session Run Time characteristic implementation.

Implements the CGM Session Run Time characteristic (0x2AAB).

Structure (from GSS YAML):
    CGM Session Run Time (uint16) -- expected run time in hours
    E2E-CRC (uint16, optional) -- present if E2E-CRC Supported

References:
    Bluetooth SIG Continuous Glucose Monitoring Service
    org.bluetooth.characteristic.cgm_session_run_time (GSS YAML)
"""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CGMSessionRunTimeData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from CGM Session Run Time characteristic.

    Attributes:
        run_time_hours: Expected run time of the CGM session in hours.
        e2e_crc: E2E-CRC value. None if absent.

    """

    run_time_hours: int
    e2e_crc: int | None = None


class CGMSessionRunTimeCharacteristic(BaseCharacteristic[CGMSessionRunTimeData]):
    """CGM Session Run Time characteristic (0x2AAB).

    Reports the expected run time of the CGM session in hours.
    """

    expected_type = CGMSessionRunTimeData
    min_length: int = 2  # run_time(2)
    allow_variable_length: bool = True  # optional E2E-CRC

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> CGMSessionRunTimeData:
        """Parse CGM Session Run Time from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic (2 or 4 bytes).
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            CGMSessionRunTimeData with parsed run time.

        """
        run_time_hours = DataParser.parse_int16(data, 0, signed=False)

        _min_length_with_crc = 4
        e2e_crc: int | None = None
        if len(data) >= _min_length_with_crc:
            e2e_crc = DataParser.parse_int16(data, 2, signed=False)

        return CGMSessionRunTimeData(
            run_time_hours=run_time_hours,
            e2e_crc=e2e_crc,
        )

    def _encode_value(self, data: CGMSessionRunTimeData) -> bytearray:
        """Encode CGMSessionRunTimeData back to BLE bytes.

        Args:
            data: CGMSessionRunTimeData instance.

        Returns:
            Encoded bytearray (2 or 4 bytes).

        """
        result = DataParser.encode_int16(data.run_time_hours, signed=False)
        if data.e2e_crc is not None:
            result.extend(DataParser.encode_int16(data.e2e_crc, signed=False))
        return result

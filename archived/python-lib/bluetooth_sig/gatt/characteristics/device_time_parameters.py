"""Device Time Parameters characteristic (0x2B8F).

Per DTS v1.0 Table 3.4, the DT Parameters characteristic is 2-12 octets
depending on which optional features are supported:

  Field                          Condition  Type    Octets  Unit
  E2E_CRC                        C.1        uint16  0 or 2  None
  RTC_Resolution                 M          uint16  2       1/65,536 Second
  Max_RTC_Drift_Limit            C.2        uint16  0 or 2  Seconds
  Max_Days_Until_Sync_Loss       C.2        uint16  0 or 2  Days
  Non_Logged_Time_Adjustment_Limit C.3      uint16  0 or 2  Seconds
  Displayed_Formats              C.4        uint16  0 or 2  N/A

(C.1=E2E-CRC feature; C.2=RTC Drift Tracking feature;
 C.3=Time Change Logging feature; C.4=Displayed Formats feature)

References:
    Bluetooth SIG Device Time Service v1.0, Table 3.4
"""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_MIN_LENGTH = 2


class DeviceTimeParametersData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Device Time Parameters characteristic.

    Attributes:
        rtc_resolution: RTC resolution in 1/65,536-second units (0=unknown).
        max_rtc_drift_limit: Max drift before sync loss, in seconds (optional).
        max_days_until_sync_loss: Max days without sync before loss (optional).
        non_logged_time_adjustment_limit: Non-logged adjustment limit in
            seconds; below this value Base_Time changes are not logged (optional).
        displayed_formats: Device displayed date/time format encoding (optional).
    """

    rtc_resolution: int
    max_rtc_drift_limit: int | None = None
    max_days_until_sync_loss: int | None = None
    non_logged_time_adjustment_limit: int | None = None
    displayed_formats: int | None = None


class DeviceTimeParametersCharacteristic(BaseCharacteristic[DeviceTimeParametersData]):
    """Device Time Parameters characteristic (0x2B8F).

    org.bluetooth.characteristic.device_time_parameters

    Reveals the Server's capabilities and behavioural thresholds for the
    Device Time Service.  The characteristic is 2-12 octets in length
    depending on which optional features are supported.
    """

    min_length = _MIN_LENGTH
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> DeviceTimeParametersData:
        rtc_resolution = DataParser.parse_int16(data, 0, signed=False)

        offset = 2
        max_rtc_drift_limit: int | None = None
        max_days_until_sync_loss: int | None = None
        non_logged_time_adjustment_limit: int | None = None
        displayed_formats: int | None = None

        if len(data) >= offset + 2:
            max_rtc_drift_limit = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        if len(data) >= offset + 2:
            max_days_until_sync_loss = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        if len(data) >= offset + 2:
            non_logged_time_adjustment_limit = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        if len(data) >= offset + 2:
            displayed_formats = DataParser.parse_int16(data, offset, signed=False)

        return DeviceTimeParametersData(
            rtc_resolution=rtc_resolution,
            max_rtc_drift_limit=max_rtc_drift_limit,
            max_days_until_sync_loss=max_days_until_sync_loss,
            non_logged_time_adjustment_limit=non_logged_time_adjustment_limit,
            displayed_formats=displayed_formats,
        )

    def _encode_value(self, data: DeviceTimeParametersData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int16(data.rtc_resolution, signed=False))
        if data.max_rtc_drift_limit is not None:
            result.extend(DataParser.encode_int16(data.max_rtc_drift_limit, signed=False))
        if data.max_days_until_sync_loss is not None:
            result.extend(DataParser.encode_int16(data.max_days_until_sync_loss, signed=False))
        if data.non_logged_time_adjustment_limit is not None:
            result.extend(DataParser.encode_int16(data.non_logged_time_adjustment_limit, signed=False))
        if data.displayed_formats is not None:
            result.extend(DataParser.encode_int16(data.displayed_formats, signed=False))
        return result

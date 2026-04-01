"""IDD Features characteristic (0x2B23).

Composite structure: E2E-CRC (uint16) + E2E-Counter (uint8) +
Insulin Concentration (SFLOAT) + Flags (24-bit).

References:
    Bluetooth SIG Insulin Delivery Service v1.0.1, Table 4.11, 4.12
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser


class IDDFeatureFlags(IntFlag):
    """IDD Feature flags (24-bit) per IDS v1.0.1 Table 4.12."""

    E2E_PROTECTION_SUPPORTED = 0x000001  # bit 0
    BASAL_RATE_SUPPORTED = 0x000002  # bit 1
    TBR_TYPE_ABSOLUTE_SUPPORTED = 0x000004  # bit 2
    TBR_TYPE_RELATIVE_SUPPORTED = 0x000008  # bit 3
    TBR_TEMPLATE_SUPPORTED = 0x000010  # bit 4
    FAST_BOLUS_SUPPORTED = 0x000020  # bit 5
    EXTENDED_BOLUS_SUPPORTED = 0x000040  # bit 6
    MULTIWAVE_BOLUS_SUPPORTED = 0x000080  # bit 7
    BOLUS_DELAY_TIME_SUPPORTED = 0x000100  # bit 8
    BOLUS_TEMPLATE_SUPPORTED = 0x000200  # bit 9
    ISF_PROFILE_TEMPLATE_SUPPORTED = 0x000400  # bit 10
    I2CHO_RATIO_PROFILE_TEMPLATE_SUPPORTED = 0x000800  # bit 11
    TARGET_GLUCOSE_RANGE_PROFILE_TEMPLATE_SUPPORTED = 0x001000  # bit 12
    INSULIN_ON_BOARD_SUPPORTED = 0x008000  # bit 15
    FEATURE_EXTENSION = 0x800000  # bit 23


class IDDFeaturesData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed IDD Features characteristic data.

    Attributes:
        e2e_crc: CRC-CCITT value (0xFFFF if E2E not supported).
        e2e_counter: E2E counter (0x00 if E2E not supported).
        insulin_concentration: Insulin concentration as SFLOAT.
        flags: Supported feature flags (24-bit).

    """

    e2e_crc: int
    e2e_counter: int
    insulin_concentration: float
    flags: IDDFeatureFlags


class IDDFeaturesCharacteristic(BaseCharacteristic[IDDFeaturesData]):
    """IDD Features characteristic (0x2B23).

    org.bluetooth.characteristic.idd_features

    Reports supported features of the Insulin Delivery Device.
    Structure: E2E-CRC(2) + E2E-Counter(1) + InsulinConcentration(2) + Flags(3) = 8 bytes.
    """

    min_length = 8
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IDDFeaturesData:
        """Parse IDD Features data per IDS v1.0.1 Table 4.11."""
        e2e_crc = DataParser.parse_int16(data, 0, signed=False)
        e2e_counter = DataParser.parse_int8(data, 2, signed=False)
        insulin_concentration = IEEE11073Parser.parse_sfloat(data, 3)
        flags_raw = DataParser.parse_int24(data, 5, signed=False)
        flags = IDDFeatureFlags(flags_raw)
        return IDDFeaturesData(
            e2e_crc=e2e_crc,
            e2e_counter=e2e_counter,
            insulin_concentration=insulin_concentration,
            flags=flags,
        )

    def _encode_value(self, data: IDDFeaturesData) -> bytearray:
        """Encode IDD Features data."""
        result = bytearray()
        result.extend(DataParser.encode_int16(data.e2e_crc, signed=False))
        result.extend(DataParser.encode_int8(data.e2e_counter, signed=False))
        result.extend(IEEE11073Parser.encode_sfloat(data.insulin_concentration))
        result.extend(DataParser.encode_int24(int(data.flags), signed=False))
        return result

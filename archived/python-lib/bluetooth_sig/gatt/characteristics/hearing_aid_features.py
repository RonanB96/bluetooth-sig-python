"""Hearing Aid Features characteristic (0x2BDA)."""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class HearingAidType(IntEnum):
    """Hearing Aid Type as per HAS 1.0, Section 3.1 (bits 0-1)."""

    BINAURAL = 0x00
    MONAURAL = 0x01
    BANDED = 0x02


class HearingAidFeatureFlags(IntFlag):
    """Hearing Aid feature flags as per HAS 1.0, Section 3.1 (bits 2-5)."""

    PRESET_SYNCHRONIZATION_SUPPORT = 0x04
    INDEPENDENT_PRESETS = 0x08
    DYNAMIC_PRESETS = 0x10
    WRITABLE_PRESETS = 0x20


class HearingAidFeaturesData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Hearing Aid Features characteristic."""

    hearing_aid_type: HearingAidType
    preset_synchronization_support: bool
    independent_presets: bool
    dynamic_presets: bool
    writable_presets: bool


class HearingAidFeaturesCharacteristic(BaseCharacteristic[HearingAidFeaturesData]):
    """Hearing Aid Features characteristic (0x2BDA).

    org.bluetooth.characteristic.hearing_aid_features

    1-octet bitfield: bits 0-1 = Hearing Aid Type enum,
    bits 2-5 = feature flags.

    References:
        Hearing Access Service 1.0, Section 3.1
    """

    expected_length = 1

    _HEARING_AID_TYPE_MASK = 0x03

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> HearingAidFeaturesData:
        raw = DataParser.parse_int8(data, 0, signed=False)
        hearing_aid_type = HearingAidType(raw & self._HEARING_AID_TYPE_MASK)

        return HearingAidFeaturesData(
            hearing_aid_type=hearing_aid_type,
            preset_synchronization_support=bool(raw & HearingAidFeatureFlags.PRESET_SYNCHRONIZATION_SUPPORT),
            independent_presets=bool(raw & HearingAidFeatureFlags.INDEPENDENT_PRESETS),
            dynamic_presets=bool(raw & HearingAidFeatureFlags.DYNAMIC_PRESETS),
            writable_presets=bool(raw & HearingAidFeatureFlags.WRITABLE_PRESETS),
        )

    def _encode_value(self, data: HearingAidFeaturesData) -> bytearray:
        raw = int(data.hearing_aid_type)
        if data.preset_synchronization_support:
            raw |= HearingAidFeatureFlags.PRESET_SYNCHRONIZATION_SUPPORT
        if data.independent_presets:
            raw |= HearingAidFeatureFlags.INDEPENDENT_PRESETS
        if data.dynamic_presets:
            raw |= HearingAidFeatureFlags.DYNAMIC_PRESETS
        if data.writable_presets:
            raw |= HearingAidFeatureFlags.WRITABLE_PRESETS

        return DataParser.encode_int8(raw, signed=False)

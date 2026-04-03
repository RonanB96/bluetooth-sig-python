"""OTS Feature characteristic (0x2ABD)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class OACPFeatures(IntFlag):
    """Object Action Control Point feature flags."""

    CREATE = 0x00000001
    DELETE = 0x00000002
    CALCULATE_CHECKSUM = 0x00000004
    EXECUTE = 0x00000008
    READ = 0x00000010
    WRITE = 0x00000020
    APPEND = 0x00000040
    TRUNCATE = 0x00000080
    PATCH = 0x00000100
    ABORT = 0x00000200


class OLCPFeatures(IntFlag):
    """Object List Control Point feature flags."""

    GO_TO = 0x00000001
    ORDER = 0x00000002
    REQUEST_NUMBER_OF_OBJECTS = 0x00000004
    CLEAR_MARKING = 0x00000008


class OTSFeatureData(msgspec.Struct, frozen=True):
    """OTS Feature characteristic data.

    Attributes:
        oacp_features: OACP features bitmap (uint32).
        olcp_features: OLCP features bitmap (uint32).
    """

    oacp_features: OACPFeatures
    olcp_features: OLCPFeatures


class OTSFeatureCharacteristic(BaseCharacteristic[OTSFeatureData]):
    """OTS Feature characteristic (0x2ABD).

    org.bluetooth.characteristic.ots_feature

    Contains two uint32 fields: OACP features and OLCP features.
    """

    expected_length: int = 8

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> OTSFeatureData:
        oacp = OACPFeatures(int.from_bytes(data[0:4], byteorder="little", signed=False))
        olcp = OLCPFeatures(int.from_bytes(data[4:8], byteorder="little", signed=False))
        return OTSFeatureData(oacp_features=oacp, olcp_features=olcp)

    def _encode_value(self, data: OTSFeatureData) -> bytearray:
        result = bytearray()
        result.extend(int(data.oacp_features).to_bytes(4, byteorder="little", signed=False))
        result.extend(int(data.olcp_features).to_bytes(4, byteorder="little", signed=False))
        return result

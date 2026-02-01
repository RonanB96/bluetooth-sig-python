"""Extended advertising field types (BLE 5.0+).

Constant Tone Extension, Advertising Data Info, Auxiliary Pointer, and Sync Info.
"""

from __future__ import annotations

from enum import IntEnum

import msgspec


class CTEType(IntEnum):
    """Constant Tone Extension (CTE) Types (Core Spec Vol 6, Part B, Section 2.5)."""

    AOA = 0x00  # Angle of Arrival
    AOD_1US = 0x01  # Angle of Departure with 1μs slots
    AOD_2US = 0x02  # Angle of Departure with 2μs slots


class CTEInfo(msgspec.Struct, kw_only=True):
    """Constant Tone Extension (CTE) information (BLE 5.1+ Direction Finding).

    Attributes:
        cte_time: CTE length in 8μs units (0-19, representing 16-160μs)
        cte_type: Type of CTE (AoA, AoD 1μs, or AoD 2μs)
    """

    cte_time: int
    cte_type: CTEType


class AdvertisingDataInfo(msgspec.Struct, kw_only=True):
    """Advertising Data Info (ADI) field (BLE 5.0+).

    Attributes:
        advertising_data_id: Advertising Data ID (DID) - 12 bits
        advertising_set_id: Advertising Set ID (SID) - 4 bits
    """

    advertising_data_id: int  # 12-bit DID (0-4095)
    advertising_set_id: int  # 4-bit SID (0-15)


class PHYType(IntEnum):
    """PHY types for auxiliary channel (Core Spec Vol 6, Part B, Section 2.3.4.6)."""

    LE_1M = 0x00
    LE_2M = 0x01
    LE_CODED = 0x02


class AuxiliaryPointer(msgspec.Struct, kw_only=True):
    """Auxiliary Pointer for chaining extended advertising packets (BLE 5.0+).

    Attributes:
        channel_index: Advertising channel index (0-39)
        ca: Clock accuracy (0=51-500ppm, 1=0-50ppm)
        offset_units: Units for aux_offset (0=30μs, 1=300μs)
        aux_offset: Time offset to auxiliary packet (13 bits)
        aux_phy: PHY used for auxiliary packet
    """

    channel_index: int  # 0-39
    ca: bool
    offset_units: int  # 0 or 1
    aux_offset: int  # 13-bit value
    aux_phy: PHYType


class SyncInfo(msgspec.Struct, kw_only=True):
    """Synchronization Info for Periodic Advertising (BLE 5.0+).

    Attributes:
        sync_packet_offset: Offset to first periodic advertising packet (13 bits, 30μs units)
        offset_units: Units for sync_packet_offset (0=30μs, 1=300μs)
        interval: Periodic advertising interval (1.25ms units, range: 7.5ms-81.91875s)
        channel_map: Channel map for periodic advertising (37 bits)
        sleep_clock_accuracy: Sleep clock accuracy (0-7, represents ppm ranges)
        advertising_address: Advertiser address (6 bytes)
        advertising_address_type: 0=Public, 1=Random
        sync_counter: Synchronization counter for packet identification
    """

    sync_packet_offset: int  # 13 bits
    offset_units: int  # 0 or 1
    interval: int  # Periodic advertising interval in 1.25ms units
    channel_map: int  # 37-bit channel map
    sleep_clock_accuracy: int  # 0-7 (ppm ranges)
    advertising_address: str  # MAC address
    advertising_address_type: int  # 0 or 1
    sync_counter: int  # Packet counter

"""Shared parsing/encoding utilities for Fitness Machine Service characteristics.

All six Fitness Machine data characteristics (treadmill, indoor bike, cross
trainer, rower, stair climber, step climber) share the same trailing optional
field blocks: energy triplet, heart rate, metabolic equivalent, elapsed time,
and remaining time.  This module provides reusable helpers so each
characteristic only has to implement its own unique fields.

References:
    Bluetooth SIG Fitness Machine Service 1.0
    org.bluetooth.characteristic.{treadmill,indoor_bike,cross_trainer,
        rower,stair_climber,step_climber}_data YAML specs in GSS submodule
"""

from __future__ import annotations

from .utils import DataParser

# ---------------------------------------------------------------------------
# Scaling constants (from YAML M/d/b parameters)
# ---------------------------------------------------------------------------
MET_RESOLUTION = 10.0  # M=1, d=-1, b=0 -> raw / 10

# ---------------------------------------------------------------------------
# Decode helpers
# ---------------------------------------------------------------------------


def decode_energy_triplet(data: bytearray, offset: int) -> tuple[int | None, int | None, int | None, int]:
    """Decode the shared Energy triplet (Total + Per Hour + Per Minute).

    Wire format: uint16 + uint16 + uint8 = 5 bytes, all gated by a single
    flag bit.

    Args:
        data: Raw BLE bytes.
        offset: Current read position.

    Returns:
        (total_energy, energy_per_hour, energy_per_minute, new_offset)

    """
    if len(data) < offset + 5:
        return None, None, None, offset
    total_energy = DataParser.parse_int16(data, offset, signed=False)
    energy_per_hour = DataParser.parse_int16(data, offset + 2, signed=False)
    energy_per_minute = DataParser.parse_int8(data, offset + 4, signed=False)
    return total_energy, energy_per_hour, energy_per_minute, offset + 5


def decode_heart_rate(data: bytearray, offset: int) -> tuple[int | None, int]:
    """Decode the shared Heart Rate field (uint8, bpm).

    Args:
        data: Raw BLE bytes.
        offset: Current read position.

    Returns:
        (heart_rate, new_offset)

    """
    if len(data) < offset + 1:
        return None, offset
    return DataParser.parse_int8(data, offset, signed=False), offset + 1


def decode_metabolic_equivalent(data: bytearray, offset: int) -> tuple[float | None, int]:
    """Decode the shared Metabolic Equivalent field (uint8, M=1 d=-1 b=0).

    Args:
        data: Raw BLE bytes.
        offset: Current read position.

    Returns:
        (metabolic_equivalent, new_offset)

    """
    if len(data) < offset + 1:
        return None, offset
    raw = DataParser.parse_int8(data, offset, signed=False)
    return raw / MET_RESOLUTION, offset + 1


def decode_elapsed_time(data: bytearray, offset: int) -> tuple[int | None, int]:
    """Decode the shared Elapsed Time field (uint16, seconds).

    Args:
        data: Raw BLE bytes.
        offset: Current read position.

    Returns:
        (elapsed_time, new_offset)

    """
    if len(data) < offset + 2:
        return None, offset
    return DataParser.parse_int16(data, offset, signed=False), offset + 2


def decode_remaining_time(data: bytearray, offset: int) -> tuple[int | None, int]:
    """Decode the shared Remaining Time field (uint16, seconds).

    Args:
        data: Raw BLE bytes.
        offset: Current read position.

    Returns:
        (remaining_time, new_offset)

    """
    if len(data) < offset + 2:
        return None, offset
    return DataParser.parse_int16(data, offset, signed=False), offset + 2


# ---------------------------------------------------------------------------
# Encode helpers
# ---------------------------------------------------------------------------


def encode_energy_triplet(
    total_energy: int | None,
    energy_per_hour: int | None,
    energy_per_minute: int | None,
) -> bytearray:
    """Encode the shared Energy triplet (Total + Per Hour + Per Minute).

    Args:
        total_energy: Total energy in kcal (uint16).
        energy_per_hour: Energy per hour in kcal (uint16).
        energy_per_minute: Energy per minute in kcal (uint8).

    Returns:
        5-byte bytearray (uint16 + uint16 + uint8).

    """
    result = bytearray()
    result.extend(DataParser.encode_int16(total_energy if total_energy is not None else 0, signed=False))
    result.extend(DataParser.encode_int16(energy_per_hour if energy_per_hour is not None else 0, signed=False))
    result.extend(DataParser.encode_int8(energy_per_minute if energy_per_minute is not None else 0, signed=False))
    return result


def encode_heart_rate(heart_rate: int) -> bytearray:
    """Encode the shared Heart Rate field (uint8, bpm).

    Args:
        heart_rate: Heart rate in bpm (uint8).

    Returns:
        1-byte bytearray.

    """
    return DataParser.encode_int8(heart_rate, signed=False)


def encode_metabolic_equivalent(metabolic_equivalent: float) -> bytearray:
    """Encode the shared Metabolic Equivalent field (uint8, M=1 d=-1 b=0).

    Args:
        metabolic_equivalent: Metabolic equivalent value (real).

    Returns:
        1-byte bytearray.

    """
    raw = round(metabolic_equivalent * MET_RESOLUTION)
    return DataParser.encode_int8(raw, signed=False)


def encode_elapsed_time(elapsed_time: int) -> bytearray:
    """Encode the shared Elapsed Time field (uint16, seconds).

    Args:
        elapsed_time: Elapsed time in seconds (uint16).

    Returns:
        2-byte bytearray.

    """
    return DataParser.encode_int16(elapsed_time, signed=False)


def encode_remaining_time(remaining_time: int) -> bytearray:
    """Encode the shared Remaining Time field (uint16, seconds).

    Args:
        remaining_time: Remaining time in seconds (uint16).

    Returns:
        2-byte bytearray.

    """
    return DataParser.encode_int16(remaining_time, signed=False)

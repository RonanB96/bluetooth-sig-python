"""IEEE 11073 medical device format support utilities."""

from __future__ import annotations

import math
import struct
from datetime import MAXYEAR, datetime

from ...exceptions import InsufficientDataError, ValueRangeError
from .bit_field_utils import BitFieldUtils


class IEEE11073Parser:
    """Utility class for IEEE-11073 medical device format support."""

    # IEEE-11073 SFLOAT (16-bit) constants
    SFLOAT_MANTISSA_MASK = 0x0FFF
    SFLOAT_MANTISSA_SIGN_BIT = 0x0800
    SFLOAT_MANTISSA_CONVERSION = 0x1000
    SFLOAT_EXPONENT_MASK = 0x0F
    SFLOAT_EXPONENT_SIGN_BIT = 0x08
    SFLOAT_EXPONENT_CONVERSION = 0x10
    SFLOAT_MANTISSA_MAX = 2048
    SFLOAT_EXPONENT_MIN = -8
    SFLOAT_EXPONENT_MAX = 7
    # Bit field positions and widths (no magic numbers)
    SFLOAT_MANTISSA_START_BIT = 0
    SFLOAT_MANTISSA_BIT_WIDTH = 12
    SFLOAT_EXPONENT_START_BIT = 12
    SFLOAT_EXPONENT_BIT_WIDTH = 4

    # IEEE-11073 SFLOAT (16-bit) special values
    SFLOAT_NAN = 0x07FF
    SFLOAT_NRES = 0x0800  # NRes (Not a valid result) - treated as NaN
    SFLOAT_POSITIVE_INFINITY = 0x07FE
    SFLOAT_NEGATIVE_INFINITY = 0x0802

    # IEEE-11073 FLOAT32 (32-bit) constants
    FLOAT32_NAN = 0x007FFFFF
    FLOAT32_POSITIVE_INFINITY = 0x00800000
    FLOAT32_NEGATIVE_INFINITY = 0x00800001
    FLOAT32_NRES = 0x00800002
    FLOAT32_MANTISSA_MASK = 0x00FFFFFF
    FLOAT32_MANTISSA_SIGN_BIT = 0x00800000
    FLOAT32_MANTISSA_CONVERSION = 0x01000000
    FLOAT32_EXPONENT_MASK = 0xFF
    FLOAT32_EXPONENT_SIGN_BIT = 0x80
    FLOAT32_EXPONENT_CONVERSION = 0x100
    FLOAT32_MANTISSA_MAX = 8388608  # 2^23
    FLOAT32_EXPONENT_MIN = -8
    FLOAT32_EXPONENT_MAX = 7
    # Bit field positions and widths (no magic numbers)
    FLOAT32_MANTISSA_START_BIT = 0
    FLOAT32_MANTISSA_BIT_WIDTH = 24
    FLOAT32_EXPONENT_START_BIT = 24
    FLOAT32_EXPONENT_BIT_WIDTH = 8

    # IEEE-11073 timestamp validation constants
    IEEE11073_MIN_YEAR = 1582  # Gregorian calendar adoption year (per Bluetooth SIG spec)
    MONTH_MIN = 1
    MONTH_MAX = 12
    DAY_MIN = 1
    DAY_MAX = 31  # Simplified validation - actual days depend on month/year
    HOUR_MIN = 0
    HOUR_MAX = 23  # 24-hour format
    MINUTE_MIN = 0
    MINUTE_MAX = 59
    SECOND_MIN = 0
    SECOND_MAX = 59

    # Common constants
    TIMESTAMP_LENGTH = 7

    @staticmethod
    def parse_sfloat(data: bytes | bytearray, offset: int = 0) -> float:
        """Parse IEEE 11073 16-bit SFLOAT.

        Args:
            data: Raw bytes/bytearray
            offset: Offset in the data

        """
        if len(data) < offset + 2:
            raise InsufficientDataError("IEEE 11073 SFLOAT", data[offset:], 2)
        raw_value = int.from_bytes(data[offset : offset + 2], byteorder="little")

        # Handle special values
        if raw_value == IEEE11073Parser.SFLOAT_NAN:
            return float("nan")  # NaN
        if raw_value == IEEE11073Parser.SFLOAT_NRES:
            return float("nan")  # NRes (Not a valid result)
        if raw_value == IEEE11073Parser.SFLOAT_POSITIVE_INFINITY:
            return float("inf")  # +INFINITY
        if raw_value == IEEE11073Parser.SFLOAT_NEGATIVE_INFINITY:
            return float("-inf")  # -INFINITY

        # Extract mantissa and exponent
        mantissa = BitFieldUtils.extract_bits(raw_value, IEEE11073Parser.SFLOAT_MANTISSA_MASK)
        if mantissa >= IEEE11073Parser.SFLOAT_MANTISSA_SIGN_BIT:  # Negative mantissa
            mantissa = mantissa - IEEE11073Parser.SFLOAT_MANTISSA_CONVERSION

        exponent = BitFieldUtils.extract_bit_field_from_mask(
            raw_value,
            IEEE11073Parser.SFLOAT_EXPONENT_MASK,
            IEEE11073Parser.SFLOAT_EXPONENT_START_BIT,
        )
        if exponent >= IEEE11073Parser.SFLOAT_EXPONENT_SIGN_BIT:  # Negative exponent
            exponent = exponent - IEEE11073Parser.SFLOAT_EXPONENT_CONVERSION

        return float(mantissa * (10.0**exponent))

    @staticmethod
    def parse_float32(data: bytes | bytearray, offset: int = 0) -> float:
        """Parse IEEE 11073 32-bit FLOAT."""
        if len(data) < offset + 4:
            raise InsufficientDataError("IEEE 11073 FLOAT32", data[offset:], 4)

        raw_value = int.from_bytes(data[offset : offset + 4], byteorder="little")

        # Handle special values (similar to SFLOAT but 32-bit)
        if raw_value == IEEE11073Parser.FLOAT32_NAN:
            return float("nan")
        if raw_value == IEEE11073Parser.FLOAT32_POSITIVE_INFINITY:
            return float("inf")
        if raw_value == IEEE11073Parser.FLOAT32_NEGATIVE_INFINITY:
            return float("-inf")
        if raw_value == IEEE11073Parser.FLOAT32_NRES:
            return float("nan")  # NRes (Not a valid result)

        # Extract mantissa (24-bit) and exponent (8-bit)
        mantissa = BitFieldUtils.extract_bits(raw_value, IEEE11073Parser.FLOAT32_MANTISSA_MASK)
        if mantissa >= IEEE11073Parser.FLOAT32_MANTISSA_SIGN_BIT:  # Negative mantissa
            mantissa = mantissa - IEEE11073Parser.FLOAT32_MANTISSA_CONVERSION

        exponent = BitFieldUtils.extract_bit_field_from_mask(
            raw_value,
            IEEE11073Parser.FLOAT32_EXPONENT_MASK,
            IEEE11073Parser.FLOAT32_EXPONENT_START_BIT,
        )
        if exponent >= IEEE11073Parser.FLOAT32_EXPONENT_SIGN_BIT:  # Negative exponent
            exponent = exponent - IEEE11073Parser.FLOAT32_EXPONENT_CONVERSION

        return float(mantissa * (10**exponent))

    @staticmethod
    def encode_sfloat(value: float) -> bytearray:
        """Encode float to IEEE 11073 16-bit SFLOAT."""
        if math.isnan(value):
            return bytearray(IEEE11073Parser.SFLOAT_NAN.to_bytes(2, byteorder="little"))
        if math.isinf(value):
            if value > 0:
                return bytearray(IEEE11073Parser.SFLOAT_POSITIVE_INFINITY.to_bytes(2, byteorder="little"))
            return bytearray(IEEE11073Parser.SFLOAT_NEGATIVE_INFINITY.to_bytes(2, byteorder="little"))

        # Find best exponent and mantissa representation
        exponent = 0
        mantissa = value

        while abs(mantissa) >= IEEE11073Parser.SFLOAT_MANTISSA_MAX and exponent < IEEE11073Parser.SFLOAT_EXPONENT_MAX:
            mantissa /= 10
            exponent += 1

        while abs(mantissa) < 1 and mantissa != 0 and exponent > IEEE11073Parser.SFLOAT_EXPONENT_MIN:
            mantissa *= 10
            exponent -= 1

        mantissa_int = int(round(mantissa))

        # Pack into 16-bit value
        if exponent < 0:
            exponent = exponent + IEEE11073Parser.SFLOAT_EXPONENT_CONVERSION
        if mantissa_int < 0:
            mantissa_int = mantissa_int + IEEE11073Parser.SFLOAT_MANTISSA_CONVERSION

        raw_value = BitFieldUtils.merge_bit_fields(
            (
                mantissa_int,
                IEEE11073Parser.SFLOAT_MANTISSA_START_BIT,
                IEEE11073Parser.SFLOAT_MANTISSA_BIT_WIDTH,
            ),
            (
                exponent,
                IEEE11073Parser.SFLOAT_EXPONENT_START_BIT,
                IEEE11073Parser.SFLOAT_EXPONENT_BIT_WIDTH,
            ),
        )
        return bytearray(raw_value.to_bytes(2, byteorder="little"))

    @staticmethod
    def encode_float32(value: float) -> bytearray:
        """Encode float to IEEE 11073 32-bit FLOAT."""
        if math.isnan(value):
            return bytearray(IEEE11073Parser.FLOAT32_NAN.to_bytes(4, byteorder="little"))
        if math.isinf(value):
            if value > 0:
                return bytearray(IEEE11073Parser.FLOAT32_POSITIVE_INFINITY.to_bytes(4, byteorder="little"))
            return bytearray(IEEE11073Parser.FLOAT32_NEGATIVE_INFINITY.to_bytes(4, byteorder="little"))

        if value == 0.0:
            return bytearray([0x00, 0x00, 0x00, 0x00])

        # Find the best representation by trying different exponents
        # IEEE-11073 32-bit FLOAT: 24-bit signed mantissa + 8-bit signed exponent
        best_mantissa = 0
        best_exponent = 0
        best_error = float("inf")

        # Try exponents from min to max (reasonable range for medical values)
        for exp in range(
            IEEE11073Parser.FLOAT32_EXPONENT_MIN,
            IEEE11073Parser.FLOAT32_EXPONENT_MAX + 1,
        ):
            # Calculate what mantissa would be with this exponent
            potential_mantissa = value * (10 ** (-exp))

            # Check if mantissa fits in 24-bit signed range
            if abs(potential_mantissa) < IEEE11073Parser.FLOAT32_MANTISSA_MAX:
                # Round to integer
                mantissa_int = round(potential_mantissa)

                # Calculate the actual value this would represent
                actual_value = mantissa_int * (10**exp)
                error = abs(value - actual_value)

                # Use this if it's better (less error) or if it's exact
                if error < best_error:
                    best_error = error
                    best_mantissa = mantissa_int
                    best_exponent = exp

                    # If we found an exact representation, use it
                    if error == 0.0:
                        break

        # Validate mantissa fits in 24-bit signed range
        if abs(best_mantissa) >= IEEE11073Parser.FLOAT32_MANTISSA_MAX:
            raise ValueRangeError(
                "IEEE-11073 FLOAT32 mantissa",
                best_mantissa,
                -(IEEE11073Parser.FLOAT32_MANTISSA_MAX - 1),
                IEEE11073Parser.FLOAT32_MANTISSA_MAX - 1,
            )

        # Pack into 32-bit value: mantissa (24-bit signed) + exponent (8-bit signed)
        # Convert signed values to unsigned for bit packing
        mantissa_unsigned = (
            best_mantissa if best_mantissa >= 0 else best_mantissa + IEEE11073Parser.FLOAT32_MANTISSA_CONVERSION
        )
        exponent_unsigned = (
            best_exponent if best_exponent >= 0 else best_exponent + IEEE11073Parser.FLOAT32_EXPONENT_CONVERSION
        )

        raw_value = BitFieldUtils.merge_bit_fields(
            (
                mantissa_unsigned,
                IEEE11073Parser.FLOAT32_MANTISSA_START_BIT,
                IEEE11073Parser.FLOAT32_MANTISSA_BIT_WIDTH,
            ),
            (
                exponent_unsigned,
                IEEE11073Parser.FLOAT32_EXPONENT_START_BIT,
                IEEE11073Parser.FLOAT32_EXPONENT_BIT_WIDTH,
            ),
        )
        return bytearray(raw_value.to_bytes(4, byteorder="little"))

    @staticmethod
    def parse_timestamp(data: bytearray, offset: int) -> datetime:
        """Parse IEEE-11073 timestamp format (7 bytes)."""
        if len(data) < offset + IEEE11073Parser.TIMESTAMP_LENGTH:
            raise InsufficientDataError("IEEE 11073 timestamp", data[offset:], IEEE11073Parser.TIMESTAMP_LENGTH)

        timestamp_data = data[offset : offset + IEEE11073Parser.TIMESTAMP_LENGTH]
        year, month, day, hours, minutes, seconds = struct.unpack("<HBBBBB", timestamp_data)
        return datetime(year, month, day, hours, minutes, seconds)

    @staticmethod
    def encode_timestamp(timestamp: datetime) -> bytearray:
        """Encode timestamp to IEEE-11073 7-byte format."""
        # Validate ranges per IEEE-11073 specification
        if not IEEE11073Parser.IEEE11073_MIN_YEAR <= timestamp.year <= MAXYEAR:
            raise ValueRangeError("year", timestamp.year, IEEE11073Parser.IEEE11073_MIN_YEAR, MAXYEAR)
        if not IEEE11073Parser.MONTH_MIN <= timestamp.month <= IEEE11073Parser.MONTH_MAX:
            raise ValueRangeError(
                "month",
                timestamp.month,
                IEEE11073Parser.MONTH_MIN,
                IEEE11073Parser.MONTH_MAX,
            )
        if not IEEE11073Parser.DAY_MIN <= timestamp.day <= IEEE11073Parser.DAY_MAX:
            raise ValueRangeError("day", timestamp.day, IEEE11073Parser.DAY_MIN, IEEE11073Parser.DAY_MAX)
        if not IEEE11073Parser.HOUR_MIN <= timestamp.hour <= IEEE11073Parser.HOUR_MAX:
            raise ValueRangeError(
                "hour",
                timestamp.hour,
                IEEE11073Parser.HOUR_MIN,
                IEEE11073Parser.HOUR_MAX,
            )
        if not IEEE11073Parser.MINUTE_MIN <= timestamp.minute <= IEEE11073Parser.MINUTE_MAX:
            raise ValueRangeError(
                "minute",
                timestamp.minute,
                IEEE11073Parser.MINUTE_MIN,
                IEEE11073Parser.MINUTE_MAX,
            )
        if not IEEE11073Parser.SECOND_MIN <= timestamp.second <= IEEE11073Parser.SECOND_MAX:
            raise ValueRangeError(
                "second",
                timestamp.second,
                IEEE11073Parser.SECOND_MIN,
                IEEE11073Parser.SECOND_MAX,
            )

        return bytearray(
            struct.pack(
                "<HBBBBB",
                timestamp.year,
                timestamp.month,
                timestamp.day,
                timestamp.hour,
                timestamp.minute,
                timestamp.second,
            )
        )

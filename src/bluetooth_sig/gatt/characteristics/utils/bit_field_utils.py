"""Bit field manipulation and flag handling utilities."""

from __future__ import annotations


class BitPositions:  # pylint: disable=too-few-public-methods
    """Common bit position constants for flag manipulation."""

    # Common flag bit positions
    BIT_0 = 1 << 0
    BIT_1 = 1 << 1
    BIT_2 = 1 << 2
    BIT_3 = 1 << 3
    BIT_4 = 1 << 4
    BIT_5 = 1 << 5
    BIT_6 = 1 << 6
    BIT_7 = 1 << 7


class BitFieldUtils:  # pylint: disable=too-many-public-methods
    """Utility class for bit field manipulation and flag handling."""

    # Common bit operation constants
    SINGLE_BIT_MASK = 1
    DEFAULT_BIT_WIDTH = 32

    @staticmethod
    def extract_bit_field(value: int, start_bit: int, num_bits: int) -> int:
        """Extract a bit field from an integer value."""
        if num_bits <= 0 or start_bit < 0:
            raise ValueError("Invalid bit field parameters")
        mask = (1 << num_bits) - 1
        return (value >> start_bit) & mask

    @staticmethod
    def set_bit_field(value: int, field_value: int, start_bit: int, num_bits: int) -> int:
        """Set a bit field in an integer value."""
        if num_bits <= 0 or start_bit < 0:
            raise ValueError("Invalid bit field parameters")
        mask = (BitFieldUtils.SINGLE_BIT_MASK << num_bits) - 1
        if field_value > mask:
            raise ValueError(f"Field value {field_value} exceeds {num_bits}-bit capacity")
        # Clear the field and set new value
        value &= ~(mask << start_bit)
        value |= (field_value & mask) << start_bit
        return value

    @staticmethod
    def create_bitmask(start_bit: int, num_bits: int) -> int:
        """Create a bitmask for a specific bit field range."""
        if num_bits <= 0 or start_bit < 0:
            raise ValueError("Invalid bitmask parameters")
        mask = (1 << num_bits) - 1
        return mask << start_bit

    @staticmethod
    def test_bit(value: int, bit_position: int) -> bool:
        """Test if a specific bit is set in the value."""
        if bit_position < 0:
            raise ValueError("Bit position must be non-negative")
        return bool(value & (BitFieldUtils.SINGLE_BIT_MASK << bit_position))

    @staticmethod
    def test_bits_any(value: int, bitmask: int) -> bool:
        """Test if any bits in the bitmask are set in the value."""
        return bool(value & bitmask)

    @staticmethod
    def test_bits_all(value: int, bitmask: int) -> bool:
        """Test if all bits in the bitmask are set in the value."""
        return (value & bitmask) == bitmask

    @staticmethod
    def set_bit(value: int, bit_position: int) -> int:
        """Set a specific bit in the value."""
        if bit_position < 0:
            raise ValueError("Bit position must be non-negative")
        return value | (BitFieldUtils.SINGLE_BIT_MASK << bit_position)

    @staticmethod
    def clear_bit(value: int, bit_position: int) -> int:
        """Clear a specific bit in the value."""
        if bit_position < 0:
            raise ValueError("Bit position must be non-negative")
        return value & ~(BitFieldUtils.SINGLE_BIT_MASK << bit_position)

    @staticmethod
    def toggle_bit(value: int, bit_position: int) -> int:
        """Toggle a specific bit in the value."""
        if bit_position < 0:
            raise ValueError("Bit position must be non-negative")
        return value ^ (BitFieldUtils.SINGLE_BIT_MASK << bit_position)

    @staticmethod
    def extract_bits(value: int, bitmask: int) -> int:
        """Extract bits from value using a bitmask."""
        return value & bitmask

    @staticmethod
    def set_bits(value: int, bitmask: int) -> int:
        """Set all bits specified in the bitmask."""
        return value | bitmask

    @staticmethod
    def clear_bits(value: int, bitmask: int) -> int:
        """Clear all bits specified in the bitmask."""
        return value & ~bitmask

    @staticmethod
    def toggle_bits(value: int, bitmask: int) -> int:
        """Toggle all bits specified in the bitmask."""
        return value ^ bitmask

    @staticmethod
    def count_set_bits(value: int) -> int:
        """Count the number of set bits in the value."""
        count = 0
        while value:
            count += value & 1
            value >>= 1
        return count

    @staticmethod
    def get_bit_positions(value: int) -> list[int]:
        """Get a list of positions of all set bits in the value."""
        positions: list[int] = []
        bit_pos = 0
        while value:
            if value & 1:
                positions.append(bit_pos)
            value >>= 1
            bit_pos += 1
        return positions

    @staticmethod
    def find_first_set_bit(value: int) -> int | None:
        """Find the position of the first (least significant) set bit."""
        if value == 0:
            return None
        position = 0
        while (value & 1) == 0:
            value >>= 1
            position += 1
        return position

    @staticmethod
    def find_last_set_bit(value: int) -> int | None:
        """Find the position of the last (most significant) set bit."""
        if value == 0:
            return None
        position = 0
        while value > 1:
            value >>= 1
            position += 1
        return position

    @staticmethod
    def reverse_bits(value: int, bit_width: int = DEFAULT_BIT_WIDTH) -> int:
        """Reverse the bits in a value within the specified bit width."""
        result = 0
        for i in range(bit_width):
            if value & (1 << i):
                result |= 1 << (bit_width - 1 - i)
        return result

    @staticmethod
    def calculate_parity(value: int) -> int:
        """Calculate the parity (even/odd) of set bits.

        Returns 0 for even, 1 for odd.
        """
        parity = 0
        while value:
            parity ^= value & 1
            value >>= 1
        return parity

    @staticmethod
    def validate_bit_field_range(start_bit: int, num_bits: int, total_bits: int = DEFAULT_BIT_WIDTH) -> bool:
        """Validate that a bit field range is within bounds."""
        return start_bit >= 0 and num_bits > 0 and start_bit + num_bits <= total_bits

    @staticmethod
    def copy_bit_field(source: int, dest: int, source_start: int, dest_start: int, num_bits: int) -> int:
        """Copy a bit field from source to destination."""
        field_value = BitFieldUtils.extract_bit_field(source, source_start, num_bits)
        return BitFieldUtils.set_bit_field(dest, field_value, dest_start, num_bits)

    @staticmethod
    def shift_bit_field_left(value: int, start_bit: int, num_bits: int, shift_amount: int) -> int:
        """Shift a bit field left within the value."""
        if shift_amount <= 0:
            return value
        field_value = BitFieldUtils.extract_bit_field(value, start_bit, num_bits)
        # Clear the original field
        value = BitFieldUtils.set_bit_field(value, 0, start_bit, num_bits)
        # Set the shifted field
        new_start = start_bit + shift_amount
        return BitFieldUtils.set_bit_field(value, field_value, new_start, num_bits)

    @staticmethod
    def shift_bit_field_right(value: int, start_bit: int, num_bits: int, shift_amount: int) -> int:
        """Shift a bit field right within the value."""
        if shift_amount <= 0:
            return value
        field_value = BitFieldUtils.extract_bit_field(value, start_bit, num_bits)
        # Clear the original field
        value = BitFieldUtils.set_bit_field(value, 0, start_bit, num_bits)
        # Set the shifted field
        new_start = max(0, start_bit - shift_amount)
        return BitFieldUtils.set_bit_field(value, field_value, new_start, num_bits)

    @staticmethod
    def merge_bit_fields(*fields: tuple[int, int, int]) -> int:
        """Merge multiple bit fields into a single value.

        Args:
            fields: Tuples of (field_value, start_bit, num_bits)
        """
        result = 0
        for field_value, start_bit, num_bits in fields:
            result = BitFieldUtils.set_bit_field(result, field_value, start_bit, num_bits)
        return result

    @staticmethod
    def split_bit_field(value: int, *field_specs: tuple[int, int]) -> list[int]:
        """Split a value into multiple bit fields.

        Args:
            value: The value to split
            field_specs: Tuples of (start_bit, num_bits) for each field

        Returns:
            List of extracted field values
        """
        return [BitFieldUtils.extract_bit_field(value, start_bit, num_bits) for start_bit, num_bits in field_specs]

    @staticmethod
    def compare_bit_fields(value1: int, value2: int, start_bit: int, num_bits: int) -> int:
        """Compare bit fields between two values.

        Returns -1, 0, or 1.
        """
        field1 = BitFieldUtils.extract_bit_field(value1, start_bit, num_bits)
        field2 = BitFieldUtils.extract_bit_field(value2, start_bit, num_bits)
        if field1 < field2:
            return -1
        if field1 > field2:
            return 1
        return 0

    @staticmethod
    def rotate_left(value: int, positions: int, bit_width: int = DEFAULT_BIT_WIDTH) -> int:
        """Rotate bits left by the specified number of positions."""
        positions = positions % bit_width
        if positions == 0:
            return value
        mask = (1 << bit_width) - 1
        value &= mask
        return ((value << positions) | (value >> (bit_width - positions))) & mask

    @staticmethod
    def rotate_right(value: int, positions: int, bit_width: int = DEFAULT_BIT_WIDTH) -> int:
        """Rotate bits right by the specified number of positions."""
        positions = positions % bit_width
        if positions == 0:
            return value
        mask = (1 << bit_width) - 1
        value &= mask
        return ((value >> positions) | (value << (bit_width - positions))) & mask

    @staticmethod
    def extract_bit_field_from_mask(value: int, mask: int, shift: int) -> int:
        """Extract a bit field using a mask and shift amount.

        Args:
            value: The value to extract from
            mask: The base mask (e.g., 0x0F for 4 bits)
            shift: How many bits to shift the mask left

        Returns:
            The extracted bit field value
        """
        shifted_mask = mask << shift
        return BitFieldUtils.extract_bits(value, shifted_mask) >> shift

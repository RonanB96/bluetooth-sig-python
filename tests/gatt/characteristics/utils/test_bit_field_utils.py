"""Test cases for bit field manipulation utilities."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.utils.bit_field_utils import BitFieldUtils, BitPositions


class TestBitPositions:
    """Test BitPositions constants."""

    def test_bit_position_constants(self) -> None:
        """Test that bit position constants have correct values."""
        assert BitPositions.BIT_0 == 1
        assert BitPositions.BIT_1 == 2
        assert BitPositions.BIT_2 == 4
        assert BitPositions.BIT_3 == 8
        assert BitPositions.BIT_4 == 16
        assert BitPositions.BIT_5 == 32
        assert BitPositions.BIT_6 == 64
        assert BitPositions.BIT_7 == 128


class TestBitFieldExtraction:
    """Test bit field extraction operations."""

    def test_extract_bit_field_basic(self) -> None:
        """Test basic bit field extraction."""
        value = 0b11010110  # 214
        assert BitFieldUtils.extract_bit_field(value, 0, 4) == 0b0110  # Bottom 4 bits
        assert BitFieldUtils.extract_bit_field(value, 2, 4) == 0b0101  # Bits 2-5
        assert BitFieldUtils.extract_bit_field(value, 4, 4) == 0b1101  # Top 4 bits

    def test_extract_bit_field_single_bit(self) -> None:
        """Test extracting single bits."""
        value = 0b10101010
        assert BitFieldUtils.extract_bit_field(value, 0, 1) == 0
        assert BitFieldUtils.extract_bit_field(value, 1, 1) == 1
        assert BitFieldUtils.extract_bit_field(value, 2, 1) == 0
        assert BitFieldUtils.extract_bit_field(value, 3, 1) == 1

    def test_extract_bit_field_full_width(self) -> None:
        """Test extracting full width bit field."""
        value = 0xFFFF
        assert BitFieldUtils.extract_bit_field(value, 0, 16) == 0xFFFF

    def test_extract_bit_field_invalid_params(self) -> None:
        """Test bit field extraction with invalid parameters."""
        with pytest.raises(ValueError):
            BitFieldUtils.extract_bit_field(0xFF, 0, 0)  # Zero width
        with pytest.raises(ValueError):
            BitFieldUtils.extract_bit_field(0xFF, -1, 4)  # Negative start


class TestBitFieldSetting:
    """Test bit field setting operations."""

    def test_set_bit_field_basic(self) -> None:
        """Test basic bit field setting."""
        value = 0x00
        result = BitFieldUtils.set_bit_field(value, 0xF, 0, 4)
        assert result == 0x0F

        result = BitFieldUtils.set_bit_field(result, 0xA, 4, 4)
        assert result == 0xAF

    def test_set_bit_field_overwrite(self) -> None:
        """Test bit field setting overwrites existing bits."""
        value = 0xFF
        result = BitFieldUtils.set_bit_field(value, 0x0, 2, 4)
        assert result == 0xC3  # 11000011

    def test_set_bit_field_invalid_params(self) -> None:
        """Test bit field setting with invalid parameters."""
        with pytest.raises(ValueError):
            BitFieldUtils.set_bit_field(0x00, 0xF, 0, 0)  # Zero width
        with pytest.raises(ValueError):
            BitFieldUtils.set_bit_field(0x00, 0xF, -1, 4)  # Negative start

    def test_set_bit_field_value_too_large(self) -> None:
        """Test bit field setting with value exceeding capacity."""
        with pytest.raises(ValueError):
            BitFieldUtils.set_bit_field(0x00, 0x10, 0, 4)  # 16 doesn't fit in 4 bits


class TestBitmaskOperations:
    """Test bitmask creation and manipulation."""

    def test_create_bitmask(self) -> None:
        """Test bitmask creation."""
        assert BitFieldUtils.create_bitmask(0, 4) == 0x0F
        assert BitFieldUtils.create_bitmask(2, 4) == 0x3C  # 111100
        assert BitFieldUtils.create_bitmask(8, 8) == 0xFF00

    def test_create_bitmask_invalid_params(self) -> None:
        """Test bitmask creation with invalid parameters."""
        with pytest.raises(ValueError):
            BitFieldUtils.create_bitmask(0, 0)  # Zero width
        with pytest.raises(ValueError):
            BitFieldUtils.create_bitmask(-1, 4)  # Negative start

    def test_extract_bits(self) -> None:
        """Test extracting bits using bitmask."""
        value = 0b11010110
        mask = 0b00111100  # Bits 2-5
        assert BitFieldUtils.extract_bits(value, mask) == 0b00010100


class TestSingleBitOperations:
    """Test single bit manipulation operations."""

    def test_test_bit(self) -> None:
        """Test testing individual bits."""
        value = 0b10101010
        assert not BitFieldUtils.test_bit(value, 0)
        assert BitFieldUtils.test_bit(value, 1)
        assert not BitFieldUtils.test_bit(value, 2)
        assert BitFieldUtils.test_bit(value, 3)

    def test_test_bit_invalid_position(self) -> None:
        """Test testing bit with invalid position."""
        with pytest.raises(ValueError):
            BitFieldUtils.test_bit(0xFF, -1)

    def test_set_bit(self) -> None:
        """Test setting individual bits."""
        value = 0x00
        result = BitFieldUtils.set_bit(value, 0)
        assert result == 0x01
        result = BitFieldUtils.set_bit(result, 2)
        assert result == 0x05  # 101

    def test_clear_bit(self) -> None:
        """Test clearing individual bits."""
        value = 0xFF
        result = BitFieldUtils.clear_bit(value, 0)
        assert result == 0xFE
        result = BitFieldUtils.clear_bit(result, 2)
        assert result == 0xFA  # 11111010

    def test_toggle_bit(self) -> None:
        """Test toggling individual bits."""
        value = 0xAA  # 10101010
        result = BitFieldUtils.toggle_bit(value, 0)
        assert result == 0xAB  # 10101011
        result = BitFieldUtils.toggle_bit(result, 1)
        assert result == 0xA9  # 10101001


class TestMultipleBitOperations:
    """Test operations on multiple bits."""

    def test_test_bits_any(self) -> None:
        """Test checking if any bits in mask are set."""
        value = 0b10100000
        mask = 0b11000000  # Test top two bits
        assert BitFieldUtils.test_bits_any(value, mask)

        mask = 0b00000011  # Test bottom two bits
        assert not BitFieldUtils.test_bits_any(value, mask)

    def test_test_bits_all(self) -> None:
        """Test checking if all bits in mask are set."""
        value = 0b11100000
        mask = 0b11000000  # Test top two bits
        assert BitFieldUtils.test_bits_all(value, mask)

        mask = 0b11110000  # Test top four bits
        assert not BitFieldUtils.test_bits_all(value, mask)

    def test_set_bits(self) -> None:
        """Test setting multiple bits using mask."""
        value = 0x00
        mask = 0x0F  # Set bottom 4 bits
        result = BitFieldUtils.set_bits(value, mask)
        assert result == 0x0F

    def test_clear_bits(self) -> None:
        """Test clearing multiple bits using mask."""
        value = 0xFF
        mask = 0x0F  # Clear bottom 4 bits
        result = BitFieldUtils.clear_bits(value, mask)
        assert result == 0xF0

    def test_toggle_bits(self) -> None:
        """Test toggling multiple bits using mask."""
        value = 0xAA  # 10101010
        mask = 0x0F  # Toggle bottom 4 bits
        result = BitFieldUtils.toggle_bits(value, mask)
        assert result == 0xA5  # 10100101


class TestBitCounting:
    """Test bit counting operations."""

    def test_count_set_bits(self) -> None:
        """Test counting set bits."""
        assert BitFieldUtils.count_set_bits(0x00) == 0
        assert BitFieldUtils.count_set_bits(0x01) == 1
        assert BitFieldUtils.count_set_bits(0x03) == 2
        assert BitFieldUtils.count_set_bits(0x07) == 3
        assert BitFieldUtils.count_set_bits(0xFF) == 8

    def test_get_bit_positions(self) -> None:
        """Test getting positions of set bits."""
        assert BitFieldUtils.get_bit_positions(0x00) == []
        assert BitFieldUtils.get_bit_positions(0x01) == [0]
        assert BitFieldUtils.get_bit_positions(0x05) == [0, 2]  # 101
        assert BitFieldUtils.get_bit_positions(0x0F) == [0, 1, 2, 3]

    def test_find_first_set_bit(self) -> None:
        """Test finding first (least significant) set bit."""
        assert BitFieldUtils.find_first_set_bit(0x00) is None
        assert BitFieldUtils.find_first_set_bit(0x01) == 0
        assert BitFieldUtils.find_first_set_bit(0x02) == 1
        assert BitFieldUtils.find_first_set_bit(0x04) == 2
        assert BitFieldUtils.find_first_set_bit(0x0C) == 2  # 1100

    def test_find_last_set_bit(self) -> None:
        """Test finding last (most significant) set bit."""
        assert BitFieldUtils.find_last_set_bit(0x00) is None
        assert BitFieldUtils.find_last_set_bit(0x01) == 0
        assert BitFieldUtils.find_last_set_bit(0x02) == 1
        assert BitFieldUtils.find_last_set_bit(0x04) == 2
        assert BitFieldUtils.find_last_set_bit(0x0C) == 3  # 1100


class TestBitManipulation:
    """Test advanced bit manipulation operations."""

    def test_reverse_bits(self) -> None:
        """Test reversing bits within specified width."""
        # 8-bit reverse
        value = 0b10110001  # 177
        result = BitFieldUtils.reverse_bits(value, 8)
        assert result == 0b10001101  # 141

        # 4-bit reverse
        value = 0b1010
        result = BitFieldUtils.reverse_bits(value, 4)
        assert result == 0b0101

    def test_calculate_parity(self) -> None:
        """Test calculating parity of set bits."""
        assert BitFieldUtils.calculate_parity(0x00) == 0  # Even (0 bits)
        assert BitFieldUtils.calculate_parity(0x01) == 1  # Odd (1 bit)
        assert BitFieldUtils.calculate_parity(0x03) == 0  # Even (2 bits)
        assert BitFieldUtils.calculate_parity(0x07) == 1  # Odd (3 bits)

    def test_validate_bit_field_range(self) -> None:
        """Test bit field range validation."""
        assert BitFieldUtils.validate_bit_field_range(0, 8, 32)
        assert BitFieldUtils.validate_bit_field_range(24, 8, 32)
        assert not BitFieldUtils.validate_bit_field_range(25, 8, 32)  # Would exceed
        assert not BitFieldUtils.validate_bit_field_range(-1, 8, 32)  # Negative start
        assert not BitFieldUtils.validate_bit_field_range(0, 0, 32)  # Zero width


class TestAdvancedBitOperations:
    """Test advanced bit field operations."""

    def test_copy_bit_field(self) -> None:
        """Test copying bit field between values."""
        source = 0b11110000
        dest = 0b00000000
        result = BitFieldUtils.copy_bit_field(source, dest, 4, 0, 4)
        assert result == 0b00001111

    def test_shift_bit_field_left(self) -> None:
        """Test shifting bit field left."""
        value = 0b00001111  # Field at bits 0-3
        result = BitFieldUtils.shift_bit_field_left(value, 0, 4, 2)
        assert result == 0b00111100  # Field now at bits 2-5

    def test_shift_bit_field_right(self) -> None:
        """Test shifting bit field right."""
        value = 0b00111100  # Field at bits 2-5
        result = BitFieldUtils.shift_bit_field_right(value, 2, 4, 2)
        assert result == 0b00001111  # Field now at bits 0-3

    def test_merge_bit_fields(self) -> None:
        """Test merging multiple bit fields."""
        result = BitFieldUtils.merge_bit_fields(
            (0xF, 0, 4),  # Value 15 at bits 0-3
            (0xA, 4, 4),  # Value 10 at bits 4-7
            (0x3, 8, 2),  # Value 3 at bits 8-9
        )
        assert result == 0x3AF

    def test_split_bit_field(self) -> None:
        """Test splitting value into multiple bit fields."""
        value = 0x3AF  # 001110101111
        result = BitFieldUtils.split_bit_field(
            value,
            (0, 4),  # Bottom 4 bits
            (4, 4),  # Next 4 bits
            (8, 2),  # Top 2 bits
        )
        assert result == [0xF, 0xA, 0x3]

    def test_compare_bit_fields(self) -> None:
        """Test comparing bit fields between values."""
        value1 = 0b11110000
        value2 = 0b10100000

        # Compare bits 4-7
        assert BitFieldUtils.compare_bit_fields(value1, value2, 4, 4) == 1
        assert BitFieldUtils.compare_bit_fields(value2, value1, 4, 4) == -1

        # Compare equal fields
        value3 = 0b11110000
        assert BitFieldUtils.compare_bit_fields(value1, value3, 4, 4) == 0


class TestRotateOperations:
    """Test bit rotation operations."""

    def test_rotate_left(self) -> None:
        """Test rotating bits left."""
        # 8-bit rotation
        value = 0b10000001
        result = BitFieldUtils.rotate_left(value, 1, 8)
        assert result == 0b00000011

        # 4-bit rotation
        value = 0b1001
        result = BitFieldUtils.rotate_left(value, 1, 4)
        assert result == 0b0011

    def test_rotate_right(self) -> None:
        """Test rotating bits right."""
        # 8-bit rotation
        value = 0b10000001
        result = BitFieldUtils.rotate_right(value, 1, 8)
        assert result == 0b11000000

        # 4-bit rotation
        value = 0b1001
        result = BitFieldUtils.rotate_right(value, 1, 4)
        assert result == 0b1100

    def test_rotate_zero_positions(self) -> None:
        """Test rotation with zero positions."""
        value = 0b10101010
        assert BitFieldUtils.rotate_left(value, 0, 8) == value
        assert BitFieldUtils.rotate_right(value, 0, 8) == value

    def test_rotate_full_cycle(self) -> None:
        """Test rotation full cycle returns to original."""
        value = 0b10101010
        result = BitFieldUtils.rotate_left(value, 8, 8)
        assert result == value
        result = BitFieldUtils.rotate_right(value, 8, 8)
        assert result == value


class TestExtractBitFieldFromMask:
    """Test bit field extraction using mask and shift."""

    def test_extract_bit_field_from_mask(self) -> None:
        """Test extracting bit field using mask and shift."""
        # Extract bits 4-7 using mask 0x0F shifted by 4
        value = 0xABCD
        mask = 0x0F
        shift = 4
        result = BitFieldUtils.extract_bit_field_from_mask(value, mask, shift)
        assert result == 0x0C  # Bits 4-7 of 0xABCD

        # Extract bits 8-11
        shift = 8
        result = BitFieldUtils.extract_bit_field_from_mask(value, mask, shift)
        assert result == 0x0B  # Bits 8-11 of 0xABCD

    def test_extract_bit_field_from_mask_single_bit(self) -> None:
        """Test extracting single bit using mask and shift."""
        value = 0b10101010
        mask = 0x01

        # Extract bit 1
        result = BitFieldUtils.extract_bit_field_from_mask(value, mask, 1)
        assert result == 1

        # Extract bit 0
        result = BitFieldUtils.extract_bit_field_from_mask(value, mask, 0)
        assert result == 0

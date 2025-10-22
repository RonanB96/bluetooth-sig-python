"""Tests for the BitFieldUtils class."""

import pytest

from bluetooth_sig.gatt.characteristics.utils.bit_field_utils import BitFieldUtils


class TestBitFieldUtils:  # pylint: disable=too-many-public-methods
    """Comprehensive tests for BitFieldUtils class."""

    # Test extract_bit_field
    def test_extract_bit_field_basic(self) -> None:
        """Test basic bit field extraction."""
        # Extract 4 bits starting at bit 4 from 0b11110000 (240)
        result = BitFieldUtils.extract_bit_field(0b11110000, 4, 4)
        assert result == 0b1111

        # Extract 2 bits starting at bit 1 from 0b1010 (10)
        result = BitFieldUtils.extract_bit_field(0b1010, 1, 2)
        assert result == 0b01  # 0b1010 >> 1 = 0b0101, & 0b0011 = 0b0001

    def test_extract_bit_field_edge_cases(self) -> None:
        """Test edge cases for bit field extraction."""
        # Extract from bit 0
        result = BitFieldUtils.extract_bit_field(0b1111, 0, 4)
        assert result == 0b1111

        # Extract single bit
        result = BitFieldUtils.extract_bit_field(0b1010, 1, 1)
        assert result == 1

        # Extract all bits
        result = BitFieldUtils.extract_bit_field(0xFF, 0, 8)
        assert result == 0xFF

    def test_extract_bit_field_invalid_params(self) -> None:
        """Test invalid parameters for bit field extraction."""
        with pytest.raises(ValueError, match="Invalid bit field parameters"):
            BitFieldUtils.extract_bit_field(0b1111, -1, 4)

        with pytest.raises(ValueError, match="Invalid bit field parameters"):
            BitFieldUtils.extract_bit_field(0b1111, 0, 0)

        with pytest.raises(ValueError, match="Invalid bit field parameters"):
            BitFieldUtils.extract_bit_field(0b1111, 0, -1)

    # Test set_bit_field
    def test_set_bit_field_basic(self) -> None:
        """Test basic bit field setting."""
        # Set 4-bit field at position 4 to 0b1010 in 0
        result = BitFieldUtils.set_bit_field(0, 0b1010, 4, 4)
        assert result == 0b10100000

        # Modify existing value
        result = BitFieldUtils.set_bit_field(0b11111111, 0b0000, 4, 4)
        assert result == 0b00001111

    def test_set_bit_field_edge_cases(self) -> None:
        """Test edge cases for bit field setting."""
        # Set at bit 0
        result = BitFieldUtils.set_bit_field(0, 0b1111, 0, 4)
        assert result == 0b1111

        # Set single bit
        result = BitFieldUtils.set_bit_field(0, 1, 7, 1)
        assert result == 0b10000000

        # Set maximum value for field
        result = BitFieldUtils.set_bit_field(0, 15, 4, 4)  # 15 = 2^4 - 1
        assert result == 0b11110000

    def test_set_bit_field_invalid_params(self) -> None:
        """Test invalid parameters for bit field setting."""
        with pytest.raises(ValueError, match="Invalid bit field parameters"):
            BitFieldUtils.set_bit_field(0, 1, -1, 4)

        with pytest.raises(ValueError, match="Invalid bit field parameters"):
            BitFieldUtils.set_bit_field(0, 1, 0, 0)

        with pytest.raises(ValueError, match="Field value .* exceeds .* capacity"):
            BitFieldUtils.set_bit_field(0, 16, 0, 4)  # 16 > 15 for 4 bits

    # Test create_bitmask
    def test_create_bitmask_basic(self) -> None:
        """Test basic bitmask creation."""
        # Create mask for 4 bits starting at bit 4
        result = BitFieldUtils.create_bitmask(4, 4)
        assert result == 0b11110000

        # Create mask for single bit
        result = BitFieldUtils.create_bitmask(7, 1)
        assert result == 0b10000000

    def test_create_bitmask_invalid_params(self) -> None:
        """Test invalid parameters for bitmask creation."""
        with pytest.raises(ValueError, match="Invalid bitmask parameters"):
            BitFieldUtils.create_bitmask(-1, 4)

        with pytest.raises(ValueError, match="Invalid bitmask parameters"):
            BitFieldUtils.create_bitmask(0, 0)

    # Test test_bit
    def test_test_bit_basic(self) -> None:
        """Test basic bit testing."""
        value = 0b10101010

        assert BitFieldUtils.test_bit(value, 0) is False  # Bit 0 is 0
        assert BitFieldUtils.test_bit(value, 1) is True  # Bit 1 is 1
        assert BitFieldUtils.test_bit(value, 7) is True  # Bit 7 is 1

    def test_test_bit_edge_cases(self) -> None:
        """Test edge cases for bit testing."""
        # Test bit 0
        assert BitFieldUtils.test_bit(1, 0) is True
        assert BitFieldUtils.test_bit(0, 0) is False

        # Test high bits
        assert BitFieldUtils.test_bit(0x80000000, 31) is True

    def test_test_bit_invalid_params(self) -> None:
        """Test invalid parameters for bit testing."""
        with pytest.raises(ValueError, match="Bit position must be non-negative"):
            BitFieldUtils.test_bit(1, -1)

    # Test test_bits_any and test_bits_all
    def test_test_bits_any(self) -> None:
        """Test testing if any bits in mask are set."""
        value = 0b1010

        assert BitFieldUtils.test_bits_any(value, 0b0001) is False  # Bit 0 not set
        assert BitFieldUtils.test_bits_any(value, 0b0010) is True  # Bit 1 is set
        assert BitFieldUtils.test_bits_any(value, 0b1100) is True  # Bit 3 is set
        assert BitFieldUtils.test_bits_any(value, 0b0100) is False  # No overlap

    def test_test_bits_all(self) -> None:
        """Test testing if all bits in mask are set."""
        value = 0b1010

        assert BitFieldUtils.test_bits_all(value, 0b0010) is True  # Bit 1 is set
        assert BitFieldUtils.test_bits_all(value, 0b1010) is True  # All bits set
        assert BitFieldUtils.test_bits_all(value, 0b1110) is False  # Bit 0 not set
        assert BitFieldUtils.test_bits_all(value, 0b0001) is False  # Bit 0 not set

    # Test set_bit, clear_bit, toggle_bit
    def test_set_bit(self) -> None:
        """Test setting individual bits."""
        result = BitFieldUtils.set_bit(0, 3)
        assert result == 0b1000

        result = BitFieldUtils.set_bit(0b0101, 1)
        assert result == 0b0111

    def test_clear_bit(self) -> None:
        """Test clearing individual bits."""
        result = BitFieldUtils.clear_bit(0b1111, 1)
        assert result == 0b1101

        result = BitFieldUtils.clear_bit(0b1000, 3)
        assert result == 0

    def test_toggle_bit(self) -> None:
        """Test toggling individual bits."""
        result = BitFieldUtils.toggle_bit(0b0101, 0)
        assert result == 0b0100

        result = BitFieldUtils.toggle_bit(0b0101, 1)
        assert result == 0b0111

    def test_bit_operations_invalid_params(self) -> None:
        """Test invalid parameters for bit operations."""
        with pytest.raises(ValueError, match="Bit position must be non-negative"):
            BitFieldUtils.set_bit(0, -1)

        with pytest.raises(ValueError, match="Bit position must be non-negative"):
            BitFieldUtils.clear_bit(0, -1)

        with pytest.raises(ValueError, match="Bit position must be non-negative"):
            BitFieldUtils.toggle_bit(0, -1)

    # Test set_bits, clear_bits, toggle_bits, extract_bits
    def test_set_bits(self) -> None:
        """Test setting multiple bits with mask."""
        result = BitFieldUtils.set_bits(0b0000, 0b1010)
        assert result == 0b1010

        result = BitFieldUtils.set_bits(0b0101, 0b1010)
        assert result == 0b1111

    def test_clear_bits(self) -> None:
        """Test clearing multiple bits with mask."""
        result = BitFieldUtils.clear_bits(0b1111, 0b1010)
        assert result == 0b0101

        result = BitFieldUtils.clear_bits(0b1111, 0b1111)
        assert result == 0

    def test_toggle_bits(self) -> None:
        """Test toggling multiple bits with mask."""
        result = BitFieldUtils.toggle_bits(0b0101, 0b1010)
        assert result == 0b1111

        result = BitFieldUtils.toggle_bits(0b1111, 0b1010)
        assert result == 0b0101

    def test_extract_bits(self) -> None:
        """Test extracting bits with mask."""
        result = BitFieldUtils.extract_bits(0b1111, 0b1010)
        assert result == 0b1010

        result = BitFieldUtils.extract_bits(0b1100, 0b0011)
        assert result == 0

    # Test count_set_bits
    def test_count_set_bits(self) -> None:
        """Test counting set bits."""
        assert BitFieldUtils.count_set_bits(0) == 0
        assert BitFieldUtils.count_set_bits(1) == 1
        assert BitFieldUtils.count_set_bits(0b10101010) == 4
        assert BitFieldUtils.count_set_bits(0xFFFFFFFF) == 32

    # Test get_bit_positions
    def test_get_bit_positions(self) -> None:
        """Test getting positions of set bits."""
        assert BitFieldUtils.get_bit_positions(0) == []
        assert BitFieldUtils.get_bit_positions(1) == [0]
        assert BitFieldUtils.get_bit_positions(0b10101010) == [1, 3, 5, 7]
        assert BitFieldUtils.get_bit_positions(0x80000000) == [31]

    # Test find_first_set_bit
    def test_find_first_set_bit(self) -> None:
        """Test finding first set bit."""
        assert BitFieldUtils.find_first_set_bit(0) is None
        assert BitFieldUtils.find_first_set_bit(1) == 0
        assert BitFieldUtils.find_first_set_bit(0b1110) == 1
        assert BitFieldUtils.find_first_set_bit(0x80000000) == 31

    # Test find_last_set_bit
    def test_find_last_set_bit(self) -> None:
        """Test finding last set bit."""
        assert BitFieldUtils.find_last_set_bit(0) is None
        assert BitFieldUtils.find_last_set_bit(1) == 0
        assert BitFieldUtils.find_last_set_bit(0b1110) == 3
        assert BitFieldUtils.find_last_set_bit(0x80000000) == 31

    # Test reverse_bits
    def test_reverse_bits(self) -> None:
        """Test bit reversal."""
        result = BitFieldUtils.reverse_bits(0b1100, 4)  # 12 -> 3 (0b0011)
        assert result == 0b0011

        result = BitFieldUtils.reverse_bits(0b0001, 4)  # 1 -> 8 (0b1000)
        assert result == 0b1000

        result = BitFieldUtils.reverse_bits(0b11110000, 8)  # 240 -> 15 (0b00001111)
        assert result == 0b00001111

    # Test calculate_parity
    def test_calculate_parity(self) -> None:
        """Test parity calculation."""
        assert BitFieldUtils.calculate_parity(0) == 0  # Even
        assert BitFieldUtils.calculate_parity(1) == 1  # Odd
        assert BitFieldUtils.calculate_parity(0b101) == 0  # Even (2 ones)
        assert BitFieldUtils.calculate_parity(0b111) == 1  # Odd (3 ones)

    # Test validate_bit_field_range
    def test_validate_bit_field_range(self) -> None:
        """Test bit field range validation."""
        assert BitFieldUtils.validate_bit_field_range(0, 8, 32) is True
        assert BitFieldUtils.validate_bit_field_range(24, 8, 32) is True
        assert BitFieldUtils.validate_bit_field_range(25, 8, 32) is False  # Exceeds 32 bits
        assert BitFieldUtils.validate_bit_field_range(-1, 8, 32) is False  # Negative start
        assert BitFieldUtils.validate_bit_field_range(0, 0, 32) is False  # Zero bits

    # Test copy_bit_field
    def test_copy_bit_field(self) -> None:
        """Test copying bit fields between values."""
        source = 0b11110000  # Bits 4-7 set
        dest = 0b00001111  # Bits 0-3 set

        result = BitFieldUtils.copy_bit_field(source, dest, 4, 0, 4)
        assert result == 0b00001111  # dest with bits 0-3 replaced by source bits 4-7 (15 -> 15)

    # Test shift_bit_field_left and shift_bit_field_right
    def test_shift_bit_field_left(self) -> None:
        """Test shifting bit fields left."""
        value = 0b00001111  # Bits 0-3 set

        result = BitFieldUtils.shift_bit_field_left(value, 0, 4, 4)
        assert result == 0b11110000  # Shifted left by 4 positions

    def test_shift_bit_field_right(self) -> None:
        """Test shifting bit fields right."""
        value = 0b11110000  # Bits 4-7 set

        result = BitFieldUtils.shift_bit_field_right(value, 4, 4, 2)
        assert result == 0b00111100  # Shifted right by 2 positions

    # Test merge_bit_fields
    def test_merge_bit_fields(self) -> None:
        """Test merging multiple bit fields."""
        result = BitFieldUtils.merge_bit_fields(
            (0b11, 0, 2),  # Bits 0-1: 11
            (0b10, 4, 2),  # Bits 4-5: 10
            (0b01, 7, 1),  # Bit 7: 1
        )
        expected = 0b10100011  # 0b10100011 = 163
        assert result == expected

    # Test split_bit_field
    def test_split_bit_field(self) -> None:
        """Test splitting values into multiple bit fields."""
        value = 0b10110100  # 180 in decimal

        result = BitFieldUtils.split_bit_field(
            value,
            (0, 2),  # Bits 0-1: should be 0b00 = 0
            (4, 2),  # Bits 4-5: should be 0b11 = 3
            (7, 1),  # Bit 7: should be 0b1 = 1
        )

        assert result == [0, 3, 1]

    # Test compare_bit_fields
    def test_compare_bit_fields(self) -> None:
        """Test comparing bit fields between values."""
        val1 = 0b10110000
        val2 = 0b10001111

        # Compare bits 4-7: 1011 vs 1000
        result = BitFieldUtils.compare_bit_fields(val1, val2, 4, 4)
        assert result == 1  # 1011 > 1000

        # Compare bits 0-3: 0000 vs 1111
        result = BitFieldUtils.compare_bit_fields(val1, val2, 0, 4)
        assert result == -1  # 0000 < 1111

        # Compare equal fields
        result = BitFieldUtils.compare_bit_fields(val1, val1, 4, 4)
        assert result == 0

    # Test rotate_left
    def test_rotate_left(self) -> None:
        """Test left rotation of bits."""
        result = BitFieldUtils.rotate_left(0b1001, 1, 4)  # Rotate 0b1001 left by 1
        assert result == 0b0011  # Should be 0b0011 (3)

        result = BitFieldUtils.rotate_left(0b1001, 2, 4)  # Rotate left by 2
        assert result == 0b0110  # Should be 0b0110 (6)

        result = BitFieldUtils.rotate_left(0b1001, 4, 4)  # Full rotation
        assert result == 0b1001  # Should be unchanged

    # Test rotate_right
    def test_rotate_right(self) -> None:
        """Test right rotation of bits."""
        result = BitFieldUtils.rotate_right(0b1001, 1, 4)  # Rotate 0b1001 right by 1
        assert result == 0b1100  # Should be 0b1100 (12)

        result = BitFieldUtils.rotate_right(0b1001, 2, 4)  # Rotate right by 2
        assert result == 0b0110  # Should be 0b0110 (6)

        result = BitFieldUtils.rotate_right(0b1001, 4, 4)  # Full rotation
        assert result == 0b1001  # Should be unchanged

    # Test extract_bit_field_from_mask
    def test_extract_bit_field_from_mask(self) -> None:
        """Test extracting bit fields using mask and shift."""
        value = 0b11110000

        # Extract 4 bits starting at bit 4 using mask 0x0F shifted by 4
        result = BitFieldUtils.extract_bit_field_from_mask(value, 0x0F, 4)
        assert result == 0b1111

        # Extract 2 bits starting at bit 1
        result = BitFieldUtils.extract_bit_field_from_mask(value, 0x03, 1)
        assert result == 0b00

    # Test integration scenarios
    def test_ble_flag_handling(self) -> None:
        """Test BLE characteristic flag handling scenarios."""
        # Simulate battery power state flags
        flags = 0

        # Set multiple flags
        flags = BitFieldUtils.set_bit(flags, 0)  # Present state available
        flags = BitFieldUtils.set_bit(flags, 1)  # Battery level available
        flags = BitFieldUtils.set_bit(flags, 4)  # Charging state available

        assert BitFieldUtils.test_bit(flags, 0) is True
        assert BitFieldUtils.test_bit(flags, 1) is True
        assert BitFieldUtils.test_bit(flags, 4) is True
        assert BitFieldUtils.test_bit(flags, 2) is False

        # Extract battery level (assume 8-bit field at position 8)
        battery_level = 85
        data = BitFieldUtils.set_bit_field(flags, battery_level, 8, 8)
        extracted_level = BitFieldUtils.extract_bit_field(data, 8, 8)
        assert extracted_level == 85

    def test_cycling_power_data_parsing(self) -> None:
        """Test cycling power measurement data parsing."""
        # Simulate cycling power flags (16-bit)
        flags = BitFieldUtils.merge_bit_fields(
            (1, 0, 1),  # Pedal power balance present
            (1, 1, 1),  # Pedal power balance reference
            (1, 8, 1),  # Accumulated energy present
            (1, 10, 1),  # Wheel revolution data present
        )

        # Check flags
        assert BitFieldUtils.test_bit(flags, 0) is True  # Pedal power balance present
        assert BitFieldUtils.test_bit(flags, 8) is True  # Accumulated energy present
        assert BitFieldUtils.test_bit(flags, 10) is True  # Wheel data present

        # Simulate power value (16-bit at offset 16)
        power = 250  # 250 watts
        data = BitFieldUtils.set_bit_field(flags, power, 16, 16)

        extracted_power = BitFieldUtils.extract_bit_field(data, 16, 16)
        assert extracted_power == 250

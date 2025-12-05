src.bluetooth_sig.gatt.characteristics.utils.bit_field_utils
============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.utils.bit_field_utils

.. autoapi-nested-parse::

   Bit field manipulation and flag handling utilities.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.utils.bit_field_utils.BitPositions
   src.bluetooth_sig.gatt.characteristics.utils.bit_field_utils.BitFieldUtils


Module Contents
---------------

.. py:class:: BitPositions

   Common bit position constants for flag manipulation.


   .. py:attribute:: BIT_0
      :value: 1



   .. py:attribute:: BIT_1
      :value: 2



   .. py:attribute:: BIT_2
      :value: 4



   .. py:attribute:: BIT_3
      :value: 8



   .. py:attribute:: BIT_4
      :value: 16



   .. py:attribute:: BIT_5
      :value: 32



   .. py:attribute:: BIT_6
      :value: 64



   .. py:attribute:: BIT_7
      :value: 128



.. py:class:: BitFieldUtils

   Utility class for bit field manipulation and flag handling.


   .. py:attribute:: SINGLE_BIT_MASK
      :value: 1



   .. py:attribute:: DEFAULT_BIT_WIDTH
      :value: 32



   .. py:method:: extract_bit_field(value: int, start_bit: int, num_bits: int) -> int
      :staticmethod:


      Extract a bit field from an integer value.



   .. py:method:: set_bit_field(value: int, field_value: int, start_bit: int, num_bits: int) -> int
      :staticmethod:


      Set a bit field in an integer value.



   .. py:method:: create_bitmask(start_bit: int, num_bits: int) -> int
      :staticmethod:


      Create a bitmask for a specific bit field range.



   .. py:method:: test_bit(value: int, bit_position: int) -> bool
      :staticmethod:


      Test if a specific bit is set in the value.



   .. py:method:: test_bits_any(value: int, bitmask: int) -> bool
      :staticmethod:


      Test if any bits in the bitmask are set in the value.



   .. py:method:: test_bits_all(value: int, bitmask: int) -> bool
      :staticmethod:


      Test if all bits in the bitmask are set in the value.



   .. py:method:: set_bit(value: int, bit_position: int) -> int
      :staticmethod:


      Set a specific bit in the value.



   .. py:method:: clear_bit(value: int, bit_position: int) -> int
      :staticmethod:


      Clear a specific bit in the value.



   .. py:method:: toggle_bit(value: int, bit_position: int) -> int
      :staticmethod:


      Toggle a specific bit in the value.



   .. py:method:: extract_bits(value: int, bitmask: int) -> int
      :staticmethod:


      Extract bits from value using a bitmask.



   .. py:method:: set_bits(value: int, bitmask: int) -> int
      :staticmethod:


      Set all bits specified in the bitmask.



   .. py:method:: clear_bits(value: int, bitmask: int) -> int
      :staticmethod:


      Clear all bits specified in the bitmask.



   .. py:method:: toggle_bits(value: int, bitmask: int) -> int
      :staticmethod:


      Toggle all bits specified in the bitmask.



   .. py:method:: count_set_bits(value: int) -> int
      :staticmethod:


      Count the number of set bits in the value.



   .. py:method:: get_bit_positions(value: int) -> list[int]
      :staticmethod:


      Get a list of positions of all set bits in the value.



   .. py:method:: find_first_set_bit(value: int) -> int | None
      :staticmethod:


      Find the position of the first (least significant) set bit.



   .. py:method:: find_last_set_bit(value: int) -> int | None
      :staticmethod:


      Find the position of the last (most significant) set bit.



   .. py:method:: reverse_bits(value: int, bit_width: int = DEFAULT_BIT_WIDTH) -> int
      :staticmethod:


      Reverse the bits in a value within the specified bit width.



   .. py:method:: calculate_parity(value: int) -> int
      :staticmethod:


      Calculate the parity (even/odd) of set bits.

      Returns 0 for even, 1 for odd.



   .. py:method:: validate_bit_field_range(start_bit: int, num_bits: int, total_bits: int = DEFAULT_BIT_WIDTH) -> bool
      :staticmethod:


      Validate that a bit field range is within bounds.



   .. py:method:: copy_bit_field(source: int, dest: int, source_start: int, dest_start: int, num_bits: int) -> int
      :staticmethod:


      Copy a bit field from source to destination.



   .. py:method:: shift_bit_field_left(value: int, start_bit: int, num_bits: int, shift_amount: int) -> int
      :staticmethod:


      Shift a bit field left within the value.



   .. py:method:: shift_bit_field_right(value: int, start_bit: int, num_bits: int, shift_amount: int) -> int
      :staticmethod:


      Shift a bit field right within the value.



   .. py:method:: merge_bit_fields(*fields: tuple[int, int, int]) -> int
      :staticmethod:


      Merge multiple bit fields into a single value.

      :param fields: Tuples of (field_value, start_bit, num_bits)



   .. py:method:: split_bit_field(value: int, *field_specs: tuple[int, int]) -> list[int]
      :staticmethod:


      Split a value into multiple bit fields.

      :param value: The value to split
      :param field_specs: Tuples of (start_bit, num_bits) for each field

      :returns: List of extracted field values



   .. py:method:: compare_bit_fields(value1: int, value2: int, start_bit: int, num_bits: int) -> int
      :staticmethod:


      Compare bit fields between two values.

      Returns -1, 0, or 1.



   .. py:method:: rotate_left(value: int, positions: int, bit_width: int = DEFAULT_BIT_WIDTH) -> int
      :staticmethod:


      Rotate bits left by the specified number of positions.



   .. py:method:: rotate_right(value: int, positions: int, bit_width: int = DEFAULT_BIT_WIDTH) -> int
      :staticmethod:


      Rotate bits right by the specified number of positions.



   .. py:method:: extract_bit_field_from_mask(value: int, mask: int, shift: int) -> int
      :staticmethod:


      Extract a bit field using a mask and shift amount.

      :param value: The value to extract from
      :param mask: The base mask (e.g., 0x0F for 4 bits)
      :param shift: How many bits to shift the mask left

      :returns: The extracted bit field value




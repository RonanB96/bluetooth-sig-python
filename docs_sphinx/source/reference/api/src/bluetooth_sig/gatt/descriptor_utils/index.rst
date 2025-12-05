src.bluetooth_sig.gatt.descriptor_utils
=======================================

.. py:module:: src.bluetooth_sig.gatt.descriptor_utils

.. autoapi-nested-parse::

   Descriptor context utility functions.

   Provides helper functions for extracting and working with descriptor information
   from CharacteristicContext. These functions serve as both standalone utilities
   and are mirrored as methods in BaseCharacteristic for convenience.



Functions
---------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptor_utils.get_descriptors_from_context
   src.bluetooth_sig.gatt.descriptor_utils.get_descriptor_from_context
   src.bluetooth_sig.gatt.descriptor_utils.get_valid_range_from_context
   src.bluetooth_sig.gatt.descriptor_utils.get_presentation_format_from_context
   src.bluetooth_sig.gatt.descriptor_utils.get_user_description_from_context
   src.bluetooth_sig.gatt.descriptor_utils.validate_value_against_descriptor_range
   src.bluetooth_sig.gatt.descriptor_utils.enhance_error_message_with_descriptors


Module Contents
---------------

.. py:function:: get_descriptors_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None) -> dict[str, Any]

   Extract descriptor data from the parsing context.

   :param ctx: The characteristic context containing descriptor information

   :returns: Dictionary mapping descriptor UUIDs to DescriptorData objects


.. py:function:: get_descriptor_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None, descriptor_class: type[src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor]) -> src.bluetooth_sig.types.DescriptorData | None

   Get a specific descriptor from context.

   :param ctx: Characteristic context containing descriptors
   :param descriptor_class: Descriptor class to look for

   :returns: DescriptorData if found, None otherwise


.. py:function:: get_valid_range_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> tuple[int | float, int | float] | None

   Get valid range from descriptor context if available.

   :param ctx: Characteristic context containing descriptors

   :returns: Tuple of (min, max) values if Valid Range descriptor present, None otherwise


.. py:function:: get_presentation_format_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> src.bluetooth_sig.gatt.descriptors.characteristic_presentation_format.CharacteristicPresentationFormatData | None

   Get presentation format from descriptor context if available.

   :param ctx: Characteristic context containing descriptors

   :returns: CharacteristicPresentationFormatData if present, None otherwise


.. py:function:: get_user_description_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> str | None

   Get user description from descriptor context if available.

   :param ctx: Characteristic context containing descriptors

   :returns: User description string if present, None otherwise


.. py:function:: validate_value_against_descriptor_range(value: int | float, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> bool

   Validate a value against descriptor-defined valid range.

   :param value: Value to validate
   :param ctx: Characteristic context containing descriptors

   :returns: True if value is within valid range or no range defined, False otherwise


.. py:function:: enhance_error_message_with_descriptors(base_message: str, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> str

   Enhance error message with descriptor information for better debugging.

   :param base_message: Original error message
   :param ctx: Characteristic context containing descriptors

   :returns: Enhanced error message with descriptor context



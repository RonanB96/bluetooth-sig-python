src.bluetooth_sig.types.registry.appearance_info
================================================

.. py:module:: src.bluetooth_sig.types.registry.appearance_info

.. autoapi-nested-parse::

   Appearance information data structures.

   This module contains only the data structures for appearance values,
   with no dependencies on the registry system. This allows the registry
   to import these types without creating circular dependencies.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.registry.appearance_info.AppearanceSubcategoryInfo
   src.bluetooth_sig.types.registry.appearance_info.AppearanceInfo


Module Contents
---------------

.. py:class:: AppearanceSubcategoryInfo

   Bases: :py:obj:`msgspec.Struct`


   Decoded appearance subcategory information.

   .. attribute:: name

      Human-readable subcategory name (e.g., "Heart Rate Belt")

   .. attribute:: value

      Subcategory value (0-63)


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: value
      :type:  int


.. py:class:: AppearanceInfo

   Bases: :py:obj:`msgspec.Struct`


   Decoded appearance information from registry.

   The 16-bit appearance value encodes device type information:
   - Bits 15-6 (10 bits): Category value (0-1023)
   - Bits 5-0 (6 bits): Subcategory value (0-63)
   - Full code = (category << 6) | subcategory

   .. attribute:: category

      Human-readable device category name (e.g., "Heart Rate Sensor")

   .. attribute:: category_value

      Category value (upper 10 bits of appearance code)

   .. attribute:: subcategory

      Optional subcategory information (e.g., "Heart Rate Belt")


   .. py:attribute:: category
      :type:  str


   .. py:attribute:: category_value
      :type:  int


   .. py:attribute:: subcategory
      :type:  AppearanceSubcategoryInfo | None
      :value: None



   .. py:property:: full_name
      :type: str


      Get full appearance name.

      :returns: Full name with category and optional subcategory
                (e.g., "Heart Rate Sensor: Heart Rate Belt" or "Phone")



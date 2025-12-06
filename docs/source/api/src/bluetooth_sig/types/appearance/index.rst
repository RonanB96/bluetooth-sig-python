src.bluetooth_sig.types.appearance
==================================

.. py:module:: src.bluetooth_sig.types.appearance

.. autoapi-nested-parse::

   Appearance value types for Bluetooth device identification.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.appearance.AppearanceData


Module Contents
---------------

.. py:class:: AppearanceData

   Bases: :py:obj:`msgspec.Struct`


   Appearance characteristic data with human-readable info.

   .. attribute:: raw_value

      Raw 16-bit appearance code from BLE

   .. attribute:: info

      Optional decoded appearance information from registry


   .. py:method:: from_category(category: str, subcategory: str | None = None) -> AppearanceData
      :classmethod:


      Create AppearanceData from category and subcategory strings.

      This helper validates the strings and finds the correct raw_value by
      searching the registry. Useful when creating appearance data from
      user-provided human-readable names.

      :param category: Device category name (e.g., "Heart Rate Sensor")
      :param subcategory: Optional subcategory name (e.g., "Heart Rate Belt")

      :returns: AppearanceData with validated info and correct raw_value

      :raises ValueError: If category/subcategory combination is not found in registry

      .. admonition:: Example

         >>> data = AppearanceData.from_category("Heart Rate Sensor", "Heart Rate Belt")
         >>> data.raw_value
         833



   .. py:property:: category
      :type: str | None


      Get device category name.

      :returns: Category name or None if info not available


   .. py:property:: full_name
      :type: str | None


      Get full human-readable name.

      :returns: Full device type name or None if info not available


   .. py:attribute:: info
      :type:  bluetooth_sig.types.registry.appearance_info.AppearanceInfo | None
      :value: None



   .. py:attribute:: raw_value
      :type:  int


   .. py:property:: subcategory
      :type: str | None


      Get device subcategory name.

      :returns: Subcategory name or None if not available



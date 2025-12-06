src.bluetooth_sig.registry.core.appearance_values
=================================================

.. py:module:: src.bluetooth_sig.registry.core.appearance_values

.. autoapi-nested-parse::

   Registry for Bluetooth appearance values.

   This module provides a registry for looking up human-readable device types
   and categories from appearance codes found in advertising data and GATT
   characteristics.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.core.appearance_values.appearance_values_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.core.appearance_values.AppearanceValuesRegistry


Module Contents
---------------

.. py:class:: AppearanceValuesRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseGenericRegistry`\ [\ :py:obj:`bluetooth_sig.types.registry.appearance_info.AppearanceInfo`\ ]


   Registry for Bluetooth appearance values with lazy loading.

   This registry loads appearance values from the Bluetooth SIG assigned_numbers
   YAML file and provides lookup methods to decode appearance codes into
   human-readable device type information.

   The registry uses lazy loading - the YAML file is only parsed on the first
   lookup call. This improves startup time and reduces memory usage when the
   registry is not needed.

   Thread Safety:
       This registry is thread-safe. Multiple threads can safely call
       get_appearance_info() concurrently.

   .. admonition:: Example

      >>> registry = AppearanceValuesRegistry()
      >>> info = registry.get_appearance_info(833)
      >>> if info:
      ...     print(info.full_name)  # "Heart Rate Sensor: Heart Rate Belt"
      ...     print(info.category)  # "Heart Rate Sensor"
      ...     print(info.subcategory)  # "Heart Rate Belt"

   Initialize the registry with lazy loading.


   .. py:method:: find_by_category_subcategory(category: str, subcategory: str | None = None) -> bluetooth_sig.types.registry.appearance_info.AppearanceInfo | None

      Find appearance info by category and subcategory names.

      This method searches the registry for an appearance that matches
      the given category and subcategory names.

      :param category: Device category name (e.g., "Heart Rate Sensor")
      :param subcategory: Optional subcategory name (e.g., "Heart Rate Belt")

      :returns: AppearanceInfo if found, None otherwise

      .. admonition:: Example

         >>> registry = AppearanceValuesRegistry()
         >>> info = registry.find_by_category_subcategory("Heart Rate Sensor", "Heart Rate Belt")
         >>> if info:
         ...     print(info.category_value)  # Category value for lookup



   .. py:method:: get_appearance_info(appearance_code: int) -> bluetooth_sig.types.registry.appearance_info.AppearanceInfo | None

      Get appearance info by appearance code.

      This method lazily loads the YAML file on first call.

      :param appearance_code: 16-bit appearance value from BLE (0-65535)

      :returns: AppearanceInfo with decoded information, or None if code not found

      :raises ValueError: If appearance_code is outside valid range (0-65535)

      .. admonition:: Example

         >>> registry = AppearanceValuesRegistry()
         >>> info = registry.get_appearance_info(833)
         >>> if info:
         ...     print(info.full_name)  # "Heart Rate Sensor: Heart Rate Belt"



.. py:data:: appearance_values_registry
   :value: None



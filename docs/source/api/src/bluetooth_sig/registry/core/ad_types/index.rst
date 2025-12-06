src.bluetooth_sig.registry.core.ad_types
========================================

.. py:module:: src.bluetooth_sig.registry.core.ad_types

.. autoapi-nested-parse::

   AD Types registry for Bluetooth SIG advertising data type definitions.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.core.ad_types.ad_types_registry
   src.bluetooth_sig.registry.core.ad_types.logger


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.core.ad_types.ADTypesRegistry


Module Contents
---------------

.. py:class:: ADTypesRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseGenericRegistry`\ [\ :py:obj:`bluetooth_sig.types.advertising.ADTypeInfo`\ ]


   Registry for Bluetooth advertising data types with lazy loading.

   This registry loads AD type definitions from the official Bluetooth SIG
   assigned_numbers YAML file, providing authoritative AD type information
   from the specification.

   Initialize the AD types registry.


   .. py:method:: get_ad_type_by_name(name: str) -> bluetooth_sig.types.advertising.ADTypeInfo | None

      Get AD type info by name (lazy loads on first call).

      :param name: AD type name (case-insensitive)

      :returns: ADTypeInfo object, or None if not found



   .. py:method:: get_ad_type_info(ad_type: int) -> bluetooth_sig.types.advertising.ADTypeInfo | None

      Get AD type info by value (lazy loads on first call).

      :param ad_type: The AD type value (e.g., 0x01 for Flags)

      :returns: ADTypeInfo object, or None if not found



   .. py:method:: get_all_ad_types() -> dict[int, bluetooth_sig.types.advertising.ADTypeInfo]

      Get all registered AD types (lazy loads on first call).

      :returns: Dictionary mapping AD type values to ADTypeInfo objects



   .. py:method:: is_known_ad_type(ad_type: int) -> bool

      Check if AD type is known (lazy loads on first call).

      :param ad_type: The AD type value to check

      :returns: True if the AD type is registered, False otherwise



.. py:data:: ad_types_registry

.. py:data:: logger


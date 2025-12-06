src.bluetooth_sig.gatt.descriptors.manufacturer_limits
======================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.manufacturer_limits

.. autoapi-nested-parse::

   Manufacturer Limits Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.manufacturer_limits.ManufacturerLimitsData
   src.bluetooth_sig.gatt.descriptors.manufacturer_limits.ManufacturerLimitsDescriptor


Module Contents
---------------

.. py:class:: ManufacturerLimitsData

   Bases: :py:obj:`msgspec.Struct`


   Manufacturer Limits descriptor data.


   .. py:attribute:: max_limit
      :type:  int | float


   .. py:attribute:: min_limit
      :type:  int | float


.. py:class:: ManufacturerLimitsDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Manufacturer Limits Descriptor (0x2913).

   Defines manufacturer-specified limits for characteristic values.
   Contains minimum and maximum limits set by the manufacturer.


   .. py:method:: get_max_limit(data: bytes) -> int | float

      Get the maximum manufacturer limit.



   .. py:method:: get_min_limit(data: bytes) -> int | float

      Get the minimum manufacturer limit.



   .. py:method:: is_value_within_limits(data: bytes, value: int | float) -> bool

      Check if a value is within manufacturer limits.




src.bluetooth_sig.gatt.descriptors.valid_range
==============================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.valid_range

.. autoapi-nested-parse::

   Valid Range Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.valid_range.ValidRangeData
   src.bluetooth_sig.gatt.descriptors.valid_range.ValidRangeDescriptor


Module Contents
---------------

.. py:class:: ValidRangeData

   Bases: :py:obj:`msgspec.Struct`


   Valid Range descriptor data.


   .. py:attribute:: min_value
      :type:  int | float


   .. py:attribute:: max_value
      :type:  int | float


.. py:class:: ValidRangeDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`, :py:obj:`src.bluetooth_sig.gatt.descriptors.base.RangeDescriptorMixin`


   Valid Range Descriptor (0x2906).

   Defines the valid range for characteristic values.
   Contains minimum and maximum values for validation.



src.bluetooth_sig.gatt.descriptors.valid_range_and_accuracy
===========================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.valid_range_and_accuracy

.. autoapi-nested-parse::

   Valid Range and Accuracy Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.valid_range_and_accuracy.ValidRangeAndAccuracyData
   src.bluetooth_sig.gatt.descriptors.valid_range_and_accuracy.ValidRangeAndAccuracyDescriptor


Module Contents
---------------

.. py:class:: ValidRangeAndAccuracyData

   Bases: :py:obj:`msgspec.Struct`


   Valid Range and Accuracy descriptor data.


   .. py:attribute:: accuracy
      :type:  int | float


   .. py:attribute:: max_value
      :type:  int | float


   .. py:attribute:: min_value
      :type:  int | float


.. py:class:: ValidRangeAndAccuracyDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`, :py:obj:`src.bluetooth_sig.gatt.descriptors.base.RangeDescriptorMixin`


   Valid Range and Accuracy Descriptor (0x2911).

   Defines the valid range and accuracy for characteristic values.
   Contains minimum value, maximum value, and accuracy information.

   Initialize descriptor with resolved information.


   .. py:method:: get_accuracy(data: bytes) -> int | float

      Get the accuracy value.

      :param data: Raw descriptor data

      :returns: Accuracy value for the characteristic




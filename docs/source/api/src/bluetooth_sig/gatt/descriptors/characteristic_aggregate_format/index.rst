src.bluetooth_sig.gatt.descriptors.characteristic_aggregate_format
==================================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.characteristic_aggregate_format

.. autoapi-nested-parse::

   Characteristic Aggregate Format Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.characteristic_aggregate_format.CharacteristicAggregateFormatData
   src.bluetooth_sig.gatt.descriptors.characteristic_aggregate_format.CharacteristicAggregateFormatDescriptor


Module Contents
---------------

.. py:class:: CharacteristicAggregateFormatData

   Bases: :py:obj:`msgspec.Struct`


   Characteristic Aggregate Format descriptor data.


   .. py:attribute:: attribute_handles
      :type:  list[int]


.. py:class:: CharacteristicAggregateFormatDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Characteristic Aggregate Format Descriptor (0x2905).

   Contains a list of attribute handles that collectively form an aggregate value.
   Used to group multiple characteristics into a single logical value.


   .. py:method:: get_attribute_handles(data: bytes) -> list[int]

      Get the list of attribute handles.



   .. py:method:: get_handle_count(data: bytes) -> int

      Get the number of attribute handles.




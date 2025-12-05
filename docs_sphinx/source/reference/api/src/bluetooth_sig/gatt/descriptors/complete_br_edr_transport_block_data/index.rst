src.bluetooth_sig.gatt.descriptors.complete_br_edr_transport_block_data
=======================================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.complete_br_edr_transport_block_data

.. autoapi-nested-parse::

   Complete BR-EDR Transport Block Data Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.complete_br_edr_transport_block_data.CompleteBREDRTransportBlockDataData
   src.bluetooth_sig.gatt.descriptors.complete_br_edr_transport_block_data.CompleteBREDRTransportBlockDataDescriptor


Module Contents
---------------

.. py:class:: CompleteBREDRTransportBlockDataData

   Bases: :py:obj:`msgspec.Struct`


   Complete BR-EDR Transport Block Data descriptor data.


   .. py:attribute:: transport_data
      :type:  bytes


.. py:class:: CompleteBREDRTransportBlockDataDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Complete BR-EDR Transport Block Data Descriptor (0x290F).

   Contains complete BR-EDR transport block data.
   Used for transporting large data blocks over BR-EDR.


   .. py:method:: get_transport_data(data: bytes) -> bytes

      Get the transport block data.




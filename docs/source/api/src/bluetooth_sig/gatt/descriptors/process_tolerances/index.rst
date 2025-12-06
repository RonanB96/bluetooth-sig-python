src.bluetooth_sig.gatt.descriptors.process_tolerances
=====================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.process_tolerances

.. autoapi-nested-parse::

   Process Tolerances Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.process_tolerances.ProcessTolerancesData
   src.bluetooth_sig.gatt.descriptors.process_tolerances.ProcessTolerancesDescriptor


Module Contents
---------------

.. py:class:: ProcessTolerancesData

   Bases: :py:obj:`msgspec.Struct`


   Process Tolerances descriptor data.


   .. py:attribute:: tolerance_max
      :type:  int | float


   .. py:attribute:: tolerance_min
      :type:  int | float


.. py:class:: ProcessTolerancesDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Process Tolerances Descriptor (0x2914).

   Defines process tolerances for characteristic values.
   Contains minimum and maximum tolerance values.

   Initialize descriptor with resolved information.


   .. py:method:: get_tolerance_max(data: bytes) -> int | float

      Get the maximum process tolerance.



   .. py:method:: get_tolerance_min(data: bytes) -> int | float

      Get the minimum process tolerance.




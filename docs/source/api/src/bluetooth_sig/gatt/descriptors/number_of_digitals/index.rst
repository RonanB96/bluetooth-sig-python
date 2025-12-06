src.bluetooth_sig.gatt.descriptors.number_of_digitals
=====================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.number_of_digitals

.. autoapi-nested-parse::

   Number of Digitals Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.number_of_digitals.NumberOfDigitalsData
   src.bluetooth_sig.gatt.descriptors.number_of_digitals.NumberOfDigitalsDescriptor


Module Contents
---------------

.. py:class:: NumberOfDigitalsData

   Bases: :py:obj:`msgspec.Struct`


   Number of Digitals descriptor data.


   .. py:attribute:: number_of_digitals
      :type:  int


.. py:class:: NumberOfDigitalsDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Number of Digitals Descriptor (0x2909).

   Specifies the number of digital states supported by a characteristic.
   Used in sensor applications.

   Initialize descriptor with resolved information.


   .. py:method:: get_number_of_digitals(data: bytes) -> int

      Get the number of digitals.




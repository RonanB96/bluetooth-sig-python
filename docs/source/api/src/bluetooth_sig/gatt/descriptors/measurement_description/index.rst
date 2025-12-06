src.bluetooth_sig.gatt.descriptors.measurement_description
==========================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.measurement_description

.. autoapi-nested-parse::

   Measurement Description Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.measurement_description.MeasurementDescriptionData
   src.bluetooth_sig.gatt.descriptors.measurement_description.MeasurementDescriptionDescriptor


Module Contents
---------------

.. py:class:: MeasurementDescriptionData

   Bases: :py:obj:`msgspec.Struct`


   Measurement Description descriptor data.


   .. py:attribute:: description
      :type:  str


.. py:class:: MeasurementDescriptionDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Measurement Description Descriptor (0x2912).

   Contains a human-readable description of the measurement.
   UTF-8 encoded string describing what the measurement represents.

   Initialize descriptor with resolved information.


   .. py:method:: get_description(data: bytes) -> str

      Get the measurement description string.




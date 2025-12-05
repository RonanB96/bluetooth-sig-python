src.bluetooth_sig.gatt.descriptors.environmental_sensing_measurement
====================================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.environmental_sensing_measurement

.. autoapi-nested-parse::

   Environmental Sensing Measurement Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.environmental_sensing_measurement.EnvironmentalSensingMeasurementData
   src.bluetooth_sig.gatt.descriptors.environmental_sensing_measurement.EnvironmentalSensingMeasurementDescriptor


Module Contents
---------------

.. py:class:: EnvironmentalSensingMeasurementData

   Bases: :py:obj:`msgspec.Struct`


   Environmental Sensing Measurement descriptor data.


   .. py:attribute:: sampling_function
      :type:  int


   .. py:attribute:: measurement_period
      :type:  int


   .. py:attribute:: update_interval
      :type:  int


   .. py:attribute:: application
      :type:  int


   .. py:attribute:: measurement_uncertainty
      :type:  int


.. py:class:: EnvironmentalSensingMeasurementDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Environmental Sensing Measurement Descriptor (0x290C).

   Contains measurement parameters for environmental sensors.
   Includes sampling function, measurement period, and other parameters.


   .. py:method:: get_sampling_function(data: bytes) -> int

      Get the sampling function.



   .. py:method:: get_measurement_period(data: bytes) -> int

      Get the measurement period.



   .. py:method:: get_update_interval(data: bytes) -> int

      Get the update interval.



   .. py:method:: get_application(data: bytes) -> int

      Get the application identifier.



   .. py:method:: get_measurement_uncertainty(data: bytes) -> int

      Get the measurement uncertainty.




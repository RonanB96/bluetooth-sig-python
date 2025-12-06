src.bluetooth_sig.gatt.descriptors.observation_schedule
=======================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.observation_schedule

.. autoapi-nested-parse::

   Observation Schedule Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.observation_schedule.ObservationScheduleData
   src.bluetooth_sig.gatt.descriptors.observation_schedule.ObservationScheduleDescriptor


Module Contents
---------------

.. py:class:: ObservationScheduleData

   Bases: :py:obj:`msgspec.Struct`


   Observation Schedule descriptor data.


   .. py:attribute:: schedule
      :type:  bytes


.. py:class:: ObservationScheduleDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Observation Schedule Descriptor (0x2910).

   Defines the observation schedule for sensor measurements.
   Format varies depending on the sensor type and requirements.

   Initialize descriptor with resolved information.


   .. py:method:: get_schedule_data(data: bytes) -> bytes

      Get the raw schedule data.




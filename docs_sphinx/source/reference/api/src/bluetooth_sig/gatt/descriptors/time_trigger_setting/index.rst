src.bluetooth_sig.gatt.descriptors.time_trigger_setting
=======================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.time_trigger_setting

.. autoapi-nested-parse::

   Time Trigger Setting Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.time_trigger_setting.TimeTriggerSettingData
   src.bluetooth_sig.gatt.descriptors.time_trigger_setting.TimeTriggerSettingDescriptor


Module Contents
---------------

.. py:class:: TimeTriggerSettingData

   Bases: :py:obj:`msgspec.Struct`


   Time Trigger Setting descriptor data.


   .. py:attribute:: time_interval
      :type:  int


.. py:class:: TimeTriggerSettingDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Time Trigger Setting Descriptor (0x290E).

   Defines time-based trigger settings for measurements.
   Contains time interval in seconds for periodic triggering.


   .. py:method:: get_time_interval(data: bytes) -> int

      Get the time interval in seconds.




src.bluetooth_sig.gatt.descriptors.imd_trigger_setting
======================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.imd_trigger_setting

.. autoapi-nested-parse::

   IMD Trigger Setting Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.imd_trigger_setting.IMDTriggerSettingData
   src.bluetooth_sig.gatt.descriptors.imd_trigger_setting.IMDTriggerSettingDescriptor


Module Contents
---------------

.. py:class:: IMDTriggerSettingData

   Bases: :py:obj:`msgspec.Struct`


   IMD Trigger Setting descriptor data.


   .. py:attribute:: trigger_setting
      :type:  int


.. py:class:: IMDTriggerSettingDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   IMD Trigger Setting Descriptor (0x2915).

   Defines trigger settings for Impedance Measurement Devices (IMD).
   Contains trigger configuration for IMD measurements.

   Initialize descriptor with resolved information.


   .. py:method:: get_trigger_setting(data: bytes) -> int

      Get the IMD trigger setting.




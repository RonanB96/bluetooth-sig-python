src.bluetooth_sig.gatt.descriptors.environmental_sensing_trigger_setting
========================================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.environmental_sensing_trigger_setting

.. autoapi-nested-parse::

   Environmental Sensing Trigger Setting Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.environmental_sensing_trigger_setting.EnvironmentalSensingTriggerSettingData
   src.bluetooth_sig.gatt.descriptors.environmental_sensing_trigger_setting.EnvironmentalSensingTriggerSettingDescriptor


Module Contents
---------------

.. py:class:: EnvironmentalSensingTriggerSettingData

   Bases: :py:obj:`msgspec.Struct`


   Environmental Sensing Trigger Setting descriptor data.


   .. py:attribute:: condition
      :type:  int


   .. py:attribute:: operand
      :type:  int


.. py:class:: EnvironmentalSensingTriggerSettingDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Environmental Sensing Trigger Setting Descriptor (0x290D).

   Defines trigger conditions for environmental sensing measurements.
   Contains condition and operand for triggering measurements.

   Initialize descriptor with resolved information.


   .. py:method:: get_condition(data: bytes) -> int

      Get the trigger condition.



   .. py:method:: get_operand(data: bytes) -> int

      Get the trigger operand.




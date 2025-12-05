src.bluetooth_sig.gatt.descriptors.value_trigger_setting
========================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.value_trigger_setting

.. autoapi-nested-parse::

   Value Trigger Setting Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.value_trigger_setting.TriggerCondition
   src.bluetooth_sig.gatt.descriptors.value_trigger_setting.ValueTriggerSettingData
   src.bluetooth_sig.gatt.descriptors.value_trigger_setting.ValueTriggerSettingDescriptor


Module Contents
---------------

.. py:class:: TriggerCondition

   Bases: :py:obj:`enum.IntEnum`


   Trigger condition values for Value Trigger Setting.


   .. py:attribute:: NONE
      :value: 0



   .. py:attribute:: EQUAL_TO
      :value: 1



   .. py:attribute:: NOT_EQUAL_TO
      :value: 2



   .. py:attribute:: LESS_THAN
      :value: 3



   .. py:attribute:: LESS_THAN_OR_EQUAL_TO
      :value: 4



   .. py:attribute:: GREATER_THAN
      :value: 5



   .. py:attribute:: GREATER_THAN_OR_EQUAL_TO
      :value: 6



.. py:class:: ValueTriggerSettingData

   Bases: :py:obj:`msgspec.Struct`


   Value Trigger Setting descriptor data.


   .. py:attribute:: condition
      :type:  int


   .. py:attribute:: value
      :type:  int


.. py:class:: ValueTriggerSettingDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Value Trigger Setting Descriptor (0x290A).

   Defines trigger conditions for value-based notifications.
   Contains condition and reference value for triggering.


   .. py:method:: get_condition(data: bytes) -> int

      Get the trigger condition.



   .. py:method:: get_trigger_value(data: bytes) -> int

      Get the trigger reference value.



   .. py:method:: is_condition_equal_to(data: bytes) -> bool

      Check if condition is 'equal to'.



   .. py:method:: is_condition_greater_than(data: bytes) -> bool

      Check if condition is 'greater than'.




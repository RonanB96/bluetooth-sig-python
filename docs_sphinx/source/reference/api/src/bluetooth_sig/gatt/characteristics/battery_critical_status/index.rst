src.bluetooth_sig.gatt.characteristics.battery_critical_status
==============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.battery_critical_status

.. autoapi-nested-parse::

   Battery Critical Status characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.battery_critical_status.BatteryCriticalStatus
   src.bluetooth_sig.gatt.characteristics.battery_critical_status.BatteryCriticalStatusValues
   src.bluetooth_sig.gatt.characteristics.battery_critical_status.BatteryCriticalStatusCharacteristic


Module Contents
---------------

.. py:class:: BatteryCriticalStatus

   Bases: :py:obj:`msgspec.Struct`


   Battery Critical Status data structure.


   .. py:attribute:: critical_power_state
      :type:  bool


   .. py:attribute:: immediate_service_required
      :type:  bool


.. py:class:: BatteryCriticalStatusValues

   Bases: :py:obj:`enum.IntFlag`


   Bit mask constants for Battery Critical Status characteristic.


   .. py:attribute:: CRITICAL_POWER_STATE_MASK
      :value: 1



   .. py:attribute:: IMMEDIATE_SERVICE_REQUIRED_MASK
      :value: 2



.. py:class:: BatteryCriticalStatusCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Battery Critical Status characteristic.


   .. py:attribute:: expected_length
      :value: 1



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> BatteryCriticalStatus

      Decode the battery critical status value.



   .. py:method:: encode_value(data: BatteryCriticalStatus) -> bytearray

      Encode the battery critical status value.




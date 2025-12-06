src.bluetooth_sig.gatt.characteristics.battery_critical_status
==============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.battery_critical_status

.. autoapi-nested-parse::

   Battery Critical Status characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.battery_critical_status.BatteryCriticalStatus
   src.bluetooth_sig.gatt.characteristics.battery_critical_status.BatteryCriticalStatusCharacteristic
   src.bluetooth_sig.gatt.characteristics.battery_critical_status.BatteryCriticalStatusValues


Module Contents
---------------

.. py:class:: BatteryCriticalStatus

   Bases: :py:obj:`msgspec.Struct`


   Battery Critical Status data structure.


   .. py:attribute:: critical_power_state
      :type:  bool


   .. py:attribute:: immediate_service_required
      :type:  bool


.. py:class:: BatteryCriticalStatusCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Battery Critical Status characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> BatteryCriticalStatus

      Decode the battery critical status value.



   .. py:method:: encode_value(data: BatteryCriticalStatus) -> bytearray

      Encode the battery critical status value.



   .. py:attribute:: expected_length
      :value: 1



.. py:class:: BatteryCriticalStatusValues

   Bases: :py:obj:`enum.IntFlag`


   Bit mask constants for Battery Critical Status characteristic.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: CRITICAL_POWER_STATE_MASK
      :value: 1



   .. py:attribute:: IMMEDIATE_SERVICE_REQUIRED_MASK
      :value: 2




src.bluetooth_sig.gatt.characteristics.battery_level_status
===========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.battery_level_status

.. autoapi-nested-parse::

   Battery Level Status characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.battery_level_status.BatteryLevelStatus
   src.bluetooth_sig.gatt.characteristics.battery_level_status.BatteryLevelStatusCharacteristic
   src.bluetooth_sig.gatt.characteristics.battery_level_status.BatteryLevelStatusFlags


Module Contents
---------------

.. py:class:: BatteryLevelStatus

   Bases: :py:obj:`msgspec.Struct`


   Battery Level Status data structure.


   .. py:attribute:: battery_charge_level
      :type:  bluetooth_sig.types.battery.BatteryChargeLevel


   .. py:attribute:: battery_charge_state
      :type:  bluetooth_sig.types.battery.BatteryChargeState


   .. py:attribute:: battery_fault
      :type:  bool | None
      :value: None



   .. py:attribute:: battery_level
      :type:  int | None
      :value: None



   .. py:attribute:: battery_present
      :type:  bool


   .. py:attribute:: charging_fault_battery
      :type:  bool


   .. py:attribute:: charging_fault_external_power
      :type:  bool


   .. py:attribute:: charging_fault_other
      :type:  bool


   .. py:attribute:: charging_type
      :type:  bluetooth_sig.types.battery.BatteryChargingType


   .. py:attribute:: flags
      :type:  BatteryLevelStatusFlags


   .. py:attribute:: identifier
      :type:  int | None
      :value: None



   .. py:attribute:: service_required
      :type:  bluetooth_sig.types.battery.ServiceRequiredState | None
      :value: None



   .. py:attribute:: wired_external_power_connected
      :type:  bluetooth_sig.types.battery.PowerConnectionState


   .. py:attribute:: wireless_external_power_connected
      :type:  bluetooth_sig.types.battery.PowerConnectionState


.. py:class:: BatteryLevelStatusCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Battery Level Status characteristic (0x2BED).

   org.bluetooth.characteristic.battery_level_status


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> BatteryLevelStatus

      Decode the battery level status value.



   .. py:method:: encode_value(data: BatteryLevelStatus) -> bytearray

      Encode the battery level status value.



   .. py:attribute:: BIT_START_BATTERY_FAULT
      :value: 2



   .. py:attribute:: BIT_START_BATTERY_PRESENT
      :value: 0



   .. py:attribute:: BIT_START_CHARGE_LEVEL
      :value: 7



   .. py:attribute:: BIT_START_CHARGE_STATE
      :value: 5



   .. py:attribute:: BIT_START_CHARGING_TYPE
      :value: 9



   .. py:attribute:: BIT_START_FAULT_BATTERY
      :value: 12



   .. py:attribute:: BIT_START_FAULT_EXTERNAL
      :value: 13



   .. py:attribute:: BIT_START_FAULT_OTHER
      :value: 14



   .. py:attribute:: BIT_START_SERVICE_REQUIRED
      :value: 0



   .. py:attribute:: BIT_START_WIRED_POWER
      :value: 1



   .. py:attribute:: BIT_START_WIRELESS_POWER
      :value: 3



   .. py:attribute:: BIT_WIDTH_BATTERY_FAULT
      :value: 1



   .. py:attribute:: BIT_WIDTH_BATTERY_PRESENT
      :value: 1



   .. py:attribute:: BIT_WIDTH_CHARGE_LEVEL
      :value: 2



   .. py:attribute:: BIT_WIDTH_CHARGE_STATE
      :value: 2



   .. py:attribute:: BIT_WIDTH_CHARGING_TYPE
      :value: 3



   .. py:attribute:: BIT_WIDTH_FAULT_BATTERY
      :value: 1



   .. py:attribute:: BIT_WIDTH_FAULT_EXTERNAL
      :value: 1



   .. py:attribute:: BIT_WIDTH_FAULT_OTHER
      :value: 1



   .. py:attribute:: BIT_WIDTH_SERVICE_REQUIRED
      :value: 2



   .. py:attribute:: BIT_WIDTH_WIRED_POWER
      :value: 2



   .. py:attribute:: BIT_WIDTH_WIRELESS_POWER
      :value: 2



   .. py:attribute:: allow_variable_length
      :value: True



   .. py:attribute:: max_length
      :value: 7



   .. py:attribute:: min_length
      :value: 3



.. py:class:: BatteryLevelStatusFlags

   Bases: :py:obj:`enum.IntFlag`


   Battery Level Status flags.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: ADDITIONAL_STATUS_PRESENT
      :value: 4



   .. py:attribute:: BATTERY_LEVEL_PRESENT
      :value: 2



   .. py:attribute:: IDENTIFIER_PRESENT
      :value: 1




src.bluetooth_sig.types.battery
===============================

.. py:module:: src.bluetooth_sig.types.battery

.. autoapi-nested-parse::

   Battery-related enumerations for power state characteristics.

   Defines enums for battery charge states, charge levels, charging types,
   and fault reasons to replace string usage with type-safe alternatives.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.battery.BatteryChargeLevel
   src.bluetooth_sig.types.battery.BatteryChargeState
   src.bluetooth_sig.types.battery.BatteryChargingType
   src.bluetooth_sig.types.battery.BatteryFaultReason
   src.bluetooth_sig.types.battery.PowerConnectionState
   src.bluetooth_sig.types.battery.ServiceRequiredState


Module Contents
---------------

.. py:class:: BatteryChargeLevel

   Bases: :py:obj:`enum.IntEnum`


   Battery charge level enumeration.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:method:: from_byte(byte_val: int) -> BatteryChargeLevel
      :classmethod:


      Create enum from byte value with fallback.



   .. py:attribute:: CRITICALLY_LOW
      :value: 3



   .. py:attribute:: GOOD
      :value: 1



   .. py:attribute:: LOW
      :value: 2



   .. py:attribute:: UNKNOWN
      :value: 0



.. py:class:: BatteryChargeState

   Bases: :py:obj:`enum.IntEnum`


   Battery charge state enumeration.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:method:: from_byte(byte_val: int) -> BatteryChargeState
      :classmethod:


      Create enum from byte value with fallback.



   .. py:attribute:: CHARGING
      :value: 1



   .. py:attribute:: DISCHARGING
      :value: 2



   .. py:attribute:: NOT_CHARGING
      :value: 3



   .. py:attribute:: UNKNOWN
      :value: 0



.. py:class:: BatteryChargingType

   Bases: :py:obj:`enum.IntEnum`


   Battery charging type enumeration.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:method:: from_byte(byte_val: int) -> BatteryChargingType
      :classmethod:


      Create enum from byte value with fallback.



   .. py:attribute:: CONSTANT_CURRENT
      :value: 1



   .. py:attribute:: CONSTANT_VOLTAGE
      :value: 2



   .. py:attribute:: FLOAT
      :value: 4



   .. py:attribute:: TRICKLE
      :value: 3



   .. py:attribute:: UNKNOWN
      :value: 0



.. py:class:: BatteryFaultReason

   Bases: :py:obj:`enum.IntEnum`


   Battery fault reason enumeration.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: BATTERY_FAULT
      :value: 0



   .. py:attribute:: EXTERNAL_POWER_FAULT
      :value: 1



   .. py:attribute:: OTHER_FAULT
      :value: 2



.. py:class:: PowerConnectionState

   Bases: :py:obj:`enum.IntEnum`


   Power connection state enumeration.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: NO
      :value: 0



   .. py:attribute:: RFU
      :value: 3



   .. py:attribute:: UNKNOWN
      :value: 2



   .. py:attribute:: YES
      :value: 1



.. py:class:: ServiceRequiredState

   Bases: :py:obj:`enum.IntEnum`


   Service required state enumeration.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: FALSE
      :value: 0



   .. py:attribute:: RFU
      :value: 3



   .. py:attribute:: TRUE
      :value: 1



   .. py:attribute:: UNKNOWN
      :value: 2




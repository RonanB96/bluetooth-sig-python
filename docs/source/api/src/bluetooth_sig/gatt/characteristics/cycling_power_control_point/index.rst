src.bluetooth_sig.gatt.characteristics.cycling_power_control_point
==================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.cycling_power_control_point

.. autoapi-nested-parse::

   Cycling Power Control Point characteristic implementation.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.cycling_power_control_point.MIN_OP_CODE_LENGTH


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.cycling_power_control_point.CyclingPowerControlPointCharacteristic
   src.bluetooth_sig.gatt.characteristics.cycling_power_control_point.CyclingPowerControlPointData
   src.bluetooth_sig.gatt.characteristics.cycling_power_control_point.CyclingPowerOpCode
   src.bluetooth_sig.gatt.characteristics.cycling_power_control_point.CyclingPowerResponseValue
   src.bluetooth_sig.gatt.characteristics.cycling_power_control_point.OpCodeParameters


Module Contents
---------------

.. py:class:: CyclingPowerControlPointCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Cycling Power Control Point characteristic (0x2A66).

   Used for control and configuration of cycling power sensors.
   Provides commands for calibration, configuration, and sensor
   control.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> CyclingPowerControlPointData

      Parse cycling power control point data.

      Format: Op Code(1) + [Request Parameter] or Response Code(1) + [Response Parameter].

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: CyclingPowerControlPointData containing parsed control point data.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: CyclingPowerControlPointData | int) -> bytearray

      Encode cycling power control point value back to bytes.

      :param data: CyclingPowerControlPointData with op_code and optional parameters, or raw op_code integer

      :returns: Encoded bytes representing the control point command



   .. py:attribute:: CHAIN_LENGTH_RESOLUTION
      :value: 10.0



   .. py:attribute:: CHAIN_WEIGHT_RESOLUTION
      :value: 10.0



   .. py:attribute:: CRANK_LENGTH_RESOLUTION
      :value: 2.0



   .. py:attribute:: CUMULATIVE_VALUE_LENGTH
      :value: 5



   .. py:attribute:: MIN_OP_CODE_LENGTH
      :value: 1



   .. py:attribute:: RESPONSE_CODE_LENGTH
      :value: 3



   .. py:attribute:: SENSOR_LOCATION_LENGTH
      :value: 2



   .. py:attribute:: TWO_BYTE_PARAM_LENGTH
      :value: 3



.. py:class:: CyclingPowerControlPointData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Cycling Power Control Point characteristic.


   .. py:attribute:: chain_length
      :type:  float | None
      :value: None



   .. py:attribute:: chain_weight
      :type:  float | None
      :value: None



   .. py:attribute:: crank_length
      :type:  float | None
      :value: None



   .. py:attribute:: cumulative_value
      :type:  int | None
      :value: None



   .. py:attribute:: measurement_mask
      :type:  int | None
      :value: None



   .. py:attribute:: op_code
      :type:  CyclingPowerOpCode


   .. py:attribute:: request_op_code
      :type:  CyclingPowerOpCode | None
      :value: None



   .. py:attribute:: response_value
      :type:  CyclingPowerResponseValue | None
      :value: None



   .. py:attribute:: sensor_location
      :type:  int | None
      :value: None



   .. py:attribute:: span_length
      :type:  int | None
      :value: None



.. py:class:: CyclingPowerOpCode

   Bases: :py:obj:`enum.IntEnum`


   Cycling Power Control Point operation codes as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: MASK_CYCLING_POWER_MEASUREMENT
      :value: 13



   .. py:attribute:: REQUEST_CHAIN_LENGTH
      :value: 7



   .. py:attribute:: REQUEST_CHAIN_WEIGHT
      :value: 9



   .. py:attribute:: REQUEST_CRANK_LENGTH
      :value: 5



   .. py:attribute:: REQUEST_FACTORY_CALIBRATION_DATE
      :value: 15



   .. py:attribute:: REQUEST_SAMPLING_RATE
      :value: 14



   .. py:attribute:: REQUEST_SPAN_LENGTH
      :value: 11



   .. py:attribute:: REQUEST_SUPPORTED_SENSOR_LOCATIONS
      :value: 3



   .. py:attribute:: RESPONSE_CODE
      :value: 32



   .. py:attribute:: SET_CHAIN_LENGTH
      :value: 6



   .. py:attribute:: SET_CHAIN_WEIGHT
      :value: 8



   .. py:attribute:: SET_CRANK_LENGTH
      :value: 4



   .. py:attribute:: SET_CUMULATIVE_VALUE
      :value: 1



   .. py:attribute:: SET_SPAN_LENGTH
      :value: 10



   .. py:attribute:: START_OFFSET_COMPENSATION
      :value: 12



   .. py:attribute:: UPDATE_SENSOR_LOCATION
      :value: 2



.. py:class:: CyclingPowerResponseValue

   Bases: :py:obj:`enum.IntEnum`


   Cycling Power Control Point response values as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: INVALID_PARAMETER
      :value: 3



   .. py:attribute:: OPERATION_FAILED
      :value: 4



   .. py:attribute:: OP_CODE_NOT_SUPPORTED
      :value: 2



   .. py:attribute:: SUCCESS
      :value: 1



.. py:class:: OpCodeParameters

   Bases: :py:obj:`msgspec.Struct`


   Parsed operation code parameters.


   .. py:attribute:: chain_length
      :type:  float | None


   .. py:attribute:: chain_weight
      :type:  float | None


   .. py:attribute:: crank_length
      :type:  float | None


   .. py:attribute:: cumulative_value
      :type:  int | None


   .. py:attribute:: measurement_mask
      :type:  int | None


   .. py:attribute:: request_op_code
      :type:  CyclingPowerOpCode | None


   .. py:attribute:: response_value
      :type:  CyclingPowerResponseValue | None


   .. py:attribute:: sensor_location
      :type:  int | None


   .. py:attribute:: span_length
      :type:  int | None


.. py:data:: MIN_OP_CODE_LENGTH
   :value: 1



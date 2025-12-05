src.bluetooth_sig.gatt.characteristics.ln_control_point
=======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.ln_control_point

.. autoapi-nested-parse::

   LN Control Point characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.ln_control_point.LNControlPointOpCode
   src.bluetooth_sig.gatt.characteristics.ln_control_point.LNControlPointResponseValue
   src.bluetooth_sig.gatt.characteristics.ln_control_point.LNControlPointData
   src.bluetooth_sig.gatt.characteristics.ln_control_point.LNControlPointCharacteristic


Module Contents
---------------

.. py:class:: LNControlPointOpCode

   Bases: :py:obj:`enum.IntEnum`


   LN Control Point operation codes as per Bluetooth SIG specification.


   .. py:attribute:: SET_CUMULATIVE_VALUE
      :value: 1



   .. py:attribute:: MASK_LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT
      :value: 2



   .. py:attribute:: NAVIGATION_CONTROL
      :value: 3



   .. py:attribute:: REQUEST_NUMBER_OF_ROUTES
      :value: 4



   .. py:attribute:: REQUEST_NAME_OF_ROUTE
      :value: 5



   .. py:attribute:: SELECT_ROUTE
      :value: 6



   .. py:attribute:: SET_FIX_RATE
      :value: 7



   .. py:attribute:: SET_ELEVATION
      :value: 8



   .. py:attribute:: RESPONSE_CODE
      :value: 32



.. py:class:: LNControlPointResponseValue

   Bases: :py:obj:`enum.IntEnum`


   LN Control Point response values as per Bluetooth SIG specification.


   .. py:attribute:: SUCCESS
      :value: 1



   .. py:attribute:: OP_CODE_NOT_SUPPORTED
      :value: 2



   .. py:attribute:: INVALID_OPERAND
      :value: 3



   .. py:attribute:: OPERATION_FAILED
      :value: 4



.. py:class:: LNControlPointData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from LN Control Point characteristic.


   .. py:attribute:: op_code
      :type:  LNControlPointOpCode


   .. py:attribute:: cumulative_value
      :type:  int | None
      :value: None



   .. py:attribute:: content_mask
      :type:  int | None
      :value: None



   .. py:attribute:: navigation_control_value
      :type:  int | None
      :value: None



   .. py:attribute:: route_number
      :type:  int | None
      :value: None



   .. py:attribute:: route_name
      :type:  str | None
      :value: None



   .. py:attribute:: fix_rate
      :type:  int | None
      :value: None



   .. py:attribute:: elevation
      :type:  float | None
      :value: None



   .. py:attribute:: request_op_code
      :type:  LNControlPointOpCode | None
      :value: None



   .. py:attribute:: response_value
      :type:  LNControlPointResponseValue | None
      :value: None



   .. py:attribute:: response_parameter
      :type:  int | str | datetime.datetime | bytearray | None
      :value: None



.. py:class:: LNControlPointCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   LN Control Point characteristic.

   Used to enable device-specific procedures related to the exchange of location and navigation information.


   .. py:attribute:: min_length
      :value: 1



   .. py:attribute:: max_length
      :value: 18



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> LNControlPointData

      Parse LN control point data according to Bluetooth specification.

      Format: Op Code(1) + Parameter(0-17).

      :param data: Raw bytearray from BLE characteristic
      :param ctx: Optional context providing surrounding context (may be None)

      :returns: LNControlPointData containing parsed control point data



   .. py:method:: encode_value(data: LNControlPointData) -> bytearray

      Encode LNControlPointData back to bytes.

      :param data: LNControlPointData instance to encode

      :returns: Encoded bytes representing the LN control point data




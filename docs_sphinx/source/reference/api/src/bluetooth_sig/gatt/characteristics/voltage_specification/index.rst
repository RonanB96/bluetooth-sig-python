src.bluetooth_sig.gatt.characteristics.voltage_specification
============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.voltage_specification

.. autoapi-nested-parse::

   Voltage Specification characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.voltage_specification.VoltageSpecificationData
   src.bluetooth_sig.gatt.characteristics.voltage_specification.VoltageSpecificationCharacteristic


Module Contents
---------------

.. py:class:: VoltageSpecificationData

   Bases: :py:obj:`msgspec.Struct`


   Data class for voltage specification.


   .. py:attribute:: minimum
      :type:  float


   .. py:attribute:: maximum
      :type:  float


.. py:class:: VoltageSpecificationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Voltage Specification characteristic (0x2B19).

   org.bluetooth.characteristic.voltage_specification

   Voltage Specification characteristic.

   Specifies minimum and maximum voltage values for electrical
   specifications.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> VoltageSpecificationData

      Parse voltage specification data (2x uint16 in units of 1/64 V).

      :param data: Raw bytes from the characteristic read.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: VoltageSpecificationData with 'minimum' and 'maximum' voltage specification values in Volts.

      :raises ValueError: If data is insufficient.



   .. py:method:: encode_value(data: VoltageSpecificationData) -> bytearray

      Encode voltage specification value back to bytes.

      :param data: VoltageSpecificationData instance with 'minimum' and 'maximum' voltage values in Volts

      :returns: Encoded bytes representing the voltage specification (2x uint16, 1/64 V resolution)




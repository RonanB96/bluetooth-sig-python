src.bluetooth_sig.gatt.characteristics.electric_current_specification
=====================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.electric_current_specification

.. autoapi-nested-parse::

   Electric Current Specification characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.electric_current_specification.ElectricCurrentSpecificationData
   src.bluetooth_sig.gatt.characteristics.electric_current_specification.ElectricCurrentSpecificationCharacteristic


Module Contents
---------------

.. py:class:: ElectricCurrentSpecificationData

   Bases: :py:obj:`msgspec.Struct`


   Data class for electric current specification.


   .. py:attribute:: minimum
      :type:  float


   .. py:attribute:: maximum
      :type:  float


.. py:class:: ElectricCurrentSpecificationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Electric Current Specification characteristic (0x2AF0).

   org.bluetooth.characteristic.electric_current_specification

   Electric Current Specification characteristic.

   Specifies minimum and maximum current values for electrical
   specifications.


   .. py:method:: decode_value(data: bytearray, _ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> ElectricCurrentSpecificationData

      Parse current specification data (2x uint16 in units of 0.01 A).

      :param data: Raw bytes from the characteristic read

      :returns: ElectricCurrentSpecificationData with 'minimum' and 'maximum' current specification values in Amperes

      :raises ValueError: If data is insufficient



   .. py:method:: encode_value(data: ElectricCurrentSpecificationData) -> bytearray

      Encode electric current specification value back to bytes.

      :param data: ElectricCurrentSpecificationData instance

      :returns: Encoded bytes representing the current specification (2x uint16, 0.01 A resolution)




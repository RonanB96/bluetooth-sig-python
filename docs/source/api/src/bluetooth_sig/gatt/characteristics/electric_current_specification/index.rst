src.bluetooth_sig.gatt.characteristics.electric_current_specification
=====================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.electric_current_specification

.. autoapi-nested-parse::

   Electric Current Specification characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.electric_current_specification.ElectricCurrentSpecificationCharacteristic
   src.bluetooth_sig.gatt.characteristics.electric_current_specification.ElectricCurrentSpecificationData


Module Contents
---------------

.. py:class:: ElectricCurrentSpecificationCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Electric Current Specification characteristic (0x2AF0).

   org.bluetooth.characteristic.electric_current_specification

   Electric Current Specification characteristic.

   Specifies minimum and maximum current values for electrical
   specifications.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, _ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> ElectricCurrentSpecificationData

      Parse current specification data (2x uint16 in units of 0.01 A).

      :param data: Raw bytes from the characteristic read

      :returns: ElectricCurrentSpecificationData with 'minimum' and 'maximum' current specification values in Amperes

      :raises ValueError: If data is insufficient



   .. py:method:: encode_value(data: ElectricCurrentSpecificationData) -> bytearray

      Encode electric current specification value back to bytes.

      :param data: ElectricCurrentSpecificationData instance

      :returns: Encoded bytes representing the current specification (2x uint16, 0.01 A resolution)



.. py:class:: ElectricCurrentSpecificationData

   Bases: :py:obj:`msgspec.Struct`


   Data class for electric current specification.


   .. py:attribute:: maximum
      :type:  float


   .. py:attribute:: minimum
      :type:  float



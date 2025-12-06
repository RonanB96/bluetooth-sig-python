src.bluetooth_sig.gatt.characteristics.power_specification
==========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.power_specification

.. autoapi-nested-parse::

   Power Specification characteristic implementation.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.power_specification.VALUE_NOT_VALID
   src.bluetooth_sig.gatt.characteristics.power_specification.VALUE_UNKNOWN


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.power_specification.PowerSpecificationCharacteristic
   src.bluetooth_sig.gatt.characteristics.power_specification.PowerSpecificationData


Module Contents
---------------

.. py:class:: PowerSpecificationCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Power Specification characteristic (0x2B06).

   org.bluetooth.characteristic.power_specification

   The Power Specification characteristic is used to represent a specification of power values.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> PowerSpecificationData

      Decode the power specification values.



   .. py:method:: encode_value(data: PowerSpecificationData) -> bytearray

      Encode the power specification values.



   .. py:attribute:: expected_length
      :value: 9



.. py:class:: PowerSpecificationData(minimum: float | None, typical: float | None, maximum: float | None)

   Data class for Power Specification characteristic.

   Initialize Power Specification data.

   :param minimum: Minimum power value in watts, or None if not valid/known
   :param typical: Typical power value in watts, or None if not valid/known
   :param maximum: Maximum power value in watts, or None if not valid/known


   .. py:attribute:: maximum


   .. py:attribute:: minimum


   .. py:attribute:: typical


.. py:data:: VALUE_NOT_VALID
   :value: 16777214


.. py:data:: VALUE_UNKNOWN
   :value: 16777215



src.bluetooth_sig.gatt.characteristics.voc_concentration
========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.voc_concentration

.. autoapi-nested-parse::

   VOC Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.voc_concentration.VOCConcentrationCharacteristic
   src.bluetooth_sig.gatt.characteristics.voc_concentration.VOCConcentrationValues


Module Contents
---------------

.. py:class:: VOCConcentrationCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Volatile Organic Compounds concentration characteristic (0x2BE7).

   Uses uint16 format as per SIG specification.
   Unit: ppb (parts per billion)
   Range: 0-65533
   (VOCConcentrationValues.VALUE_65534_OR_GREATER = ≥65534,
    VOCConcentrationValues.VALUE_UNKNOWN = unknown)

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> int

      Parse VOC concentration value with special value handling.



   .. py:method:: encode_value(data: int) -> bytearray

      Encode VOC concentration with special value handling.



   .. py:attribute:: max_value
      :type:  int | float | None
      :value: 65533



   .. py:attribute:: min_value
      :type:  int | float | None
      :value: 0



.. py:class:: VOCConcentrationValues

   Special values for VOC Concentration characteristic per Bluetooth SIG specification.


   .. py:attribute:: VALUE_65534_OR_GREATER
      :value: 65534



   .. py:attribute:: VALUE_UNKNOWN
      :value: 65535




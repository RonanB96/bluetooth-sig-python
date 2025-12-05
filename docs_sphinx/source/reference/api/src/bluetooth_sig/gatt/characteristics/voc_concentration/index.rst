src.bluetooth_sig.gatt.characteristics.voc_concentration
========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.voc_concentration

.. autoapi-nested-parse::

   VOC Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.voc_concentration.VOCConcentrationValues
   src.bluetooth_sig.gatt.characteristics.voc_concentration.VOCConcentrationCharacteristic


Module Contents
---------------

.. py:class:: VOCConcentrationValues

   Special values for VOC Concentration characteristic per Bluetooth SIG specification.


   .. py:attribute:: VALUE_65534_OR_GREATER
      :value: 65534



   .. py:attribute:: VALUE_UNKNOWN
      :value: 65535



.. py:class:: VOCConcentrationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Volatile Organic Compounds concentration characteristic (0x2BE7).

   Uses uint16 format as per SIG specification.
   Unit: ppb (parts per billion)
   Range: 0-65533
   (VOCConcentrationValues.VALUE_65534_OR_GREATER = ≥65534,
    VOCConcentrationValues.VALUE_UNKNOWN = unknown)


   .. py:attribute:: min_value
      :type:  int | float | None
      :value: 0



   .. py:attribute:: max_value
      :type:  int | float | None
      :value: 65533



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> int

      Parse VOC concentration value with special value handling.



   .. py:method:: encode_value(data: int) -> bytearray

      Encode VOC concentration with special value handling.




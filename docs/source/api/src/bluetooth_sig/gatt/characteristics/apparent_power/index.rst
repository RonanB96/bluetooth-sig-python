src.bluetooth_sig.gatt.characteristics.apparent_power
=====================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.apparent_power

.. autoapi-nested-parse::

   Apparent Power characteristic implementation.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.apparent_power.VALUE_NOT_VALID
   src.bluetooth_sig.gatt.characteristics.apparent_power.VALUE_UNKNOWN


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.apparent_power.ApparentPowerCharacteristic


Module Contents
---------------

.. py:class:: ApparentPowerCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Apparent Power characteristic.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float | None

      Decode the apparent power value.



   .. py:method:: encode_value(data: float) -> bytearray

      Encode the apparent power value.



   .. py:attribute:: expected_length
      :value: 3



.. py:data:: VALUE_NOT_VALID
   :value: 16777214


.. py:data:: VALUE_UNKNOWN
   :value: 16777215



src.bluetooth_sig.gatt.characteristics.alert_status
===================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.alert_status

.. autoapi-nested-parse::

   Alert Status characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.alert_status.AlertStatusData
   src.bluetooth_sig.gatt.characteristics.alert_status.AlertStatusCharacteristic


Module Contents
---------------

.. py:class:: AlertStatusData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Alert Status characteristic.


   .. py:attribute:: ringer_state
      :type:  bool


   .. py:attribute:: vibrate_state
      :type:  bool


   .. py:attribute:: display_alert_status
      :type:  bool


.. py:class:: AlertStatusCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Alert Status characteristic (0x2A3F).

   org.bluetooth.characteristic.alert_status

   The Alert Status characteristic defines the Status of alert.
   Bit 0: Ringer State (0=not active, 1=active)
   Bit 1: Vibrate State (0=not active, 1=active)
   Bit 2: Display Alert Status (0=not active, 1=active)
   Bits 3-7: Reserved for future use


   .. py:attribute:: RINGER_STATE_MASK
      :value: 1



   .. py:attribute:: VIBRATE_STATE_MASK
      :value: 2



   .. py:attribute:: DISPLAY_ALERT_STATUS_MASK
      :value: 4



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> AlertStatusData

      Parse alert status data according to Bluetooth specification.

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext (unused)

      :returns: AlertStatusData containing parsed alert status flags.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: AlertStatusData) -> bytearray

      Encode AlertStatusData back to bytes.

      :param data: AlertStatusData instance to encode

      :returns: Encoded bytes representing the alert status




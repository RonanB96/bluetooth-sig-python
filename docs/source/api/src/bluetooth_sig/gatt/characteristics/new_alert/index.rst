src.bluetooth_sig.gatt.characteristics.new_alert
================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.new_alert

.. autoapi-nested-parse::

   New Alert characteristic (0x2A46) implementation.

   Represents a new alert with category, count, and optional text information.
   Used by Alert Notification Service (0x1811).

   Based on Bluetooth SIG GATT Specification:
   - New Alert: Variable length (Category ID + Number of New Alert + Text String)



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.new_alert.NewAlertCharacteristic
   src.bluetooth_sig.gatt.characteristics.new_alert.NewAlertData


Module Contents
---------------

.. py:class:: NewAlertCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   New Alert characteristic (0x2A46).

   Represents the category, count, and brief text for a new alert.

   Structure (variable length):
   - Category ID: uint8 (0=Simple Alert, 1=Email, etc.)
   - Number of New Alert: uint8 (0-255, count of new alerts)
   - Text String Information: utf8s (0-18 characters, optional brief text)

   Used by Alert Notification Service (0x1811).


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> NewAlertData

      Decode New Alert data from bytes.

      :param data: Raw characteristic data (minimum 2 bytes)
      :param ctx: Optional characteristic context

      :returns: NewAlertData with all fields

      :raises ValueError: If data is insufficient or contains invalid values



   .. py:method:: encode_value(data: NewAlertData) -> bytearray

      Encode New Alert data to bytes.

      :param data: NewAlertData to encode

      :returns: Encoded new alert (variable length)

      :raises ValueError: If data contains invalid values



.. py:class:: NewAlertData

   Bases: :py:obj:`msgspec.Struct`


   New Alert characteristic data structure.


   .. py:attribute:: category_id
      :type:  src.bluetooth_sig.types.AlertCategoryID


   .. py:attribute:: number_of_new_alert
      :type:  int


   .. py:attribute:: text_string_information
      :type:  str



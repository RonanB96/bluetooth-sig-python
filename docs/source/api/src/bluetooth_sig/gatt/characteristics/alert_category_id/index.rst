src.bluetooth_sig.gatt.characteristics.alert_category_id
========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.alert_category_id

.. autoapi-nested-parse::

   Alert Category ID characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.alert_category_id.AlertCategoryIdCharacteristic


Module Contents
---------------

.. py:class:: AlertCategoryIdCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Alert Category ID characteristic (0x2A43).

   org.bluetooth.characteristic.alert_category_id

   The Alert Category ID characteristic is used to represent predefined categories of alerts and messages.
   The structure of this characteristic is defined below.

   Valid values:
       - 0: Simple Alert
       - 1: Email
       - 2: News
       - 3: Call
       - 4: Missed Call
       - 5: SMS/MMS
       - 6: Voice Mail
       - 7: Schedule
       - 8: High Prioritized Alert
       - 9: Instant Message
       - 10-250: Reserved for Future Use
       - 251-255: Service Specific

   Spec: Bluetooth SIG GATT Specification Supplement, Alert Category ID

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> src.bluetooth_sig.types.AlertCategoryID

      Decode alert category ID from raw bytes.

      :param data: Raw bytes from BLE characteristic (1 byte)
      :param ctx: Optional context for parsing

      :returns: AlertCategoryID enum value

      :raises ValueError: If data is less than 1 byte or value is invalid



   .. py:method:: encode_value(data: src.bluetooth_sig.types.AlertCategoryID | int) -> bytearray

      Encode alert category ID to raw bytes.

      :param data: AlertCategoryID enum value or integer

      :returns: Encoded characteristic data (1 byte)

      :raises ValueError: If data is not a valid category ID




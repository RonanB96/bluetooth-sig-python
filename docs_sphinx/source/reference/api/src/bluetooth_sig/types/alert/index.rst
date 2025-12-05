src.bluetooth_sig.types.alert
=============================

.. py:module:: src.bluetooth_sig.types.alert

.. autoapi-nested-parse::

   Alert Notification types and enumerations.

   Provides common types used across Alert Notification Service characteristics.
   Based on Bluetooth SIG GATT Specification for Alert Notification Service (0x1811).



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.types.alert.ALERT_CATEGORY_DEFINED_MAX
   src.bluetooth_sig.types.alert.ALERT_CATEGORY_RESERVED_MIN
   src.bluetooth_sig.types.alert.ALERT_CATEGORY_RESERVED_MAX
   src.bluetooth_sig.types.alert.ALERT_CATEGORY_SERVICE_SPECIFIC_MIN
   src.bluetooth_sig.types.alert.ALERT_TEXT_MAX_LENGTH
   src.bluetooth_sig.types.alert.UNREAD_COUNT_MAX
   src.bluetooth_sig.types.alert.UNREAD_COUNT_MORE_THAN_MAX
   src.bluetooth_sig.types.alert.ALERT_COMMAND_MAX


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.alert.AlertCategoryID
   src.bluetooth_sig.types.alert.AlertCategoryBitMask
   src.bluetooth_sig.types.alert.AlertNotificationCommandID


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.types.alert.validate_category_id


Module Contents
---------------

.. py:data:: ALERT_CATEGORY_DEFINED_MAX
   :value: 9


.. py:data:: ALERT_CATEGORY_RESERVED_MIN
   :value: 10


.. py:data:: ALERT_CATEGORY_RESERVED_MAX
   :value: 250


.. py:data:: ALERT_CATEGORY_SERVICE_SPECIFIC_MIN
   :value: 251


.. py:data:: ALERT_TEXT_MAX_LENGTH
   :value: 18


.. py:data:: UNREAD_COUNT_MAX
   :value: 254


.. py:data:: UNREAD_COUNT_MORE_THAN_MAX
   :value: 255


.. py:data:: ALERT_COMMAND_MAX
   :value: 5


.. py:class:: AlertCategoryID

   Bases: :py:obj:`enum.IntEnum`


   Alert category enumeration per Bluetooth SIG specification.

   Values 0-9 are defined, 10-250 reserved, 251-255 service-specific.


   .. py:attribute:: SIMPLE_ALERT
      :value: 0



   .. py:attribute:: EMAIL
      :value: 1



   .. py:attribute:: NEWS
      :value: 2



   .. py:attribute:: CALL
      :value: 3



   .. py:attribute:: MISSED_CALL
      :value: 4



   .. py:attribute:: SMS_MMS
      :value: 5



   .. py:attribute:: VOICE_MAIL
      :value: 6



   .. py:attribute:: SCHEDULE
      :value: 7



   .. py:attribute:: HIGH_PRIORITIZED_ALERT
      :value: 8



   .. py:attribute:: INSTANT_MESSAGE
      :value: 9



.. py:class:: AlertCategoryBitMask

   Bases: :py:obj:`enum.IntFlag`


   Alert category bit mask flags.

   Each bit represents support for a specific alert category.
   Bits 10-15 are reserved for future use.


   .. py:attribute:: SIMPLE_ALERT
      :value: 1



   .. py:attribute:: EMAIL
      :value: 2



   .. py:attribute:: NEWS
      :value: 4



   .. py:attribute:: CALL
      :value: 8



   .. py:attribute:: MISSED_CALL
      :value: 16



   .. py:attribute:: SMS_MMS
      :value: 32



   .. py:attribute:: VOICE_MAIL
      :value: 64



   .. py:attribute:: SCHEDULE
      :value: 128



   .. py:attribute:: HIGH_PRIORITIZED_ALERT
      :value: 256



   .. py:attribute:: INSTANT_MESSAGE
      :value: 512



.. py:class:: AlertNotificationCommandID

   Bases: :py:obj:`enum.IntEnum`


   Alert Notification Control Point command enumeration.


   .. py:attribute:: ENABLE_NEW_ALERT
      :value: 0



   .. py:attribute:: ENABLE_UNREAD_STATUS
      :value: 1



   .. py:attribute:: DISABLE_NEW_ALERT
      :value: 2



   .. py:attribute:: DISABLE_UNREAD_STATUS
      :value: 3



   .. py:attribute:: NOTIFY_NEW_ALERT_IMMEDIATELY
      :value: 4



   .. py:attribute:: NOTIFY_UNREAD_STATUS_IMMEDIATELY
      :value: 5



.. py:function:: validate_category_id(category_id_raw: int) -> AlertCategoryID

   Validate and convert raw category ID value.

   :param category_id_raw: Raw category ID value (0-255)

   :returns: AlertCategoryID enum value

   :raises ValueError: If category ID is in reserved range (10-250)



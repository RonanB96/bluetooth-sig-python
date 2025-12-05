src.bluetooth_sig.gatt.descriptors.cccd
=======================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.cccd

.. autoapi-nested-parse::

   Client Characteristic Configuration Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.cccd.CCCDFlags
   src.bluetooth_sig.gatt.descriptors.cccd.CCCDData
   src.bluetooth_sig.gatt.descriptors.cccd.CCCDDescriptor


Module Contents
---------------

.. py:class:: CCCDFlags

   Bases: :py:obj:`enum.IntFlag`


   CCCD (Client Characteristic Configuration Descriptor) flags.


   .. py:attribute:: NOTIFICATIONS_ENABLED
      :value: 1



   .. py:attribute:: INDICATIONS_ENABLED
      :value: 2



.. py:class:: CCCDData

   Bases: :py:obj:`msgspec.Struct`


   CCCD (Client Characteristic Configuration Descriptor) data.


   .. py:attribute:: notifications_enabled
      :type:  bool


   .. py:attribute:: indications_enabled
      :type:  bool


.. py:class:: CCCDDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Client Characteristic Configuration Descriptor (0x2902).

   Controls notification and indication settings for a characteristic.
   Critical for enabling BLE notifications and indications.


   .. py:method:: create_enable_notifications_value() -> bytes
      :staticmethod:


      Create value to enable notifications.



   .. py:method:: create_enable_indications_value() -> bytes
      :staticmethod:


      Create value to enable indications.



   .. py:method:: create_enable_both_value() -> bytes
      :staticmethod:


      Create value to enable both notifications and indications.



   .. py:method:: create_disable_value() -> bytes
      :staticmethod:


      Create value to disable notifications/indications.



   .. py:method:: is_notifications_enabled(data: bytes) -> bool

      Check if notifications are enabled.



   .. py:method:: is_indications_enabled(data: bytes) -> bool

      Check if indications are enabled.



   .. py:method:: is_any_enabled(data: bytes) -> bool

      Check if either notifications or indications are enabled.




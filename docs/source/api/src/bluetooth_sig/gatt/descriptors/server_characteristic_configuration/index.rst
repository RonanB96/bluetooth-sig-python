src.bluetooth_sig.gatt.descriptors.server_characteristic_configuration
======================================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.server_characteristic_configuration

.. autoapi-nested-parse::

   Server Characteristic Configuration Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.server_characteristic_configuration.SCCDData
   src.bluetooth_sig.gatt.descriptors.server_characteristic_configuration.SCCDFlags
   src.bluetooth_sig.gatt.descriptors.server_characteristic_configuration.ServerCharacteristicConfigurationDescriptor


Module Contents
---------------

.. py:class:: SCCDData

   Bases: :py:obj:`msgspec.Struct`


   SCCD (Server Characteristic Configuration Descriptor) data.


   .. py:attribute:: broadcasts_enabled
      :type:  bool


.. py:class:: SCCDFlags

   Bases: :py:obj:`enum.IntFlag`


   SCCD (Server Characteristic Configuration Descriptor) flags.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: BROADCASTS_ENABLED
      :value: 1



.. py:class:: ServerCharacteristicConfigurationDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Server Characteristic Configuration Descriptor (0x2903).

   Controls server-side configuration for a characteristic.
   Currently only supports broadcast enable/disable.

   Initialize descriptor with resolved information.


   .. py:method:: create_disable_broadcasts_value() -> bytes
      :staticmethod:


      Create value to disable broadcasts.



   .. py:method:: create_enable_broadcasts_value() -> bytes
      :staticmethod:


      Create value to enable broadcasts.



   .. py:method:: is_broadcasts_enabled(data: bytes) -> bool

      Check if broadcasts are enabled.




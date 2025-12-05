src.bluetooth_sig.types.device_types
====================================

.. py:module:: src.bluetooth_sig.types.device_types

.. autoapi-nested-parse::

   Device-related data types for BLE device management.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.device_types.ScannedDevice
   src.bluetooth_sig.types.device_types.DeviceService
   src.bluetooth_sig.types.device_types.DeviceEncryption


Module Contents
---------------

.. py:class:: ScannedDevice

   Bases: :py:obj:`msgspec.Struct`


   Minimal wrapper for a device discovered during BLE scanning.

   .. attribute:: address

      Bluetooth MAC address or platform-specific identifier

   .. attribute:: name

      OS-provided device name (may be None)

   .. attribute:: advertisement_data

      Complete parsed advertising data (includes rssi, manufacturer_data, etc.)


   .. py:attribute:: address
      :type:  str


   .. py:attribute:: name
      :type:  str | None
      :value: None



   .. py:attribute:: advertisement_data
      :type:  src.bluetooth_sig.types.advertising.AdvertisingData | None
      :value: None



.. py:class:: DeviceService

   Bases: :py:obj:`msgspec.Struct`


   Represents a service on a device with its characteristics.

   The characteristics dictionary stores BaseCharacteristic instances.
   Access parsed data via characteristic.last_parsed property.

   This provides a single source of truth: BaseCharacteristic instances
   maintain their own last_parsed CharacteristicData.

   .. admonition:: Example

      ```python
      # After discover_services() and read()
      service = device.services["0000180f..."]  # Battery Service
      battery_char = service.characteristics["00002a19..."]  # BatteryLevelCharacteristic instance
      
      # Access last parsed result
      if battery_char.last_parsed:
          print(f"Battery: {battery_char.last_parsed.value}%")
      
      # Or decode new data
      parsed_value = battery_char.decode_value(raw_data)
      ```


   .. py:attribute:: service
      :type:  src.bluetooth_sig.gatt.services.base.BaseGattService


   .. py:attribute:: characteristics
      :type:  dict[str, src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic]


.. py:class:: DeviceEncryption

   Bases: :py:obj:`msgspec.Struct`


   Encryption requirements and status for the device.


   .. py:attribute:: requires_authentication
      :type:  bool
      :value: False



   .. py:attribute:: requires_encryption
      :type:  bool
      :value: False



   .. py:attribute:: encryption_level
      :type:  str
      :value: ''



   .. py:attribute:: security_mode
      :type:  int
      :value: 0



   .. py:attribute:: key_size
      :type:  int
      :value: 0




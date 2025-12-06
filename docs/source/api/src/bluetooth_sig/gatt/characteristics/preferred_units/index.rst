src.bluetooth_sig.gatt.characteristics.preferred_units
======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.preferred_units

.. autoapi-nested-parse::

   Preferred Units characteristic (0x2B46).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.preferred_units.PreferredUnitsCharacteristic
   src.bluetooth_sig.gatt.characteristics.preferred_units.PreferredUnitsData


Module Contents
---------------

.. py:class:: PreferredUnitsCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Preferred Units characteristic (0x2B46).

   org.bluetooth.characteristic.preferred_units

   The Preferred Units characteristic is the list of units the user prefers.
   Each unit is represented by a 16-bit Bluetooth UUID from the Bluetooth SIG units registry.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> PreferredUnitsData

      Decode Preferred Units from raw bytes.

      :param data: Raw bytes from BLE characteristic (variable length, multiples of 2)
      :param ctx: Optional context for parsing

      :returns: Parsed preferred units as Bluetooth UUID objects
      :rtype: PreferredUnitsData

      :raises InsufficientDataError: If data length is not a multiple of 2



   .. py:method:: encode_value(data: PreferredUnitsData) -> bytearray

      Encode Preferred Units to raw bytes.

      :param data: PreferredUnitsData to encode

      :returns: Encoded bytes
      :rtype: bytearray



   .. py:method:: get_units(data: PreferredUnitsData) -> list[src.bluetooth_sig.types.registry.units.UnitInfo]

      Get unit information for the preferred units.

      :param data: PreferredUnitsData containing unit UUIDs

      :returns: List of UnitInfo objects, with placeholder UnitInfo for unrecognized UUIDs



   .. py:method:: validate_units(data: PreferredUnitsData) -> list[str]

      Validate that all units in the data are recognized Bluetooth SIG units.

      :param data: PreferredUnitsData to validate

      :returns: List of validation errors (empty if all units are valid)



.. py:class:: PreferredUnitsData

   Bases: :py:obj:`msgspec.Struct`


   Preferred Units data structure.


   .. py:attribute:: units
      :type:  list[src.bluetooth_sig.types.uuid.BluetoothUUID]



src.bluetooth_sig.gatt.characteristics.bond_management_control_point
====================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.bond_management_control_point

.. autoapi-nested-parse::

   Bond Management Control Point characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.bond_management_control_point.BondManagementCommand
   src.bluetooth_sig.gatt.characteristics.bond_management_control_point.BondManagementControlPointCharacteristic


Module Contents
---------------

.. py:class:: BondManagementCommand

   Bases: :py:obj:`enum.IntEnum`


   Bond Management Control Point commands.


   .. py:attribute:: DELETE_BOND_OF_REQUESTING_DEVICE
      :value: 1



   .. py:attribute:: DELETE_ALL_BONDS_ON_SERVER
      :value: 2



   .. py:attribute:: DELETE_ALL_BUT_ACTIVE_BOND_ON_SERVER
      :value: 3



.. py:class:: BondManagementControlPointCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Bond Management Control Point characteristic (0x2AA4).

   org.bluetooth.characteristic.bond_management_control_point

   Write-only characteristic for sending bond management commands.
   Variable length, starting with command byte.


   .. py:attribute:: min_length
      :value: 1



   .. py:attribute:: allow_variable_length
      :value: True



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> BondManagementCommand

      Decode Bond Management Control Point data from bytes.

      :param data: Raw characteristic data (at least 1 byte)
      :param ctx: Optional characteristic context

      :returns: BondManagementCommand

      :raises ValueError: If data is insufficient or command invalid



   .. py:method:: encode_value(data: BondManagementCommand) -> bytearray

      Encode Bond Management Control Point data to bytes.

      :param data: BondManagementCommand to encode

      :returns: Encoded command (1 byte)




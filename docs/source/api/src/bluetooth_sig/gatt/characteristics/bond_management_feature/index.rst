src.bluetooth_sig.gatt.characteristics.bond_management_feature
==============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.bond_management_feature

.. autoapi-nested-parse::

   Bond Management Feature characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.bond_management_feature.BondManagementFeatureCharacteristic
   src.bluetooth_sig.gatt.characteristics.bond_management_feature.BondManagementFeatureData


Module Contents
---------------

.. py:class:: BondManagementFeatureCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Bond Management Feature characteristic (0x2AA5).

   org.bluetooth.characteristic.bond_management_feature

   Read-only characteristic containing feature flags for bond management operations.
   3 bytes containing boolean flags for supported operations.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> BondManagementFeatureData

      Decode Bond Management Feature data from bytes.

      :param data: Raw characteristic data (3 bytes)
      :param ctx: Optional characteristic context

      :returns: BondManagementFeatureData with feature flags

      :raises ValueError: If data is insufficient



   .. py:method:: encode_value(data: BondManagementFeatureData) -> bytearray

      Encode Bond Management Feature data to bytes.

      :param data: BondManagementFeatureData to encode

      :returns: Encoded feature flags (3 bytes)



   .. py:attribute:: expected_length
      :value: 3



.. py:class:: BondManagementFeatureData

   Bases: :py:obj:`msgspec.Struct`


   Bond Management Feature characteristic data structure.


   .. py:attribute:: delete_all_bonds_on_server_supported
      :type:  bool


   .. py:attribute:: delete_all_but_active_bond_on_server_supported
      :type:  bool


   .. py:attribute:: delete_bond_of_requesting_device_supported
      :type:  bool



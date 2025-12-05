src.bluetooth_sig.gatt.characteristics.magnetic_flux_density_3d
===============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.magnetic_flux_density_3d

.. autoapi-nested-parse::

   Magnetic Flux Density 3D characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.magnetic_flux_density_3d.MagneticFluxDensity3DCharacteristic


Module Contents
---------------

.. py:class:: MagneticFluxDensity3DCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Magnetic Flux Density - 3D characteristic (0x2AA1).

   org.bluetooth.characteristic.magnetic_flux_density_3d

   Magnetic flux density 3D characteristic.

   Represents measurements of magnetic flux density for three
   orthogonal axes: X, Y, and Z. Note that 1 x 10^-7 Tesla equals 0.001
   Gauss.

   Format: 3 x sint16 (6 bytes total) with 1e-7 Tesla resolution.


   .. py:attribute:: resolution
      :type:  float
      :value: 1e-07



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> src.bluetooth_sig.gatt.characteristics.templates.VectorData

      Parse 3D magnetic flux density (3 x sint16 with resolution).

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: VectorData with x, y, z axis values in Tesla.

      # Parameter `ctx` is part of the public API but unused in this implementation.
      # Explicitly delete it to satisfy linters.
      del ctx



   .. py:method:: encode_value(data: src.bluetooth_sig.gatt.characteristics.templates.VectorData) -> bytearray

      Encode 3D magnetic flux density.




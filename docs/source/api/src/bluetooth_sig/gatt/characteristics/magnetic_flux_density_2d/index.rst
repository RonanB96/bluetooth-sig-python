src.bluetooth_sig.gatt.characteristics.magnetic_flux_density_2d
===============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.magnetic_flux_density_2d

.. autoapi-nested-parse::

   Magnetic Flux Density 2D characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.magnetic_flux_density_2d.MagneticFluxDensity2DCharacteristic


Module Contents
---------------

.. py:class:: MagneticFluxDensity2DCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Magnetic Flux Density - 2D characteristic (0x2AA0).

   org.bluetooth.characteristic.magnetic_flux_density_2d

   Magnetic flux density 2D characteristic.

   Represents measurements of magnetic flux density for two orthogonal
   axes: X and Y. Note that 1 x 10^-7 Tesla equals 0.001 Gauss.

   Format: 2 x sint16 (4 bytes total) with 1e-7 Tesla resolution.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> src.bluetooth_sig.gatt.characteristics.templates.Vector2DData

      Parse 2D magnetic flux density (2 x sint16 with resolution).

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: Vector2DData with x and y axis values in Tesla.



   .. py:method:: encode_value(data: src.bluetooth_sig.gatt.characteristics.templates.Vector2DData) -> bytearray

      Encode 2D magnetic flux density.



   .. py:attribute:: resolution
      :type:  float
      :value: 1e-07




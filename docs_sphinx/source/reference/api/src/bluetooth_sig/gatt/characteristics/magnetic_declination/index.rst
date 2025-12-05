src.bluetooth_sig.gatt.characteristics.magnetic_declination
===========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.magnetic_declination

.. autoapi-nested-parse::

   Magnetic Declination characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.magnetic_declination.MagneticDeclinationCharacteristic


Module Contents
---------------

.. py:class:: MagneticDeclinationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Magnetic Declination characteristic (0x2A2C).

   org.bluetooth.characteristic.magnetic_declination

   Magnetic declination characteristic.

   Represents the magnetic declination - the angle on the horizontal plane
   between the direction of True North (geographic) and the direction of
   Magnetic North, measured clockwise from True North to Magnetic North.


   .. py:attribute:: resolution
      :type:  float
      :value: 0.01



   .. py:attribute:: max_value
      :type:  float
      :value: 655.35



   .. py:method:: encode_value(data: float) -> bytearray

      Encode magnetic declination value back to bytes.

      :param data: Magnetic declination in degrees

      :returns: Encoded bytes representing the magnetic declination (uint16, 0.01 degrees resolution)




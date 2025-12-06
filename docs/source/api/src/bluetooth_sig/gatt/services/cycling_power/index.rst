src.bluetooth_sig.gatt.services.cycling_power
=============================================

.. py:module:: src.bluetooth_sig.gatt.services.cycling_power

.. autoapi-nested-parse::

   Cycling Power Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.cycling_power.CyclingPowerService


Module Contents
---------------

.. py:class:: CyclingPowerService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Cycling Power Service implementation (0x1818).

   Used for cycling power meters that measure power output in watts.
   Supports instantaneous power, force/torque vectors, and control
   functions.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]



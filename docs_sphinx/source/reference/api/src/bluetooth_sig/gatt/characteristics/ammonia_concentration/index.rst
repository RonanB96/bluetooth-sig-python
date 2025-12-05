src.bluetooth_sig.gatt.characteristics.ammonia_concentration
============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.ammonia_concentration

.. autoapi-nested-parse::

   Ammonia Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.ammonia_concentration.AmmoniaConcentrationCharacteristic


Module Contents
---------------

.. py:class:: AmmoniaConcentrationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Ammonia concentration measurement characteristic (0x2BCF).

   Uses IEEE 11073 SFLOAT format (medfloat16) as per SIG specification.
   Unit: kg/m³ (kilogram per cubic meter)



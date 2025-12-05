src.bluetooth_sig.gatt.services.weight_scale
============================================

.. py:module:: src.bluetooth_sig.gatt.services.weight_scale

.. autoapi-nested-parse::

   Weight Scale Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.weight_scale.WeightScaleService


Module Contents
---------------

.. py:class:: WeightScaleService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Weight Scale Service implementation (0x181D).

   Used for smart scale devices that measure weight and related body
   metrics. Contains Weight Measurement and Weight Scale Feature
   characteristics.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]



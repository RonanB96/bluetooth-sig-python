src.bluetooth_sig.gatt.services.body_composition
================================================

.. py:module:: src.bluetooth_sig.gatt.services.body_composition

.. autoapi-nested-parse::

   Body Composition Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.body_composition.BodyCompositionService


Module Contents
---------------

.. py:class:: BodyCompositionService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Body Composition Service implementation (0x181B).

   Used for smart scale devices that measure body composition metrics
   including body fat percentage, muscle mass, bone mass, and water
   percentage. Contains Body Composition Measurement and Body
   Composition Feature characteristics.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


